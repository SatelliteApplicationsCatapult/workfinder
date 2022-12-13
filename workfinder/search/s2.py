import json

import geopandas as gpd
import pandas as pd
from libcatapult.queues.base_queue import BaseQueue
from sentinelsat import SentinelAPI

from workfinder import get_config, S3Api
from workfinder.search import get_gpd_file, get_ard_list, get_aoi
from workfinder.search.BaseWorkFinder import BaseWorkFinder


class S2(BaseWorkFinder):

    def __init__(self, s3: S3Api, redis: BaseQueue, esa_api: SentinelAPI):
        super().__init__()
        self._s3 = s3
        self._redis = redis
        self._esa_api = esa_api

    def find_work_list(self):
        self._s3.get_s3_connection()

        region = get_config("APP", "REGION")
        aoi = get_aoi(self._s3, region)
        print(self._esa_api.dhus_version)

        world_granules = get_gpd_file(self._s3,
                                      "sentinel2_tiles_world.geojson",
                                      "SatelliteSceneTiles/sentinel2_tiles_world/sentinel2_tiles_world.geojson")
        # Create bool for intersection between any tiles - should try inversion to speed up...
        world_granules[region] = world_granules.geometry.apply(lambda x: gpd.GeoSeries(x).intersects(aoi))
        # Filter based on any True intersections
        world_granules[region] = world_granules[world_granules[region]].any(1)
        region_s2_grans = world_granules[world_granules[region] == True]

        res = self._esa_api.query(
            area=aoi,
            platformname='Sentinel-2',
            producttype='S2MSI1C',
        )
        esa_l2a = self._esa_api.to_geodataframe(res)

        res = self._esa_api.query(
            area=aoi,
            platformname='Sentinel-2',
            producttype='S2MSI1C'
        )
        esa_l1c = self._esa_api.to_geodataframe(res)

        esa_l1c['scenename'] = esa_l1c.title.apply(
            lambda x: f"{x.split('_')[0]}_{x.split('_')[1]}_{x.split('_')[2]}_{x.split('_')[5]}")
        esa_l2a['scenename'] = esa_l2a.title.apply(
            lambda x: f"{x.split('_')[0]}_MSIL1C_{x.split('_')[2]}_{x.split('_')[5]}")
        esa_l1c['granules'] = esa_l1c.identifier.str[39:44]
        esa_l2a['granules'] = esa_l2a.identifier.str[39:44]

        esa_l1c_srt = esa_l1c.sort_values('beginposition', ascending=False)
        esa_l2a_srt = esa_l2a.sort_values('beginposition', ascending=False)
        esa_l1c_srt = esa_l1c_srt.loc[~esa_l1c_srt['scenename'].isin(esa_l2a_srt.scenename.values)]

        esa_l1c_precise = esa_l1c_srt[esa_l1c_srt['granules'].isin(region_s2_grans.Name.values)]
        esa_l2a_precise = esa_l2a_srt[esa_l2a_srt['granules'].isin(region_s2_grans.Name.values)]

        result = pd.concat([esa_l1c_precise['scenename'], esa_l2a_precise['scenename']], axis=0)
        df_result = result.apply(_row_mapping, axis=1, result_type='expand')
        return df_result

    def find_already_done_list(self):
        region = get_config("APP", "REGION")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        return get_ard_list(self._s3, f"{imagery_path}/{region.lower()}/sentinel_2/")

    def submit_tasks(self, to_do_list: pd.DataFrame):
        region = get_config("APP", "REGION")
        target_bucket = get_config("S3", "BUCKET")
        target_queue = get_config("S2", "REDIS_PROCESSED_CHANNEL")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        for r in to_do_list.tolist():
            payload = {
                "in_scene": r['url'],
                "s3_bucket": target_bucket,
                "s3_dir": f"{imagery_path}/{region.lower()}/sentinel_2/"
            }
            self._redis.publish(target_queue, json.dumps(payload))


def _row_mapping(row):
    return {'id': row['scenename'], 'url': row['scenename']}
