import time
from urllib.request import Request, urlopen

from .models import DownloadResult

DEFAULT_CHUNK_SIZE = 64 * 1024
DEFAULT_USER_AGENT = "speed-measurer/1.0"


def download_once(
    *,
    request_number: int,
    url: str,
    timeout: float,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    user_agent: str = DEFAULT_USER_AGENT,
) -> DownloadResult:
    request = Request(url, headers={"User-Agent": user_agent})
    started_at = time.perf_counter()
    downloaded_bytes = 0

    with urlopen(request, timeout=timeout) as response:
        while chunk := response.read(chunk_size):
            downloaded_bytes += len(chunk)

    return DownloadResult(
        request_number=request_number,
        elapsed_seconds=time.perf_counter() - started_at,
        downloaded_bytes=downloaded_bytes,
    )
