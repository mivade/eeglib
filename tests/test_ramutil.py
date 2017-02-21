from eeglib.ramutil import read_events


def test_read_events():
    subject = ["R1001P"]
    experiment = ["FR1"]

    # Test reading one subject
    events = read_events(subjects_to_read=subject)
    assert events.subject.unique() == subject
    assert len(events.experiment.unique()) > 1
    assert len(events.session.unique()) > 1

    # Test reading one subject, one experiment
    events = read_events(subjects_to_read=subject,
                         experiments_to_read=experiment)
    assert events.subject.unique() == subject
    assert events.experiment.unique() == experiment
    assert len(events.session.unique()) > 1


if __name__ == "__main__":
    test_read_events()
