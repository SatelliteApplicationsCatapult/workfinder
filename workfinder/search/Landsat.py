import json
import logging

import geopandas as gpd
import pandas as pd
from libcatapult.queues.base_queue import BaseQueue

from workfinder import get_config, S3Api
from workfinder.api.espa_api import EspaAPI
from workfinder.search import get_ard_list, get_aoi, download_ancillary_file, download_ancillary_http
from workfinder.search.BaseWorkFinder import BaseWorkFinder


class Landsat8(BaseWorkFinder):

    def __init__(self, s3: S3Api, redis: BaseQueue, espa: EspaAPI):
        super().__init__()
        self._s3 = s3
        self._redis = redis
        self._espa = espa

    def find_work_list(self):
        self._s3.get_s3_connection()

        rows_df = self._get_rows_paths()
        df = _download_metadata()
        logging.info("finding scenes")
        df = df[
            (df['WRS Row'].isin(rows_df['ROW'].values) & df['WRS Path'].isin(rows_df['PATH'].values)) &
            (df['Satellite'] == 8) &
            (df['Landsat Product Identifier L1'].str.contains('L1TP'))
            ]
        logging.info("converting to required objects")
        logging.info(df.columns)
        logging.info(df.head(1))
        df_result = df.apply(_apply_row_mapping, axis=1, result_type='expand')
        return df_result

    def find_already_done_list(self):
        region = get_config("APP", "REGION")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        return get_ard_list(self._s3, f"{imagery_path}/{region.lower()}/landsat_8/")  # TODO: Remove hardcoding

    def submit_tasks(self, to_do_list: pd.DataFrame):
        if to_do_list is not None and len(to_do_list) > 0:
            order_id = self._order_products(to_do_list)

            channel = get_config("LANDSAT8", "REDIS_PENDING_CHANNEL")
            # get redis connection
            self._redis.connect()
            # submit each task.
            self._redis.publish(channel, json.dumps({"order_id": order_id}))
            self._redis.close()

    def _get_rows_paths(self):
        region = get_config("APP", "REGION")  # TODO: this should be a parameter
        aoi = get_aoi(self._s3, region)  # Downloads the world borders file from S3
        file_path = download_ancillary_file(self._s3, "WRS2_descending.geojson",
                                            "SatelliteSceneTiles/landsat_pr/WRS2_descending.geojson")  # Downloads the WRS2_descending.geojson file from S3
        world_granules = gpd.read_file(file_path)
        world_granules[region] = world_granules.geometry.apply(lambda x: x.intersects(aoi))
        region_ls_grans = world_granules[world_granules[region] == True]
        return region_ls_grans

    def _order_products(self, to_do_list: pd.DataFrame):
        order = self._espa.call('available-products', body=dict(inputs=to_do_list['url'].tolist()))

        projection = {
            'aea': {
                'standard_parallel_1': 29.5,
                'standard_parallel_2': 45.5,
                'central_meridian': -96.0,
                'latitude_of_origin': 23.0,
                'false_easting': 0,
                'false_northing': 0,
                'datum': 'nad83'
            }
        }

        order['format'] = 'gtiff'
        order['resampling_method'] = 'cc'
        order['note'] = f"CS_{get_config('APP', 'REGION')}_regular"
        order['projection'] = projection

        # for k, v in order.items():
        #     if "_collection" in k:
        #         if "source_metadata" not in order[k]["products"]:
        #             order[k]["products"] += ["source_metadata"]
        #
        #         if "pixel_qa" not in order[k]["products"]:
        #             order[k]["products"] += ["pixel_qa"]

        logging.info(json.dumps(order))
        # POST https://espa.cr.usgs.gov/api/v1/order
        # example payload
        # "olitirs8_collection_2_l1": {"products": ["l1", "source_metadata", "pixel_qa"], "inputs": ["LC08_L1TP_071017_20140907_20200911_02_T1"]}, "format": "gtiff", "resampling_method": "cc", "note": "CS_Fiji_regular"}
        resp = self._espa.call('order', verb='post', body=order)
        logging.info(f"created order id {resp['orderid']}")
        return resp['orderid']


def _download_metadata():
    logging.info("downloading landsat8 metadata")
    file_path = download_ancillary_http("LANDSAT_OT_C2_L2.csv.gz",
                                        "https://landsat.usgs.gov/landsat/metadata_service/bulk_metadata_files/LANDSAT_OT_C2_L2.csv.gz")
    df = pd.read_csv(file_path)
    logging.info(f"got metadata: {df.size}")
    return df


def _apply_row_mapping(row):
    return {'id': row['Landsat Product Identifier L1'][:25], 'url': row['Landsat Product Identifier L1']}
