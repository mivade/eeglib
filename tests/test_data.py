"""Unit tests for the eeglib.data module."""

import pytest
from eeglib.data import RamulatorReader
from util import get_abspath


class TestRamulatorReader:
    @pytest.fixture
    def reader(self):
        return RamulatorReader(get_abspath("data/ramulator/ampdet"), noread=True)

    def test_read_timeseries(self, reader):
        ts = reader.read_timeseries()
        assert "time" in ts.columns
        assert len(ts.columns) is 109
