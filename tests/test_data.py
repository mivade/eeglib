"""Unit tests for the eeglib.data module."""

import pytest
from eeglib.data import RamulatorReader, DataReader
from util import get_abspath

EVENT_KEYS = [
    "event_label",
    "event_value",
    "event_id"
]


def make_paths_dict(paths):
    return {
        path.split("/")[-1]: get_abspath(path) for path in paths
    }


class TestDataReader:
    def test_from_data(self):
        t = list(range(10))
        data = {
            "a": list(range(10)),
            "b": list(range(10))[::-1]
        }
        dr = DataReader.from_data(t, data)
        cols = dr.timeseries.columns

        assert "time" in cols
        assert "a" in cols
        assert "b" in cols

        assert dr.timeseries.a.iloc[-1] == 9
        assert dr.timeseries.b.iloc[-1] == 0
        assert dr.timeseries.time.iloc[0] == 0


class TestRamulatorReader:
    paths = make_paths_dict(["data/ramulator/ampdet"])

    @pytest.fixture
    def reader(self):
        return RamulatorReader(noread=True)

    def test_read_timeseries(self, reader):
        ts = reader.read_timeseries(self.paths["ampdet"])
        assert "time" in ts.columns
        assert len(ts.columns) is 109

    def test_parse_events(self, reader):
        events = reader.parse_events(self.paths["ampdet"])
        assert "events" in events
        assert isinstance(events["events"], list)

        for event in events["events"]:
            for key in EVENT_KEYS:
                assert key in event
