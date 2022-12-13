"""Main module."""
import logging

import click
import pandas

from workfinder import default_s3_api, default_nats_api, default_redis_api, default_esa_api, \
    default_espa_api
from workfinder.search.Landsat import Landsat8
from workfinder.search.landsat_ard import Landsat8ARD, Landsat4ARD, Landsat5ARD, Landsat7ARD
from workfinder.search.ml_water import Landsat8MLWater, Landsat7MLWater, Landsat5MLWater, S2MLWater, S1MLWater
from workfinder.search.mlwater_ard import Landsat8MlWaterArd, Landsat7MlWaterArd, \
    Landsat5MlWaterArd, Sentinel1MlWaterArd, Sentinel2MlWaterArd
from workfinder.search.s1 import S1
from workfinder.search.s1_ard import S1ARD
from workfinder.search.s2 import S2
from workfinder.search.s2_ard import S2ARD
from workfinder.search.wofs import Landsat8Wofs, Landsat7Wofs, Landsat5Wofs, Landsat4Wofs
from workfinder.search.wofs_ard import Landsat8WofsArd, Landsat7WofsArd, Landsat5WofsArd, Sentinel2WofsArd

# Mapping of processor names to objects.
# Note: Names must be upper case.
processors = {
    "S1": S1(default_s3_api(), default_redis_api(), default_esa_api()),
    "S1_ARD": S1ARD(default_s3_api(), default_nats_api()),
    "S2": S2(default_s3_api(), default_redis_api(), default_esa_api()),
    "S2_ARD": S2ARD(default_s3_api(), default_nats_api()),
    "LANDSAT8": Landsat8(default_s3_api(), default_redis_api(), default_espa_api()),
    "LANDSAT8_ARD": Landsat8ARD(default_s3_api(), default_nats_api()),
    "LANDSAT7_ARD": Landsat7ARD(default_s3_api(), default_nats_api()),
    "LANDSAT5_ARD": Landsat5ARD(default_s3_api(), default_nats_api()),
    "LANDSAT4_ARD": Landsat4ARD(default_s3_api(), default_nats_api()),
    "LANDSAT8_MLWATER": Landsat8MLWater(default_s3_api(), default_redis_api()),
    "LANDSAT7_MLWATER": Landsat7MLWater(default_s3_api(), default_redis_api()),
    "LANDSAT5_MLWATER": Landsat5MLWater(default_s3_api(), default_redis_api()),
    "S2_MLWATER": S2MLWater(default_s3_api(), default_redis_api()),
    "S1_MLWATER": S1MLWater(default_s3_api(), default_redis_api()),
    "LANDSAT8_MLWATER_ARD": Landsat8MlWaterArd(default_s3_api(), default_nats_api()),
    "LANDSAT7_MLWATER_ARD": Landsat7MlWaterArd(default_s3_api(), default_nats_api()),
    "LANDSAT5_MLWATER_ARD": Landsat5MlWaterArd(default_s3_api(), default_nats_api()),
    "S2_MLWATER_ARD": Sentinel2MlWaterArd(default_s3_api(), default_nats_api()),
    "S1_MLWATER_ARD": Sentinel1MlWaterArd(default_s3_api(), default_nats_api()),
    "LANDSAT8_WOFS": Landsat8Wofs(default_s3_api(), default_redis_api()),
    "LANDSAT7_WOFS": Landsat7Wofs(default_s3_api(), default_redis_api()),
    "LANDSAT5_WOFS": Landsat5Wofs(default_s3_api(), default_redis_api()),
    "LANDSAT4_WOFS": Landsat4Wofs(default_s3_api(), default_redis_api()),
    "LANDSAT8_WOFS_ARD": Landsat8WofsArd(default_s3_api(), default_nats_api()),
    "LANDSAT7_WOFS_ARD": Landsat7WofsArd(default_s3_api(), default_nats_api()),
    "LANDSAT5_WOFS_ARD": Landsat5WofsArd(default_s3_api(), default_nats_api()),
    "S2_WOFS_ARD": Sentinel2WofsArd(default_s3_api(), default_nats_api()),

}


@click.command()
@click.option('--limit', default=-1, help='Number records to process', )
@click.argument("process")
def main(process, limit):
    param = process.upper()
    if param in processors:
        logging.info(f"starting work search for {param}")
        work: pandas.core.frame.DataFrame = processors[param].find_new_work()
        if limit == -1:
            limit = 5000
        if limit > work.shape[0]:
            limit = work.shape[0]
        if limit > 5000:
            limit = 5000
        logging.info(f"Processing limit is set to {limit}")
        reduced_pandas_frame = work.iloc[0:limit]
        processors[param].submit_tasks(reduced_pandas_frame)
        logging.info(f"done work search for {param}")
    else:
        logging.error(f"unknown processor type {param}")


if __name__ == '__main__':
    main()
