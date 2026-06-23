import pytest

from src.ad_robot.models import DownloadResult
from src.ad_robot.stats import calculate_summary


def test_calculate_summary_uses_successful_requests_only() -> None:
    results = [
        DownloadResult(request_number=1, elapsed_seconds=2.0, downloaded_bytes=2 * 1024 * 1024),
        DownloadResult(request_number=3, elapsed_seconds=4.0, downloaded_bytes=6 * 1024 * 1024),
    ]

    summary = calculate_summary(results, failed_requests=1)

    assert summary.successful_requests == 2
    assert summary.failed_requests == 1
    assert summary.total_seconds == 6.0
    assert summary.average_seconds == 3.0
    assert summary.median_seconds == 3.0
    assert summary.min_seconds == 2.0
    assert summary.max_seconds == 4.0
    assert summary.total_mib == 8.0
    assert summary.average_speed_mib_per_second == pytest.approx(8.0 / 6.0)


def test_calculate_summary_requires_successful_request() -> None:
    with pytest.raises(ValueError, match="at least one successful request"):
        calculate_summary([])
