from libcatapult.queues.nats import NatsQueue

from workfinder import S3Api, get_config
from workfinder.search.base_ard_work_finder import BaseArdWorkFinder


class S2ARD(BaseArdWorkFinder):

    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__(s3, nats)

    def get_sensor_name(self):
        return "sentinel_2"

    def get_stac_key(self):
        return get_config("S2_ARD", "STAC_COLLECTION_PATH")
