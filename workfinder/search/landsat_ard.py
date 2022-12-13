from libcatapult.queues.nats import NatsQueue

from workfinder import get_config
from workfinder.api.s3 import S3Api
from workfinder.search.base_ard_work_finder import BaseArdWorkFinder


class Landsat8ARD(BaseArdWorkFinder):

    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_8"

    def get_stac_key(self):
        stac_path = get_config("S3", "STAC_PATH")
        collection_path = get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_8")
        return f"{stac_path}/{collection_path}"


class Landsat7ARD(BaseArdWorkFinder):

    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_7"

    def get_stac_key(self):
        stac_path = get_config("S3", "STAC_PATH")
        collection_path = get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_7")
        return f"{stac_path}/{collection_path}"


class Landsat5ARD(BaseArdWorkFinder):

    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_5"

    def get_stac_key(self):
        stac_path = get_config("S3", "STAC_PATH")
        collection_path = get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_5")
        return f"{stac_path}/{collection_path}"


class Landsat4ARD(BaseArdWorkFinder):

    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_4"

    def get_stac_key(self):
        stac_path = get_config("S3", "STAC_PATH")
        collection_path = get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_4")
        return f"{stac_path}/{collection_path}"
