import json
from abc import abstractmethod

import pandas as pd
from libcatapult.queues.base_queue import BaseQueue

from workfinder import S3Api, get_config
from workfinder.search.wofs import BaseWofs


class BaseMLWater(BaseWofs):

    @abstractmethod
    def get_source_sensor_name(self):
        pass

    @abstractmethod
    def get_target_name(self):
        pass

    def __init__(self, s3: S3Api, redis: BaseQueue):
        super().__init__(s3, redis)

    def submit_tasks(self, to_do_list: pd.DataFrame):
        region = get_config("APP", "REGION")
        target_bucket = get_config("S3", "BUCKET")
        target_queue = get_config("ML_WATER", "REDIS_PROCESSED_CHANNEL")
        wofs_summary = get_config("ML_WATER", "WOFS_SUMMARY_PATH")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        for r in to_do_list.tolist():
            payload = {
                "img_yml_path": r['url'],
                "lab_yml_path": wofs_summary,
                "s3_bucket": target_bucket,
                "s3_dir": f"{imagery_path}/{region.lower()}/{self.get_target_name()}/"
            }
            self._redis.publish(target_queue, json.dumps(payload))


class Landsat8MLWater(BaseMLWater):

    def get_source_sensor_name(self):
        return "landsat_8"

    def get_target_name(self):
        return "landsat_8_mlwater"


class Landsat7MLWater(BaseMLWater):
    def get_source_sensor_name(self):
        return "landsat_7"

    def get_target_name(self):
        return "landsat_7_mlwater"


class Landsat5MLWater(BaseMLWater):
    def get_source_sensor_name(self):
        return "landsat_5"

    def get_target_name(self):
        return "landsat_5_mlwater"


class S2MLWater(BaseMLWater):
    def get_source_sensor_name(self):
        return "sentinel_2"

    def get_target_name(self):
        return "sentinel_2_mlwater"


class S1MLWater(BaseMLWater):
    def get_source_sensor_name(self):
        return "sentinel_1"

    def get_target_name(self):
        return "sentinel_1_mlwater"
