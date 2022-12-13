import json
import logging
import math

import geopandas as gpd
import numpy
import pandas as pd
from libcatapult.queues.base_queue import BaseQueue
from sentinelsat import SentinelAPI

from workfinder import get_config
from workfinder.api.s3 import S3Api
from workfinder.search import get_aoi_wkt, get_ard_list
from workfinder.search.BaseWorkFinder import BaseWorkFinder


class S1(BaseWorkFinder):

    def __init__(self, s3: S3Api, redis: BaseQueue, esa_api: SentinelAPI):
        super().__init__()
        self._s3 = s3
        self._redis = redis
        self._esa_api = esa_api

    def submit_tasks(self, to_do_list: pd.DataFrame):

        if to_do_list is not None and len(to_do_list) > 0:
            channel = get_config("S1", "REDIS_PROCESSED_CHANNEL")
            # get redis connection
            self._redis.connect()
            # submit each task.
            imagery_path = get_config("S3", "IMAGERY_PATH")
            for index, e in to_do_list.iterrows():
                payload = {
                    "in_scene": e['id'],
                    "s3_bucket": "public-eo-data",
                    "s3_dir": "test/sentinel_1/",
                    "ext_dem": f"{imagery_path}/ancillary_products/SRTM1Sec/SRTM30_Fiji_{e['hemisphere']}.tif"}
                self._redis.publish(channel, json.dumps(payload))

    def find_work_list(self):
        self._s3.get_s3_connection()

        region = get_config("APP", "REGION")
        aoi = get_aoi_wkt(self._s3, region)
        print(self._esa_api.dhus_version)
        res = self._esa_api.query(
            area=aoi,
            platformname='Sentinel-1',
            producttype='GRD',
            sensoroperationalmode='IW'
        )

        esa_grd = self._esa_api.to_geodataframe(res)
        asf_grd_matches = get_s1_asf_urls(esa_grd.title.values)

        df = pd.merge(left=esa_grd, right=asf_grd_matches, how='left', left_on='title', right_on='Granule Name')
        for n, g in zip(aoi.NAME, aoi.geometry):
            df[n] = df.geometry.apply(lambda x: gpd.GeoSeries(x).intersects(g))
        # Filter based on any True intersections
        df[region] = df[df[aoi.NAME.values]].any(1)
        scenes = df[df[region] is True]
        return scenes

    def find_already_done_list(self):
        region = get_config("APP", "REGION")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        return get_ard_list(f"{imagery_path}/{region.lower()}/sentinel_1/")


def get_s1_asf_urls(s1_name_list: pd.Series):
    df = pd.DataFrame()

    num_parts = math.ceil(len(s1_name_list) / 119)
    s1_name_lists = numpy.array_split(numpy.array(s1_name_list), num_parts)
    for entry in s1_name_lists:
        try:
            df = df.append(
                pd.read_csv(
                    f"https://api.daac.asf.alaska.edu/services/search/param?granule_list={','.join(entry)}&output=csv"
                ),
                ignore_index=True
            )
        except Exception as e:
            logging.error(e)

    return df.loc[df['Processing Level'] == 'GRD_HD']
