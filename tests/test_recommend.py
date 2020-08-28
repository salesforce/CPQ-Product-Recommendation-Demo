"""
Copyright (c) 2018, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see LICENSE.txt file in the repo root or
https://opensource.org/licenses/BSD-3-Clause
"""
from recommend import get_product_recommendations, get_product_ids_group_by_quote_id
from bulk_operation import QUOTE_OBJECT, PRODUCT_OBJECT


def test_product_never_cooccurring_does_not_get_recommended():
    quote_lines = [dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P01'}),
                   dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P02'}),
                   dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P03'}),
                   dict({QUOTE_OBJECT: 'Q02', PRODUCT_OBJECT: 'P04'}),
                   dict({QUOTE_OBJECT: 'Q02', PRODUCT_OBJECT: 'P05'}),]
    res = get_product_recommendations(quote_lines)
    assert len(res['P01']) == 2
    recommended_ids = [rec[0] for rec in res['P01']]
    assert 'P04' not in recommended_ids
    assert 'P05' not in recommended_ids

    assert len(res['P04']) == 1
    recommended_ids = [rec[0] for rec in res['P04']]
    assert 'P01' not in recommended_ids
    assert 'P02' not in recommended_ids
    assert 'P03' not in recommended_ids


def test_all_products_cooccurring_atleast_once_get_recommended():
    quote_lines = [dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P01'}),
                   dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P02'}),
                   dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P03'}),
                   dict({QUOTE_OBJECT: 'Q02', PRODUCT_OBJECT: 'P04'}),
                   dict({QUOTE_OBJECT: 'Q02', PRODUCT_OBJECT: 'P05'}),]
    res = get_product_recommendations(quote_lines)
    assert len(res['P01']) == 2
    assert 'P02' in res['P01'].keys()
    assert 'P03' in res['P01'].keys()

    assert len(res['P04']) == 1
    assert 'P05' in res['P04'].keys()


def test_product_cooccurring_more_times_has_greater_score():
    quote_lines = [dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P01'}),
                   dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P02'}),
                   dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P03'}),
                   dict({QUOTE_OBJECT: 'Q02', PRODUCT_OBJECT: 'P01'}),
                   dict({QUOTE_OBJECT: 'Q02', PRODUCT_OBJECT: 'P02'}),]
    res = get_product_recommendations(quote_lines)
    assert res['P01']['P02'] > res['P01']['P03']


def test_product_always_cooccurring_has_100_score():
    quote_lines = [dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P01'}),
                   dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P02'}),
                   dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P03'}),
                   dict({QUOTE_OBJECT: 'Q02', PRODUCT_OBJECT: 'P01'}),
                   dict({QUOTE_OBJECT: 'Q02', PRODUCT_OBJECT: 'P02'}),]
    res = get_product_recommendations(quote_lines)
    assert res['P01']['P02'] == 100


def test_get_product_ids_group_by_quote_id_groups_accurately():
    quotelines = [dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P01'}),
                  dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P02'}),
                  dict({QUOTE_OBJECT: 'Q02', PRODUCT_OBJECT: 'P03'})]
    res = get_product_ids_group_by_quote_id(quotelines)
    assert len(res.keys()) == 2
    assert 'Q01' in res.keys() and 'Q02' in res.keys()
    assert len(res['Q01']) == 2 and len(res['Q02']) == 1
    assert 'P01' in res['Q01'] and 'P02' in res['Q01']
    assert 'P03' in res['Q02']


def test_get_product_ids_group_by_quote_id_avoids_duplicates():
    quotelines = [dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P01'}),
                  dict({QUOTE_OBJECT: 'Q01', PRODUCT_OBJECT: 'P01'})]
    res = get_product_ids_group_by_quote_id(quotelines)
    assert len(res.keys()) == 1
    assert 'Q01' in res.keys()
    assert len(res['Q01']) == 1
    assert 'P01' in res['Q01']
