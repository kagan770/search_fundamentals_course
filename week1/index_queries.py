# From Dmitiriy Shvadskiy https://github.com/dshvadskiy/search_with_machine_learning_course/blob/main/index_queries.py
import logging
import time

import click
import pandas as pd
from opensearchpy.helpers import bulk

from opensearch_client import get_opensearch

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s')


@click.command()
@click.option('--source_file', '-s', help='source csv file', required=True)
@click.option('--index_name', '-i', default="bbuy_queries", help="The name of the index to write to")
def main(source_file: str, index_name: str):
    client = get_opensearch()
    ds = pd.read_csv(source_file, keep_default_na=False)
    #print(ds.columns)
    ds['click_time'] = custom_parser(ds['click_time'])
    ds['query_time'] = custom_parser(ds['query_time'])
    #print(ds.dtypes)
    docs = []
    tic = time.perf_counter()
    for idx, row in ds.iterrows():
        doc = {}
        for col in ds.columns:
            doc[col] = row[col]
            if col == "click_time" or col == "query_time":
                doc[col] = row[col][:19] # bluntly removing the millis for now,
                # I tripped with errors although had the proper mapping for handling it
        docs.append({'_index': index_name , '_source': doc})
        if idx % 1000 == 0:
            bulk(client, docs, request_timeout=180)
            logger.info(f'{idx} documents indexed')
            docs = []
    if len(docs) > 0:
        bulk(client, docs, request_timeout=180)
    toc = time.perf_counter()
    logger.info(f'Done indexing {ds.shape[0]} records. Total time: {((toc-tic)/60):0.3f} mins.')


def custom_parser(x):
    try:
        return pd.to_datetime(x, format="%Y-%m-%d %H:%M:%S.%f", errors='raise')
    except ValueError:
        return pd.to_datetime(x, format="%Y-%m-%d %H:%M:%S", errors='ignore')


if __name__ == "__main__":
    main()