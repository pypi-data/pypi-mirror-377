import random

from trackio import utils


def test_generate_readable_names_are_unique_even_with_seed():
    names = []
    for _ in range(10):
        random.seed(42)
        names.append(utils.generate_readable_name(names))
    assert len(names) == len(set(names))


def test_sort_metrics_by_prefix():
    metrics = ["train/loss", "loss", "train/acc", "val/loss", "accuracy"]
    result = utils.sort_metrics_by_prefix(metrics)
    expected = ["accuracy", "loss", "train/acc", "train/loss", "val/loss"]
    assert result == expected


def test_group_metrics_by_prefix():
    metrics = ["loss", "accuracy", "train/loss", "train/acc", "val/loss", "test/f1"]
    result = utils.group_metrics_by_prefix(metrics)
    expected = {
        "charts": ["accuracy", "loss"],
        "test": ["test/f1"],
        "train": ["train/acc", "train/loss"],
        "val": ["val/loss"],
    }
    assert result == expected


def test_group_metrics_with_subprefixes():
    metrics = [
        "loss",
        "train/acc",
        "train/loss/normalized",
        "train/loss/unnormalized",
        "val/loss",
        "test/f1/micro",
        "test/f1/macro",
    ]
    result = utils.group_metrics_with_subprefixes(metrics)
    expected = {
        "charts": {"direct_metrics": ["loss"], "subgroups": {}},
        "train": {
            "direct_metrics": ["train/acc"],
            "subgroups": {"loss": ["train/loss/normalized", "train/loss/unnormalized"]},
        },
        "val": {"direct_metrics": ["val/loss"], "subgroups": {}},
        "test": {
            "direct_metrics": [],
            "subgroups": {"f1": ["test/f1/macro", "test/f1/micro"]},
        },
    }
    assert result == expected


def test_format_timestamp():
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)

    two_minutes_ago = (now - timedelta(minutes=2)).isoformat()
    assert utils.format_timestamp(two_minutes_ago) == "2 minutes ago"

    one_hour_ago = (now - timedelta(hours=1)).isoformat()
    assert utils.format_timestamp(one_hour_ago) == "1 hour ago"

    two_days_ago = (now - timedelta(days=2)).isoformat()
    assert utils.format_timestamp(two_days_ago) == "2 days ago"

    thirty_seconds_ago = (now - timedelta(seconds=30)).isoformat()
    assert utils.format_timestamp(thirty_seconds_ago) == "Just now"

    assert utils.format_timestamp(None) == "Unknown"
    assert utils.format_timestamp("invalid") == "Unknown"
