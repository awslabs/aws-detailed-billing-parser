# -*- coding: utf-8 -*-
#
# tests/cli.py
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
import pytest

from click.testing import CliRunner

from awsdbrparser import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code != 0  # should raises IOError for missing default input file


def test_cli_with_option(runner):
    result = runner.invoke(cli.main, ['--version'])
    assert not result.exception
    assert result.exit_code == 0
    assert 'AWS - Detailed Billing Records parser' in result.output
