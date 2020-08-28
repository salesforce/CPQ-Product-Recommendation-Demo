"""
Copyright (c) 2018, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see LICENSE.txt file in the repo root or
https://opensource.org/licenses/BSD-3-Clause
"""
# pylint: disable=redefined-outer-name
import os
import time
import pytest

from simple_salesforce import Salesforce
from bulk_operation import PRODUCT_ID_FIELD, RECOMMENDED_PRODUCT_ID_FIELD, RECOMMENDATION_OBJECT
from bulk_operation import query_from_db, insert_recommendations_in_db, delete_recommendations_in_db
from bulk_operation import login as bulk_login

sf = Salesforce(username=os.environ['ORG_USERNAME'], password=os.environ['ORG_PASSWORD'],
                security_token=os.environ['ORG_SECURITY_TOKEN'], domain=os.environ['ORG_DOMAIN'])
bulk_login()


@pytest.fixture
def random_str():
    return str(int(round(time.time() * 1000)))


def test_query_from_db_returns_inserted_records(random_str):
    # setup
    record1 = sf.Contact.create({'LastName': 'Smith' + random_str,
                                 'Email': 'smith%s@example.com' % random_str})
    assert record1['success'] is True
    record2 = sf.Contact.create({'LastName': 'Adam' + random_str,
                                 'Email': 'adam%s@example.com' % random_str})
    assert record2['success'] is True

    # test
    rows = query_from_db('Id', object_name='Contact')
    ids = [row['Id'] for row in rows]
    assert record1['id'] in ids
    assert record2['id'] in ids

    # cleanup
    sf.Contact.delete(record1['id'])
    sf.Contact.delete(record2['id'])


def test_delete_recommendations_in_db_deletes_all_recommendations_for_product_ids(random_str):
    # setup
    product1 = sf.Product2.create({'Name': 'P01' + random_str})
    assert product1['success'] is True
    product2 = sf.Product2.create({'Name': 'P02' + random_str})
    assert product2['success'] is True

    product_id_vs_recommended_ids = dict({product1['id']: dict({product2['id']: 50})})
    insert_recommendations_in_db(product_id_vs_recommended_ids)

    delete_recommendations_in_db(product_id_vs_recommended_ids.keys())
    rows = query_from_db('Id', object_name=RECOMMENDATION_OBJECT,
                         where_clause="%s = '%s' and %s = '%s'" %
                         (PRODUCT_ID_FIELD, product1['id'],
                          RECOMMENDED_PRODUCT_ID_FIELD, product2['id']))
    assert len(rows) == 0

    # cleanup
    sf.Product2.delete(product1['id'])
    sf.Product2.delete(product2['id'])


def test_insert_recommendations_in_db_inserts_from_product_dict(random_str):
    # setup
    product1 = sf.Product2.create({'Name': 'P01' + random_str})
    assert product1['success'] is True
    product2 = sf.Product2.create({'Name': 'P02' + random_str})
    assert product2['success'] is True

    product_id_vs_recommended_ids = dict({product1['id']: dict({product2['id']: 50})})
    delete_recommendations_in_db(product_id_vs_recommended_ids.keys())

    insert_recommendations_in_db(product_id_vs_recommended_ids)
    rows = query_from_db('Id', object_name=RECOMMENDATION_OBJECT,
                         where_clause="%s = '%s' and %s = '%s'" %
                         (PRODUCT_ID_FIELD, product1['id'],
                          RECOMMENDED_PRODUCT_ID_FIELD, product2['id']))
    assert len(rows) == 1

    # cleanup
    sf.Product2.delete(product1['id'])
    sf.Product2.delete(product2['id'])
