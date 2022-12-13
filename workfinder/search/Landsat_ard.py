import logging

import pandas as pd
from libcatapult.queues.nats import NatsQueue

from workfinder import get_config
from workfinder.api.s3 import S3Api
from workfinder.search import list_catalog, get_ard_list
from workfinder.search.BaseWorkFinder import BaseWorkFinder


class LandsatARD(BaseWorkFinder):

    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__()
        self.s3 = s3
        self.nats = nats

    def submit_tasks(self, to_do_list: pd.DataFrame):
        # get nats connection
        channel = get_config("LANDSAT_ARD", "NATS_CHANNEL")
        self.nats.connect()
        for index, r in to_do_list.iterrows():
            logging.info(f"publishing {r['url']}")
            self.nats.publish(channel, r['url'])
        try:
            self.nats.close()
        except:
            pass

    def find_work_list(self):
        self.s3.get_s3_connection()
        region = get_config("APP", "REGION")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        return get_ard_list(self.s3, f"{imagery_path}/{region.lower()}/landsat_8/")

    def find_already_done_list(self):
        self.s3.get_s3_connection()
        stac_key = get_config("LANDSAT_ARD", "STAC_COLLECTION_PATH")
        path_sizes = list_catalog(self.s3, stac_key)
        # map filenames to ids
        df_result = pd.DataFrame({'id': []})
        for r in path_sizes:
            df_result = df_result.append({'id': r}, ignore_index=True)
        return df_result
