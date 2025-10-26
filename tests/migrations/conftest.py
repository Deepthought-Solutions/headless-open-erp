"""Conftest for migration tests - overrides parent conftest fixtures."""

import pytest


# Override the parent conftest's test_db fixture to prevent it from running
@pytest.fixture(scope="session", autouse=True)
def test_db():
    """Override parent test_db fixture - migrations tests manage their own DB."""
    # Do nothing - migrations tests use isolated temp databases
    yield


# Override the parent conftest's clean_db_before_each_test fixture
@pytest.fixture(autouse=True)
def clean_db_before_each_test():
    """Override parent clean_db_before_each_test - not needed for migration tests."""
    # Do nothing - migration tests use isolated temp databases
    yield
