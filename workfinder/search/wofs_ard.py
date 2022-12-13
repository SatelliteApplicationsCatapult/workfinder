from libcatapult.queues.nats import NatsQueue

from workfinder import get_config, S3Api
from workfinder.search.base_ard_work_finder import BaseArdWorkFinder


class Landsat8WofsArd(BaseArdWorkFinder):
    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_8_wofs"

    def get_stac_key(self):
        return get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_8_WOFS")


class Landsat7WofsArd(BaseArdWorkFinder):
    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_7_wofs"

    def get_stac_key(self):
        return get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_7_WOFS")


class Landsat5WofsArd(BaseArdWorkFinder):
    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_5_wofs"

    def get_stac_key(self):
        return get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_5_WOFS")


class Sentinel2WofsArd(BaseArdWorkFinder):
    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "sentinel_2_wofs"

    def get_stac_key(self):
        return get_config("S2_ARD", "STAC_COLLECTION_PATH_WOFS")
