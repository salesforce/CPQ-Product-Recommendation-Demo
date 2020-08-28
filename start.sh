# Copyright (c) 2018, salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see LICENSE.txt file in the repo root or
# https://opensource.org/licenses/BSD-3-Clause

datetime=$(date +"%FT%H%M%S")
nohup ./job.py > "$datetime.log" 2>&1 &