from statistics import median

from .models import DownloadResult, MeasurementSummary


def calculate_summary(
    results: list[DownloadResult],
    *,
    failed_requests: int = 0,
) -> MeasurementSummary:
    if not results:
        raise ValueError("at least one successful request is required")

    timings = [result.elapsed_seconds for result in results]
    total_seconds = sum(timings)
    total_bytes = sum(result.downloaded_bytes for result in results)
    total_mib = total_bytes / 1024 / 1024

    return MeasurementSummary(
        successful_requests=len(results),
        failed_requests=failed_requests,
        total_seconds=total_seconds,
        average_seconds=total_seconds / len(results),
        median_seconds=median(timings),
        min_seconds=min(timings),
        max_seconds=max(timings),
        total_bytes=total_bytes,
        average_speed_mib_per_second=total_mib / total_seconds
        if total_seconds > 0
        else 0.0,
    )
