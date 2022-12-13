import abc
import json
import logging
import sys

from libcatapult.queues.base_queue import BaseQueue


class BaseWaiter(object):

    def __init__(self, q: BaseQueue):
        self.q = q

    @abc.abstractmethod
    def check_order(self, order_id: str):
        pass

    @abc.abstractmethod
    def send_complete_order(self, order_details: dict):
        pass

    @abc.abstractmethod
    def get_redis_source_queue(self):
        pass

    def process(self):
        self.q.connect()
        queue_name = self.get_redis_source_queue()
        to_check = []
        while not self.q.empty(queue_name):
            item = self.q.receive(queue_name, timeout=600)
            to_check.append(item)
        logging.info(f"got {len(to_check)} entries to check on.")
        errored = False
        for item in to_check:
            try:
                payload = json.loads(item)
                logging.info(f"checking on {item}")
                if self.check_order(payload['order_id']):
                    logging.info(f"{payload['order_id']} completed!")
                    self.send_complete_order(payload)
                else:
                    logging.info(f"{payload['order_id']} still pending")
                    self.q.publish(queue_name, item)
            except Exception as e:
                logging.info(f"Could not process {item}, {e}, putting back in queue")
                self.q.publish(queue_name, item)
                errored = True
        if errored:
            sys.exit("there was an error")
