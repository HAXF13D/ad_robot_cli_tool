import argparse

import pytest

from ad_robot.cli import build_parser, format_result, format_summary
from ad_robot.models import DownloadResult
from ad_robot.stats import calculate_summary


def parse_args(*args: str) -> argparse.Namespace:
    return build_parser().parse_args(list(args))


def test_parser_accepts_valid_options() -> None:
    args = parse_args(
        "https://example.com/file.bin",
        "--requests",
        "3",
        "--timeout",
        "1.5",
        "--chunk-size",
        "1024",
        "--fail-fast",
    )

    assert args.url == "https://example.com/file.bin"
    assert args.requests == 3
    assert args.timeout == 1.5
    assert args.chunk_size == 1024
    assert args.fail_fast is True


@pytest.mark.parametrize(
    "args",
    [
        ("ftp://example.com/file.bin",),
        ("https://example.com/file.bin", "--requests", "0"),
        ("https://example.com/file.bin", "--timeout", "-1"),
        ("https://example.com/file.bin", "--chunk-size", "0"),
    ],
)
def test_parser_rejects_invalid_values(args: tuple[str, ...]) -> None:
    with pytest.raises(SystemExit):
        parse_args(*args)


def test_help_output_uses_russian_labels(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        parse_args("--help")

    assert exit_info.value.code == 0

    help_output = capsys.readouterr().out

    assert "использование:" in help_output
    assert "позиционные аргументы:" in help_output
    assert "параметры:" in help_output
    assert "показать справку и выйти" in help_output
    assert "show this help message and exit" not in help_output


def test_format_result_includes_request_metrics() -> None:
    result = DownloadResult(
        request_number=2,
        elapsed_seconds=2.0,
        downloaded_bytes=4 * 1024 * 1024,
    )

    assert format_result(result) == "Запрос 2: 2.000 с, 4.00 MiB, 2.00 MiB/s"


def test_format_summary_uses_russian_labels() -> None:
    result = DownloadResult(
        request_number=1,
        elapsed_seconds=2.0,
        downloaded_bytes=4 * 1024 * 1024,
    )

    summary = calculate_summary([result], failed_requests=1)

    assert format_summary(summary) == "\n".join(
        [
            "Успешных запросов: 1",
            "Неуспешных запросов: 1",
            "Среднее время запроса: 2.000 с",
            "Медианное время запроса: 2.000 с",
            "Самый быстрый запрос: 2.000 с",
            "Самый медленный запрос: 2.000 с",
            "Скачано: 4.00 MiB",
            "Средняя скорость: 2.00 MiB/s",
        ]
    )
