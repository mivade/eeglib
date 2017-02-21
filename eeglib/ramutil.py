"""Utilities for working with RAM data."""

import os.path as osp
import json
import pandas as pd

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x: x


def read_events(data_root="~/mnt/rhino", subjects_to_read=None,
                experiments_to_read=None, sessions_to_read=None):
    """Read RAM events and return as a :class:`pd.DataFrame`.

    :param str data_root: Root directory for data (e.g. "/" on rhino).
    :param list subjects_to_read: Subjects to read events from or None to read
        all subjects.
    :param list experiments_to_read: Experiment types to read events from or
        None to read all.
    :param list sessions_to_read: Session numbers to read events from or None to
        read all.
    :returns: events_df
    :rtype: pd.DataFrame

    """
    def valid_subject(subject):
        if subjects_to_read is None:
            return True
        else:
            return subject in subjects_to_read

    def valid_experiment(exp):
        if experiments_to_read is None:
            return True
        else:
            return exp in experiments_to_read

    def valid_session(sess):
        if sessions_to_read is None:
            return True
        else:
            return sess in sessions_to_read

    with open(osp.join(osp.expanduser(data_root), "protocols/r1.json")) as f:
        index = json.load(f)["protocols"]["r1"]["subjects"]

    event_files = []
    for subject in index:
        if not valid_subject(subject):
            continue

        experiments = index[subject]["experiments"]

        for experiment in experiments:
            if not valid_experiment(experiment):
                continue
            for _, sessions in experiments[experiment].items():
                for session, exp in sessions.items():
                    if not valid_session(int(session)):
                        continue
                    event_files.append(exp["task_events"])

    events = [pd.read_json(osp.join(data_root, fname))
              for fname in tqdm(event_files)]
    events_df = pd.concat(events)
    events_df.stim_list = [json.dumps(s) if isinstance(s, list) else None
                           for s in events_df.stim_list]
    events_df.stim_params = [json.dumps(s) if isinstance(s, list) else None
                             for s in events_df.stim_params]
    return events_df
