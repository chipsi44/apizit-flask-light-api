# Flask Data API

A small public REST API built with Flask, Pandas, and NumPy. It exposes a few
useful data operations without requiring a database or external service.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/summary` | Descriptive statistics for a numeric series |
| `POST` | `/api/v1/normalize` | Z-score normalization |
| `POST` | `/api/v1/correlation` | Pearson correlation between two series |

All inputs must be finite JSON numbers. Request bodies are limited to 64 KiB.

## Run locally

Requirements: Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run flask --app app run --debug
```

The API will be available at `http://127.0.0.1:5000`.

## Examples

Summary:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/summary \
  -H "Content-Type: application/json" \
  -d '{"values":[4,8,15,16,23,42]}'
```

Normalization:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/normalize \
  -H "Content-Type: application/json" \
  -d '{"values":[10,20,30]}'
```

Correlation:

```bash
curl -X POST http://127.0.0.1:5000/api/v1/correlation \
  -H "Content-Type: application/json" \
  -d '{"x":[1,2,3,4],"y":[2,4,6,8]}'
```

## Tests

```bash
uv run pytest
```

## License

MIT
