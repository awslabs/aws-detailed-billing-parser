# -*- coding: utf-8 -*-
#
# awsdbrparser/utils.py
#
# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import contextlib

import click

from . import __version__


def pre_process(json_dict):
    """
    Find json keys like '{"key:subkey": "value"}' and replaces
    with '{"key" : {"subkey" : "value"}}'.

    Get items that are EC2 running and evaluate if the instance is:
    * On-Demand
    * Reserved Instance
    * Spot
    The result is included in the field: UsageItem

    The instance size is included in the new field: InstanceType

    :param dict json_dict:
    :returns: json dict
    :rtype: dict
    """
    temp_json = dict()
    for key, value in json_dict.items():
        if ':' in key:
            # This key has COLON, let's try to split this key in key/subkey
            new_key, subkey = key.split(':', 1)
            temp_json.setdefault(new_key, {}).setdefault(subkey, value)
        else:
            temp_json.setdefault(key, value)

    temp_json['UsageItem'] = ''

    if temp_json.get('ProductName') == 'Amazon Elastic Compute Cloud' and 'RunInstances' in temp_json.get('Operation'):
        # Some lineitems contain strings like: "RunInstances:002".
        if temp_json.get('ReservedInstance', '') == 'Y':
            temp_json['UsageItem'] = 'Reserved Instance'

        elif 'BoxUsage' in temp_json.get('UsageType', ' '):
            # If this LineItem is a EC2 instance running we include 'EC2-Running'
            temp_json['UsageItem'] = 'On-Demand'

        elif 'SpotUsage' in temp_json.get('UsageType', ' '):
            temp_json['UsageItem'] = 'Spot Instance'

        if ':' in temp_json.get('UsageType'):
            temp_json['InstanceType'] = temp_json.get('UsageType').split(':')[1]
        else:
            temp_json['InstanceType'] = 'N/A'

    return temp_json


def bulk_data(json_string, bulk):
    """
    Check if json has bulk data/control messages. The string to check are in
    format: ``{key : [strings]}``.
    If the key/value is found return True else False

    :param dict json_string:
    :param dict bulk:
    :returns: True if found a control message and False if not.
    :rtype: bool
    """
    for key, value in bulk.items():
        if key in json_string.keys():
            for line in value:
                if json_string.get(key) == line:
                    return True
    return False


def values_of(choices):
    """
    Returns a tuple of values from choices options represented as a tuple of
    tuples (value, label). For example:

    .. sourcecode:: python

        >>> values_of((
        ...         ('1', 'One'),
        ...         ('2', 'Two'),))
        ('1', '2')

    :rtype: tuple
    """
    return tuple([value for value, label in choices])


def hints_for(choices):
    """
    Build a hint string from choices options represented as a tuple of tuples.
    For example:

    .. sourcecode:: python

        >>> hints_for((
        ...         ('1', 'One'),
        ...         ('2', 'Two'),))
        '1=One, 2=Two'

    :rtype: str
    """
    return ', '.join(['{}={}'.format(value, label) for value, label in choices])


def display_banner(echo=None):
    echo = echo or click.echo
    echo("   ___      _____ ___  ___ ___ ___                      ")
    echo("  /_\ \    / / __|   \| _ ) _ \ _ \__ _ _ _ ___ ___ _ _ ")
    echo(" / _ \ \/\/ /\__ \ |) | _ \   /  _/ _` | '_(_-</ -_) '_|")
    echo("/_/ \_\_/\_/ |___/___/|___/_|_\_| \__,_|_| /__/\___|_|  ")
    echo("AWS - Detailed Billing Records parser, version {}\n".format(__version__))


@contextlib.contextmanager
def null_progressbar(*arg, **kwargs):
    yield


class ClickEchoWrapper(object):
    def __init__(self, quiet=False):
        self._quiet = quiet

    def __call__(self, *args, **kwargs):
        if self._quiet:
            return
        click.echo(*args, **kwargs)
