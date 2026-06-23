import argparse
import logging
import sys
from collections.abc import Sequence
from typing import Any, NoReturn, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

from .downloader import DEFAULT_CHUNK_SIZE, DEFAULT_USER_AGENT, download_once
from .models import DownloadFailure, DownloadResult, MeasurementSummary
from .stats import calculate_summary

DEFAULT_REQUESTS_COUNT = 10
DOWNLOAD_ERRORS = (HTTPError, URLError, TimeoutError, OSError)

logger = logging.getLogger(__name__)


class RussianHelpFormatter(argparse.HelpFormatter):
    SECTION_TITLES: dict[str, str] = {
        "positional arguments": "позиционные аргументы",
        "options": "параметры",
    }

    def start_section(self, heading: str | None) -> None:
        if heading is not None:
            heading = self.SECTION_TITLES.get(heading, heading)
        super().start_section(heading)

    def add_usage(
        self,
        usage: str | None,
        actions: Any,
        groups: Any,
        prefix: str | None = None,
    ) -> None:
        super().add_usage(usage, actions, groups, prefix or "использование: ")


class RussianArgumentParser(argparse.ArgumentParser):
    ERROR_REPLACEMENTS = {
        "the following arguments are required": "не указаны обязательные аргументы",
        "unrecognized arguments": "неизвестные аргументы",
        "argument ": "аргумент ",
        "invalid ": "некорректное значение ",
    }

    def error(self, message: str) -> NoReturn:
        for english, russian in self.ERROR_REPLACEMENTS.items():
            message = message.replace(english, russian)

        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: ошибка: {message}\n")


def positive_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("ожидалось число") from error

    if parsed <= 0:
        raise argparse.ArgumentTypeError("значение должно быть больше 0")
    return parsed


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("ожидалось целое число") from error

    if parsed <= 0:
        raise argparse.ArgumentTypeError("значение должно быть больше 0")
    return parsed


def http_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise argparse.ArgumentTypeError("URL должен быть абсолютным http(s)-адресом")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = RussianArgumentParser(
        description="Измеряет скорость скачивания последовательными запросами к URL.",
        formatter_class=RussianHelpFormatter,
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="показать справку и выйти")
    parser.add_argument("url", type=http_url, help="абсолютный URL для скачивания")
    parser.add_argument(
        "--requests",
        type=positive_int,
        default=DEFAULT_REQUESTS_COUNT,
        help=f"количество запросов, по умолчанию: {DEFAULT_REQUESTS_COUNT}",
    )
    parser.add_argument(
        "--timeout",
        type=positive_float,
        default=60.0,
        help="таймаут одного запроса в секундах, по умолчанию: 60",
    )
    parser.add_argument(
        "--chunk-size",
        type=positive_int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"размер блока чтения в байтах, по умолчанию: {DEFAULT_CHUNK_SIZE}",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=f"HTTP-заголовок User-Agent, по умолчанию: {DEFAULT_USER_AGENT}",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="остановиться после первой ошибки запроса",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="показывать диагностические логи",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def format_result(result: DownloadResult) -> str:
    return (
        f"Запрос {result.request_number}: "
        f"{result.elapsed_seconds:.3f} с, "
        f"{result.downloaded_mib:.2f} MiB, "
        f"{result.speed_mib_per_second:.2f} MiB/s"
    )


def format_summary(summary: MeasurementSummary) -> str:
    return "\n".join(
        [
            f"Успешных запросов: {summary.successful_requests}",
            f"Неуспешных запросов: {summary.failed_requests}",
            f"Среднее время запроса: {summary.average_seconds:.3f} с",
            f"Медианное время запроса: {summary.median_seconds:.3f} с",
            f"Самый быстрый запрос: {summary.min_seconds:.3f} с",
            f"Самый медленный запрос: {summary.max_seconds:.3f} с",
            f"Скачано: {summary.total_mib:.2f} MiB",
            f"Средняя скорость: {summary.average_speed_mib_per_second:.2f} MiB/s",
        ]
    )


def run_measurement(
    args: argparse.Namespace,
    *,
    output: TextIO = sys.stdout,
    error_output: TextIO = sys.stderr,
) -> int:
    results: list[DownloadResult] = []
    failures: list[DownloadFailure] = []

    for request_number in range(1, args.requests + 1):
        try:
            result = download_once(
                request_number=request_number,
                url=args.url,
                timeout=args.timeout,
                chunk_size=args.chunk_size,
                user_agent=args.user_agent,
            )
        except DOWNLOAD_ERRORS as error:
            failures.append(DownloadFailure(request_number=request_number, error=error))
            print(f"Запрос {request_number} завершился ошибкой: {error}", file=error_output)
            logger.debug("запрос на скачивание завершился ошибкой", exc_info=error)
            if args.fail_fast:
                break
            continue

        results.append(result)
        print(format_result(result), file=output)

    if not results:
        print("Нет успешно выполненных запросов.", file=error_output)
        return 1

    summary = calculate_summary(results, failed_requests=len(failures))
    print(file=output)
    print(format_summary(summary), file=output)

    return 1 if failures else 0


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="%(levelname)s:%(name)s:%(message)s",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose)
    return run_measurement(args)


if __name__ == "__main__":
    raise SystemExit(main())
