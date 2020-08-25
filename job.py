#!/usr/bin/env python3 -u

"""
This script periodically calls the run() method of bulk_operation.py
which updates the recommendations in Salesforce database.
"""

import time
import functools
import logging

import schedule
from bulk_operation import run


def with_logging(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info('Running job %s', func.__name__)
        result = func(*args, **kwargs)
        logging.info('Job %s completed', func.__name__)
        return result

    return wrapper


@with_logging
def recommendation_job():
    run()


schedule.every().days.do(recommendation_job)
while True:
    schedule.run_pending()
    time.sleep(3600)
