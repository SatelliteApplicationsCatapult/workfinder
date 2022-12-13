from libcatapult.queues.nats import NatsQueue

from workfinder import get_config, S3Api
from workfinder.search.base_ard_work_finder import BaseArdWorkFinder


class Landsat8MlWaterArd(BaseArdWorkFinder):
    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_8_mlwater"

    def get_stac_key(self):
        stac_path = get_config("S3", "STAC_PATH")
        collection_path = get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_8_MLWATER")
        return f"{stac_path}/{collection_path}"


class Landsat7MlWaterArd(BaseArdWorkFinder):
    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_7_mlwater"

    def get_stac_key(self):
        stac_path = get_config("S3", "STAC_PATH")
        collection_path = get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_7_MLWATER")
        return f"{stac_path}/{collection_path}"


class Landsat5MlWaterArd(BaseArdWorkFinder):
    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "landsat_5_mlwater"

    def get_stac_key(self):
        stac_path = get_config("S3", "STAC_PATH")
        collection_path = get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH_5_MLWATER")
        return f"{stac_path}/{collection_path}"


class Sentinel2MlWaterArd(BaseArdWorkFinder):
    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "sentinel_2_mlwater"

    def get_stac_key(self):
        stac_path = get_config("S3", "STAC_PATH")
        collection_path = get_config("S2_ARD", "STAC_COLLECTION_PATH_MLWATER")
        return f"{stac_path}/{collection_path}"


class Sentinel1MlWaterArd(BaseArdWorkFinder):
    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "sentinel_1_mlwater"

    def get_stac_key(self):
        stac_path = get_config("S3", "STAC_PATH")
        collection_path = get_config("S1_ARD", "STAC_COLLECTION_PATH_MLWATER")
        return f"{stac_path}/{collection_path}"
