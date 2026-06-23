# AD Robot Speed Measurer

Простая консольная утилита для измерения скорости скачивания файла по HTTP(S).

Программа несколько раз подряд скачивает указанный URL и показывает время, объем данных и среднюю скорость.

## Установка

Нужен Python 3.11 или новее.

```bash
python -m pip install -r requirements.txt
```

## Запуск

```bash
python main.py https://example.com/large-file.bin
```

Пример с настройками:

```bash
python main.py https://example.com/file.bin --requests 20 --timeout 10 --chunk-size 65536 --fail-fast
```

Примеры с тестовым файлом Cloudflare на 1 MiB:

```bash
python main.py "https://speed.cloudflare.com/__down?bytes=1048576"
```

Быстрая проверка одним запросом:

```bash
python main.py "https://speed.cloudflare.com/__down?bytes=1048576" --requests 1 --timeout 15
```

Основные параметры:

- `--requests` - количество скачиваний, по умолчанию 10.
- `--timeout` - таймаут одного запроса в секундах, по умолчанию 60.
- `--chunk-size` - размер блока чтения в байтах.
- `--fail-fast` - остановиться после первой ошибки.
- `--verbose` - показать диагностические логи.

## Проверка проекта

```bash
python -m pytest
python -m ruff check .
python -m mypy
```
