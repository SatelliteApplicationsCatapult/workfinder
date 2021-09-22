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
        df = df[df['WRS Path'].isin(rows_df['ROW'].values) & df['WRS Path'].isin(rows_df['PATH'].values)]
        logging.info("converting to required objects")
        logging.info(df.columns)
        logging.info(df.head(1))
        df_result = df.apply(_apply_row_mapping, axis=1, result_type='expand')
        return df_result

    def find_already_done_list(self):
        region = get_config("app", "region")
        return get_ard_list(self._s3, f"common_sensing/{region.lower()}/landsat_8/")

    def submit_tasks(self, to_do_list: pd.DataFrame):
        if to_do_list is not None and len(to_do_list) > 0:

            order_id = self._order_products(to_do_list)

            channel = get_config("landsat8", "redis_pending_channel")
            # get redis connection
            self._redis.connect()
            # submit each task.
            self._redis.publish(channel, json.dumps({"order_id": order_id}))
            self._redis.close()

    def _get_rows_paths(self):
        region = get_config("app", "region")
        aoi = get_aoi(self._s3, region)
        file_path = download_ancillary_file(self._s3, "WRS2_descending.geojson",
                                            "SatelliteSceneTiles/landsat_pr/WRS2_descending.geojson")
        world_granules = gpd.read_file(file_path)
        # Create bool for intersection between any tiles - should try inversion to speed up...
        world_granules[region] = world_granules.geometry.apply(lambda x: gpd.GeoSeries(x).intersects(aoi))
        # Filter based on any True intersections
        world_granules[region] = world_granules[world_granules[region]].any(1)
        # NOTE: this line will show a warning in pycharm that the == should be is however for the pandas magic to work
        # it must be ==
        region_ls_grans = world_granules[world_granules[region] == True]
        return region_ls_grans

    def _order_products(self, to_do_list: pd.DataFrame):
        order = self._espa.call('available-products', body=dict(inputs=to_do_list['url'].tolist()))
        order['format'] = 'gtiff'
        order['resampling_method'] = 'cc'
        order['note'] = f"CS_{get_config('app', 'region')}_regular"

        for k, v in order.items():
            if "_collection" in k:
                if "source_metadata" not in order[k]["products"]:
                    order[k]["products"] += ["source_metadata"]

                if "pixel_qa" not in order[k]["products"]:
                    order[k]["products"] += ["pixel_qa"]

        logging.info(json.dumps(order))

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
    # logging.info(row)
    return {'id': row['Landsat Product Identifier L1'][:25], 'url': row['Landsat Product Identifier L1']}
