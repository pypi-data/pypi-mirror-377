#   ---------------------------------------------------------------------------------
#   Copyright (c) Microsoft Corporation. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""
This is a configuration file for pytest containing customizations and fixtures.

In VSCode, Code Coverage is recorded in config.xml. Delete this file to reset reporting.
"""

from __future__ import annotations

import os
from typing import List

import pytest
from _pytest.nodes import Item

# Try to load .env file if dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Get test credentials from environment
TEST_API_KEY = os.getenv("REPROMPT_API_KEY", os.getenv("REPROMPT_TEST_API_KEY"))
TEST_ORG_SLUG = os.getenv("REPROMPT_ORG_SLUG", os.getenv("REPROMPT_TEST_ORG_SLUG"))


def pytest_collection_modifyitems(items: list[Item]):
    for item in items:
        if "spark" in item.nodeid:
            item.add_marker(pytest.mark.spark)
        elif "_int_" in item.nodeid:
            item.add_marker(pytest.mark.integration)


@pytest.fixture
def unit_test_mocks(monkeypatch: None):
    """Include Mocks here to execute all commands offline and fast."""
    pass
