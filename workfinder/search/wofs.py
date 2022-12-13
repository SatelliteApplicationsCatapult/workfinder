import json
from abc import abstractmethod

import pandas as pd
from libcatapult.queues.base_queue import BaseQueue

from workfinder import get_config, S3Api
from workfinder.search import get_ard_list
from workfinder.search.BaseWorkFinder import BaseWorkFinder


class BaseWofs(BaseWorkFinder):

    def __init__(self, s3: S3Api, redis: BaseQueue):
        self._s3 = s3
        self._redis = redis
        super().__init__()

    @abstractmethod
    def get_source_sensor_name(self):
        """
        get_source_sensor_name returns the name in the s3 bucket that contains all the ard data.
        """

    @abstractmethod
    def get_target_name(self):
        """
        get_target_name returns the name in the s3 bucket that contains all the expected result data.
        """

    def find_work_list(self):
        self._s3.get_s3_connection()
        region = get_config("APP", "REGION")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        return get_ard_list(self._s3, f"{imagery_path}/{region.lower()}/{self.get_source_sensor_name()}/")

    def find_already_done_list(self):
        self._s3.get_s3_connection()
        region = get_config("APP", "REGION")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        return get_ard_list(self._s3, f"{imagery_path}/{region.lower()}/{self.get_target_name()}/")

    def submit_tasks(self, to_do_list: pd.DataFrame):
        region = get_config("APP", "REGION")
        target_bucket = get_config("S3", "BUCKET")
        target_queue = get_config("S2", "REDIS_PROCESSED_CHANNEL")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        for r in to_do_list.tolist():
            payload = {
                "optical_yaml_path": r['url'],
                "s3_bucket": target_bucket,
                "s3_dir": f"{imagery_path}/{region.lower()}/{self.get_target_name()}/"
            }
            self._redis.publish(target_queue, json.dumps(payload))


class Landsat8Wofs(BaseWofs):
    def get_source_sensor_name(self):
        return "landsat_8"

    def get_target_name(self):
        return "landsat_8_wofs"


class Landsat7Wofs(BaseWofs):
    def get_source_sensor_name(self):
        return "landsat_7"

    def get_target_name(self):
        return "landsat_7_wofs"


class Landsat5Wofs(BaseWofs):
    def get_source_sensor_name(self):
        return "landsat_5"

    def get_target_name(self):
        return "landsat_5_wofs"


class Landsat4Wofs(BaseWofs):
    def get_source_sensor_name(self):
        return "landsat_4"

    def get_target_name(self):
        return "landsat_4_wofs"


class Sentinel2Wofs(BaseWofs):
    def get_source_sensor_name(self):
        return "sentinel_2"

    def get_target_name(self):
        return "sentinel_2_wofs"
