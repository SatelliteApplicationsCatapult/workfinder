import logging
from abc import abstractmethod

import pandas as pd


class NoWorkException(Exception):
    pass


class BaseWorkFinder:
    def __init__(self):
        pass

    def find_new_work(self):
        possible = self.find_work_list()
        done = self.find_already_done_list()

        if possible is None or possible.empty:
            raise NoWorkException

        df_possible = _to_pandas(possible)
        df_done = pd.DataFrame({'id': []})
        if done is not None and not done.empty:
            df_done = _to_pandas(done)

        return _diff_work_lists(df_possible, df_done)

    @abstractmethod
    def find_work_list(self):
        """
        find_work_list returns a list of potential work packages.
        it returns a list of dictionaries with identifier and url fields.
        """
        pass

    @abstractmethod
    def find_already_done_list(self):
        """
        find_already_done_list returns a list of work already done. This should be a list of identifiers in the same
        format as the find_work_list. This will be matched to
        """
        pass

    @abstractmethod
    def submit_tasks(self, to_do_list: pd.DataFrame):
        """
        submit_tasks will send the list of work to where it is needed for this tasking.
        """
        pass


def _diff_work_lists(possible: pd.DataFrame, done: pd.DataFrame):
    df_result = pd.DataFrame({'id': [], 'url': []})

    logging.info(f"Checking {len(possible.index)} things against {len(done.index)} already done things.")

    # This is about the worst possible way to do this.
    # (ok it could be worse)
    # but there should be a better way to do this

    df_result = possible[~possible['id'].isin(done['id'])].dropna(how='all')

    logging.info(f"found {len(df_result.index)} things to do.")
    logging.info(df_result)
    return df_result


def _to_pandas(input):
    """
    _to_pandas will make sure the input array is a pandas dataframe. if it is not something that can be converted it
    will raise an error.
    """
    # TODO: implement this when needed
    return input
