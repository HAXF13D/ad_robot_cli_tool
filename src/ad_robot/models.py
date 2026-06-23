from dataclasses import dataclass

BYTES_IN_MIB = 1024 * 1024


@dataclass(frozen=True, slots=True)
class DownloadResult:
    request_number: int
    elapsed_seconds: float
    downloaded_bytes: int

    @property
    def downloaded_mib(self) -> float:
        return self.downloaded_bytes / BYTES_IN_MIB

    @property
    def speed_mib_per_second(self) -> float:
        if self.elapsed_seconds <= 0:
            return 0.0
        return self.downloaded_mib / self.elapsed_seconds


@dataclass(frozen=True, slots=True)
class DownloadFailure:
    request_number: int
    error: Exception


@dataclass(frozen=True, slots=True)
class MeasurementSummary:
    successful_requests: int
    failed_requests: int
    total_seconds: float
    average_seconds: float
    median_seconds: float
    min_seconds: float
    max_seconds: float
    total_bytes: int
    average_speed_mib_per_second: float

    @property
    def total_mib(self) -> float:
        return self.total_bytes / BYTES_IN_MIB
