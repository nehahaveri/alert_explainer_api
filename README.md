# AI Intelligence Layer — Alert Explainer API

A FastAPI service that stores monitoring alerts in SQLite and returns a plain-language explanation for each one. Explanations are generated from fixed rules based on the alert's severity, metric value, and threshold (see [ADR 0001](docs/adr/0001-rule-based-explanations.md)).

## Project structure

```
alert_explainer_api/
├── main.py                 # FastAPI app; creates database tables and registers routers
├── database.py             # SQLite engine (alerts.db), session factory, get_db dependency
├── models.py               # SQLAlchemy Alert model
├── schemas.py              # Pydantic request/response schemas
├── routers/
│   └── alerts.py           # /alerts endpoints
├── services/
│   └── explainer.py        # Rule-based generate_explanation()
├── test_alerts.py          # API tests (in-memory SQLite)
├── requirements.txt
└── docs/
    └── adr/                # Architecture Decision Records
```

## Alert fields

| Field          | Type     | Notes                                           |
| -------------- | -------- | ----------------------------------------------- |
| `id`           | int      | Set by the server                               |
| `title`        | string   | Required                                        |
| `severity`     | string   | Required; one of `critical`, `warning`, `info`  |
| `source`       | string   | Required                                        |
| `metric_name`  | string   | Required                                        |
| `metric_value` | float    | Required                                        |
| `threshold`    | float    | Required                                        |
| `created_at`   | datetime | Set by the server (UTC)                         |

Example request body for creating an alert:

```json
{
  "title": "High CPU usage",
  "severity": "critical",
  "source": "server-1",
  "metric_name": "cpu_usage",
  "metric_value": 95.0,
  "threshold": 80.0
}
```

## Endpoints

| Method | Path                         | Description                          | Status codes                                        |
| ------ | ---------------------------- | ------------------------------------ | --------------------------------------------------- |
| GET    | `/`                          | Health check                         | 200                                                 |
| POST   | `/alerts/`                   | Create an alert                      | 201 Created, 422 Invalid body                       |
| GET    | `/alerts/`                   | List all alerts, ordered by `id`     | 200                                                 |
| GET    | `/alerts/{alert_id}`         | Get one alert                        | 200, 404 Alert not found, 422 Non-integer ID        |
| GET    | `/alerts/{alert_id}/explain` | Generate an explanation for an alert | 200, 404 Alert not found, 422 Non-integer ID        |
| POST   | `/alerts/{alert_id}/explain` | Same as the GET version              | 200, 404 Alert not found, 422 Non-integer ID        |

The explain endpoints return:

```json
{
  "alert_id": 1,
  "explanation": "This critical alert from server-1 is titled \"High CPU usage\". ...",
  "generated_at": "2026-11-19T12:00:00Z"
}
```

Interactive API docs are available at `http://127.0.0.1:8000/docs` while the server is running.

## Install and run on Windows (PowerShell)

```powershell
cd alert_explainer_api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

If PowerShell blocks the activation script, allow it for the current session first:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

The API runs at `http://127.0.0.1:8000`. On startup it creates `alerts.db` in the project folder if it does not exist.

## Run the tests

The tests need `pytest` and `httpx`, which are not listed in `requirements.txt`:

```powershell
pip install pytest httpx
python -m pytest test_alerts.py -v
```

The tests use an in-memory SQLite database and do not touch `alerts.db`.

## Architecture Decision Records

- [ADR 0001: Rule-based alert explanations](docs/adr/0001-rule-based-explanations.md)
- [ADR 0002: Human approval for alert summaries](docs/adr/0002-human-approval-for-alert-summaries.md)
