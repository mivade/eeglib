"""Read and process data from several sources."""

import os
import os.path as osp

import numpy as np
import h5py
import pandas as pd

from .exc import InvalidPathError


class DataReader(object):
    timeseries = pd.DataFrame()
    _time_column = "time"

    def read_timeseries(self, channels, **kwargs):
        """Override to read timeseries EEG data. In addition to returning the
        data as a pandas data frame, this should also set the :attr:`timeseries`
        attribute to the same data frame so that plotting and other
        data-dependent functions will work.

        :param list channels: EEG channels to return.
        :returns: EEG timeseries
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

    def plot_timeseries(self, channels=None, tmin=0, tspan=None):
        """Plot an EEG timeseries.

        :param list channels: If not None, the channels to plot.
        :param float tmin: Start time to limit the plot to.
        :param float tspan: If not None, the total amount of time to plot.
        :returns: axes object

        """
        df = self.get_time_range(channels, tmin, tspan)
        ycols = [col for col in df.cols if col is not self.time_column]
        ax = df.plot(x=self.time_column, y=ycols)
        ax.set_xlabel("time")
        return ax

    def parse_events(self):
        """Override to be able to parse events files."""
        raise NotImplementedError


class RamulatorReader(DataReader):
    """Read and process data from Ramulator.

    :param str path: Path to the directory with EEG data and event JSON file.

    """
    _timeseries_file = "eeg_timeseries.h5"
    _event_log_file = "event_log.json"
    _log_file = "output.log"

    def __init__(self, path):
        self.path = os.expanduser(path)

        if not osp.isdir(self.path):
            raise InvalidPathError("path must be a directory")

        # Check for required files
        contents = os.listdir(self.path)
        for fname in [self._timeseries_file, self._event_log_file, self._log_file]:
            if fname not in contents:
                raise InvalidPathError("{:s} not found in path {:s}".format(
                                       fname, self.path))

    def read_timeseries(self, channels, **kwargs):
        """Read Ramulator timeseries data files (stored in HDF5 format).

        :param list channels:
        :param str channel_type: "zero", "one", or "names" for using
            zero-based indexing, one-based indexing, or contact names (default:
            "zero").

        """
        channel_type = kwargs.get("channel_type", "zero")

        if channel_type is not "zero":
            # FIXME
            raise NotImplementedError("Only zero-indexing is allowed right now")

        filename = osp.join(self.path, self._timeseries_file)

        # TODO: use pytables instead so that only it is required
        with h5py.File(filename, "r") as hfile:
            ports = hfile["ports"].value[channels]
            ts = hfile["timeseries"].value[channels]

        dt = 1 / 1000.  # 1000 Hz sampling rate
        times = np.linspace(0, dt * ts.shape[1], ts.shape[1])

        df = pd.DataFrame.from_items(
            [("time", times)] +
            [("port%d" % port, ts[n]) for n, port in enumerate(ports)])

        self.timeseries = df

        return df
