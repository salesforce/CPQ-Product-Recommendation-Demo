"""
Copyright (c) 2018, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see LICENSE.txt file in the repo root or
https://opensource.org/licenses/BSD-3-Clause

This module generates the product recommendations along with a percentage score
for each.
"""
from itertools import combinations
import pandas as pd
import numpy as np

import bulk_operation

SCORE_THRESHOLD = 0


def get_product_recommendations(quote_lines):
    """
    Uses item-item co-occurrence matrix to find recommendations.

    Each recommendation is scored as a percentage from 1 to 100.
    Eg. if all quotes containing product A, also has product B
    then, among the recommendations for A:
    B gets a recommendation score of 100, as B occurs in 100% of the quotes containing A
    """
    quote_id_vs_product_ids = get_product_ids_group_by_quote_id(quote_lines)

    pairs = []
    product_id_vs_quote_count = dict()
    for product_ids in quote_id_vs_product_ids.values():
        for product_id in product_ids:
            if product_id not in product_id_vs_quote_count:
                product_id_vs_quote_count[product_id] = 0
            product_id_vs_quote_count[product_id] += 1
        pairs.extend(list(combinations(product_ids, 2)))

    distinct_product_ids = product_id_vs_quote_count.keys()
    coocc = pd.DataFrame(index=distinct_product_ids, columns=distinct_product_ids)
    coocc = coocc.fillna(0)

    res = {}
    for pair in pairs:
        product_id_1 = pair[0]
        product_id_2 = pair[1]
        coocc[product_id_1][product_id_2] += 1
        coocc[product_id_2][product_id_1] += 1

    coocc = coocc.div(pd.Series(product_id_vs_quote_count), axis=1)
    coocc = (coocc*100).apply(np.ceil).astype(int)

    for product_id in distinct_product_ids:
        if product_id not in res:
            res[product_id] = dict()
        for recommended_id, score in coocc[product_id].items():
            if score > SCORE_THRESHOLD:
                res[product_id][recommended_id] = score
    return res


def get_product_ids_group_by_quote_id(quote_lines):
    res = {}
    for quote_line in quote_lines:
        quote_id = quote_line[bulk_operation.QUOTE_OBJECT]
        product_id = quote_line[bulk_operation.PRODUCT_OBJECT]
        if quote_id not in res:
            res[quote_id] = set()
        res[quote_id].add(product_id)
    return res
