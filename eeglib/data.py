"""Read and process data from several sources."""

# TODO: allow for relative vs. absolute times

from __future__ import division
import os.path as osp
import json

import numpy as np
import h5py
import pandas as pd

from eeglib.exc import InvalidPathError


class DataReader(object):
    """Base class for EEG data readers. Deriving classes should not override
    this method but instead implement the :meth:`initialize` method to do
    anything else required. This custom initialization occurs before the file is
    read.

    Once timeseries data is read, it is placed in the :attr:`timeseries` data
    frame. Any metadata that you wish to save should be placed in the
    :attr:`metadata` dict which is by default empty.

    :param str path: Path to the directory containing EEG data or an EEG data
        file (reader-specific).
    :param list channels: When not None, limit number of channels to read.
    :param bool noread: When True, don't automatically try to read data on
        object initialization.
    :param dict kwargs: Keyword arguments to pass along to :meth:`initialize`.

    """
    def __init__(self, path=None, channels=None, noread=False, **kwargs):
        self.timeseries = pd.DataFrame()
        self.events = dict()
        self.metadata = dict()
        # self.jacksheet = dict()
        self._time_column = "time"

        if path is not None:
            path = osp.expanduser(path)

            if not osp.isdir(path):
                raise InvalidPathError("path must be a directory")

        self.initialize(**kwargs)

        if not noread and path is not None:
            self.read_timeseries(path, channels=channels)

    def initialize(self, **kwargs):
        """Override this method for custom initialization to be performed after
        generic initialization.

        """
        pass

    def read_timeseries(self, path, channels=None):
        """Override to read timeseries EEG data. In addition to returning the
        data as a pandas data frame, this should also set the :attr:`timeseries`
        attribute to the same data frame so that plotting and other
        data-dependent functions will work.

        :param str path: Path to data.
        :param list channels: EEG channels to return or None to return all.
        :returns: EEG timeseries.
        :rtype: pd.DataFrame

        """
        raise NotImplementedError

    @property
    def time_column(self):
        """The label for the time column. Default: `"time"`."""
        return self._time_column

    @time_column.setter
    def time_column(self, new_label):
        self._time_column = new_label

    @classmethod
    def from_data(cls, times, data, **kwargs):
        """Create a new :class:`DataReader` object given previously-read data.

        :param list times: Times for the data
        :param dict data: Dictionary of arrays of data (keys are channel
            labels).
        :param dict kwargs: Keyword arguments to be passed to
            :meth:`initialize`.

        """
        assert isinstance(times, (list, tuple, np.ndarray))
        assert isinstance(data, dict)

        df = pd.DataFrame.from_items(
            [("time", times)] +
            [(label, ts) for label, ts in data.items()]
        )

        instance = cls(**kwargs)
        instance.timeseries = df

        return instance

    def get_time_range(self, channels=None, tmin=0, tspan=None):
        """Return a limited subset of timeseries data.

        :param list channels: Channels to return or None to return all.
        :param float tmin: Start time to limit data to.
        :param float tspan: Total amount of time to return.

        """
        if channels is not None:
            df = self.timeseries[[self.time_column] + channels]
        else:
            df = self.timeseries

        if tspan is None:
            return df[df[self.time_column] >= tmin]
        else:
            return df[(df[self.time_column] >= tmin) & (df[self.time_column] <= (tmin + tspan))]

    def plot_timeseries(self, channels=None, tmin=0, tspan=None, **kwargs):
        """Plot an EEG timeseries.

        :param list channels: If not None, the channels to plot.
        :param float tmin: Start time to limit the plot to.
        :param float tspan: If not None, the total amount of time to plot.
        :param dict kwargs: Keyword arguments to pass to the data frame's
            :meth:`plot` method.
        :returns: axes object

        """
        df = self.get_time_range(channels, tmin, tspan)
        ycols = [col for col in df.columns if col is not self.time_column]
        ax = df.plot(x=self.time_column, y=ycols, **kwargs)
        ax.set_xlabel("time")
        return ax

    def parse_events(self, path):
        """Override to be able to parse events files.

        In addition to returning the events as a dict, this should also set the
        :attr:`events` dict so as to be accessible later.

        """
        raise NotImplementedError


class RamulatorReader(DataReader):
    """Read and process data from Ramulator.

    :param str path: Path to the directory with EEG data and event JSON file.

    """
    _timeseries_file = "eeg_timeseries.h5"
    _event_log_file = "event_log.json"
    _log_file = "output.log"

    def read_timeseries(self, path, channels=None):
        """Read Ramulator timeseries data files (stored in HDF5 format).

        :param str path: Path to the directory containing the data.
        :param list channels: List of channels to read or None to read all.

        """
        filename = osp.join(path, self._timeseries_file)

        # TODO: use pytables instead so that only it is required
        with h5py.File(filename, "r") as hfile:
            if channels is not None:
                ports = hfile["ports"].value[channels]
                ts = hfile["timeseries"].value[channels]
            else:
                ports = hfile["ports"].value
                ts = hfile["timeseries"].value

        dt = 1 / 1000.  # 1000 Hz sampling rate
        times = np.linspace(0, dt * ts.shape[1], ts.shape[1])

        df = pd.DataFrame.from_items(
            [("time", times)] +
            [("port%d" % port, ts[n]) for n, port in enumerate(ports)])

        self.timeseries = df

        return df

    def parse_events(self, path):
        """Parse JSON events file.

        :param str path: Path to directory containing data.

        """
        filename = osp.join(path, self._event_log_file)
        with open(filename, "r") as events_file:
            events = json.load(events_file)

        self.events = events
        return self.events


if __name__ == "__main__":
    pass
