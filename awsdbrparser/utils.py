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
import json

import click

from . import __version__


def split_subkeys(json_string):
    """
    Find json keys like ``"{key.subkey: value}"`` and replaces
    with ``"{key : {subkey: value}}"``.

    :param str json_string:
    :returns: json string
    :rtype: str
    """

    json_key = json.loads(json_string)
    temp_json = {}
    for key, value in json_key.items():
        index = key.find(':')
        if index > -1:
            if temp_json.get(key[:index], 1) == 1:
                temp_json[key[:index]] = {}
            temp_json[key[:index]][key[index + 1:]] = value
        else:
            temp_json.update({key: value})
    return temp_json


def bulk_data(json_string, bulk):
    """
    Check if json has bulk data/control messages. The string to check are in
    format: ``{key : [strings]}``.

    :param str json_string:
    :param bool bulk:
    :returns: True if found a control message and False if not.
    :rtype: bool
    """
    json_key = json.loads(json_string)
    for key, value in bulk.items():
        if key in json_key.keys():
            for v in bulk[key]:
                if json_key[key].find(v) > -1:
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
