#!/usr/bin/env python

# Copyright 2016 Workiva Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# create_kinesis_stream.py
#
# Script that create a Kinesis Stream.

# system imports
import argparse
import logging
import sys

# library imports

# application imports
from aws_lambda_fsm.aws import get_connection
from aws_lambda_fsm.aws import get_arn_from_arn_string
from aws_lambda_fsm.aws import validate_config
from aws_lambda_fsm.constants import AWS

import settings

# setup the command line args
parser = argparse.ArgumentParser(description='Creates AWS Kinesis streams.')
parser.add_argument('--kinesis_stream_arn', default='PRIMARY_STREAM_SOURCE')
parser.add_argument('--kinesis_num_shards', type=int, default=10)
parser.add_argument('--log_level', default='INFO')
parser.add_argument('--boto_log_level', default='INFO')
args = parser.parse_args()

logging.basicConfig(
    format='[%(levelname)s] %(asctime)-15s %(message)s',
    level=int(args.log_level) if args.log_level.isdigit() else args.log_level,
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.getLogger('boto3').setLevel(args.boto_log_level)
logging.getLogger('botocore').setLevel(args.boto_log_level)

validate_config()

# setup connections to AWS
kinesis_stream_arn = getattr(settings, args.kinesis_stream_arn)
logging.info('Kinesis stream ARN: %s', kinesis_stream_arn)
logging.info('Kinesis endpoint: %s', settings.ENDPOINTS.get(AWS.KINESIS))
if get_arn_from_arn_string(kinesis_stream_arn).service != AWS.KINESIS:
    logging.fatal("%s is not a Kinesis ARN", kinesis_stream_arn)
    sys.exit(1)
kinesis_conn = get_connection(kinesis_stream_arn, disable_chaos=True)
kinesis_stream = get_arn_from_arn_string(kinesis_stream_arn).slash_resource()
logging.info('Kinesis stream: %s', kinesis_stream)

# configure the stream
response = kinesis_conn.create_stream(
    StreamName=kinesis_stream,
    ShardCount=args.kinesis_num_shards
)
logging.info(response)
