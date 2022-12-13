import logging
from abc import abstractmethod

import pandas as pd
from libcatapult.queues.nats import NatsQueue

from workfinder import get_config, S3Api
from workfinder.search import get_ard_list, list_catalog
from workfinder.search.BaseWorkFinder import BaseWorkFinder


class BaseArdWorkFinder(BaseWorkFinder):

    def __init__(self, s3: S3Api, nats: NatsQueue):
        super().__init__()
        self.s3 = s3
        self.nats = nats

    @abstractmethod
    def get_sensor_name(self):
        """
        get_sensor_name returns the name in the s3 bucket that contains all the ard data.
        """

    @abstractmethod
    def get_stac_key(self):
        """
        get_stac_key returns the name of the stac key that contains the already processed information
        """

    def submit_tasks(self, to_do_list: pd.DataFrame):
        # get nats connection
        item_channel = get_config("NATS", "item_nats_channel")
        collection_channel = get_config("NATS", "collection_nats_channel")
        stac_key = self.get_stac_key()

        self.nats.connect()
        self.nats.publish(collection_channel, stac_key)

        for index, r in to_do_list.iterrows():
            path = '/'.join(r['url'].split('/')[0:-1]) + '/'
            logging.info(f"publishing {r['url']} as {path}")
            self.nats.publish(item_channel, path)

        try:
            self.nats.close()
        except:
            pass

    def find_work_list(self):
        self.s3.get_s3_connection()
        region = get_config("APP", "REGION")
        imagery_path = get_config("S3", "IMAGERY_PATH")
        return get_ard_list(self.s3, f"{imagery_path}/{region.lower()}/{self.get_sensor_name()}/")

    def find_already_done_list(self):
        self.s3.get_s3_connection()
        path_sizes = list_catalog(self.s3, self.get_stac_key())
        # map filenames to ids
        df_result = pd.DataFrame({'id': []})
        for r in path_sizes:
            df_result = df_result.append({'id': r}, ignore_index=True)
        return df_result
