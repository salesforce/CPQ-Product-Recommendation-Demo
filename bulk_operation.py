"""
Copyright (c) 2018, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see LICENSE.txt file in the repo root or
https://opensource.org/licenses/BSD-3-Clause

This module authenticates with the bulk api service and uses the bulk api
to read QuoteLine__c data and insert custom product recommendation objects.
"""
import os
import json
import time
import logging

from salesforce_bulk.util import IteratorBytesIO
from salesforce_bulk import SalesforceBulk
from salesforce_bulk import CsvDictsAdapter

import recommend

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

RECOMMENDATION_OBJECT = 'ProductRecommendation__c'
PRODUCT_ID_FIELD = 'Product2Id__c'
RECOMMENDED_PRODUCT_ID_FIELD = 'RecommendedProduct2Id__c'
SCORE_FIELD = 'Score__c'

PRODUCT_OBJECT = 'SBQQ__Product__c'
QUOTE_OBJECT = 'SBQQ__Quote__c'
QUOTELINE_OBJECT = 'SBQQ__QuoteLine__c'

bulk = None


def get_recommendation_record(product_id, recommended_id, score):
    return dict({PRODUCT_ID_FIELD: product_id,
                 RECOMMENDED_PRODUCT_ID_FIELD: recommended_id,
                 SCORE_FIELD: score})


def query_from_db(*fields, object_name=None, where_clause=None):
    if object_name is None:
        raise ValueError('object_name is not provided.')
    job = bulk.create_query_job(object_name, contentType='JSON')
    query = 'select ' + ', '.join(fields) + ' from ' + object_name
    if where_clause is not None:
        query += ' where ' + where_clause
    logging.info(query)
    batch = bulk.query(job, query)
    bulk.close_job(job)
    try:
        while not bulk.is_batch_done(batch):
            logging.info('batch status: %s', bulk.batch_status(batch_id=batch)['state'])
            time.sleep(10)
    finally:
        if not bulk.is_batch_done(batch):
            bulk.abort_job(job)
            logging.info('aborted job')

    records = []
    for result in bulk.get_all_results_for_query_batch(batch):
        result = json.load(IteratorBytesIO(result))
        for row in result:
            records.append(row)
    return records


def get_all_quotes_from_db():
    return query_from_db(PRODUCT_OBJECT, QUOTE_OBJECT, object_name=QUOTELINE_OBJECT)


def insert_recommendations_in_db(product_id_vs_recommended_ids):
    if len(product_id_vs_recommended_ids) == 0:
        return
    job = bulk.create_insert_job(RECOMMENDATION_OBJECT, contentType='CSV',
                                 concurrency='Parallel')
    recommendations = []
    for product_id in product_id_vs_recommended_ids:
        recommended_id_vs_scores = product_id_vs_recommended_ids[product_id]
        for recommended_id, score in recommended_id_vs_scores.items():
            recommendations.append(get_recommendation_record(product_id, recommended_id, score))

    if not recommendations:
        return
    csv_iter_recommendations = CsvDictsAdapter(iter(recommendations))
    batch_insert_recommendations = bulk.post_batch(job, csv_iter_recommendations)
    bulk.wait_for_batch(job, batch_insert_recommendations)
    bulk.close_job(job)
    logging.info("Done. Recommendations uploaded.")


def delete_recommendations_in_db(product_ids):
    """delete all recommendation object records for product_ids"""
    if not product_ids:
        return
    where_clause = '{0} IN ({1})'.format(PRODUCT_ID_FIELD,
                                         ', '.join("'{0}'".format(w) for w in product_ids))
    recommendation_object_ids = query_from_db('Id',
                                              object_name=RECOMMENDATION_OBJECT,
                                              where_clause=where_clause)
    ids = [{'Id': row['Id']} for row in recommendation_object_ids]
    if not ids:
        logging.info("Done. No Recommendations to delete.")
        return
    job = bulk.create_delete_job(RECOMMENDATION_OBJECT,
                                 contentType='CSV',
                                 concurrency='Parallel')
    csv_iter_recommendations = CsvDictsAdapter(iter(ids))
    batch_delete_recommendations = bulk.post_batch(job, csv_iter_recommendations)
    bulk.wait_for_batch(job, batch_delete_recommendations)
    bulk.close_job(job)
    logging.info("Done. Recommendations deleted.")


def login():
    global bulk
    logging.info('logging in...')
    # domain passed to SalesforceBulk should be 'test' or 'login' or 'something.my'
    bulk = SalesforceBulk(username=os.environ['ORG_USERNAME'], password=os.environ['ORG_PASSWORD'],
                          security_token=os.environ['ORG_SECURITY_TOKEN'], domain=os.environ['ORG_DOMAIN'])
    logging.info('login successful !')


def run():
    login()
    quote_lines = get_all_quotes_from_db()
    if not quote_lines:
        return
    product_id_vs_recommended_ids = recommend.get_product_recommendations(quote_lines)
    if len(product_id_vs_recommended_ids) != 0:
        delete_recommendations_in_db(product_id_vs_recommended_ids.keys())
        insert_recommendations_in_db(product_id_vs_recommended_ids)


if __name__ == '__main__':
    run()
