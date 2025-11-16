# Solutions Architect (Customer Interactions Analytics with Gen AI on AWS)
## 1. Project goal

This repo focuses on the hands-on part of the challenge:

- Implement `GET /interactions/{account_number}` with cursor-based pagination.
- Serve the endpoint via a FastAPI HTTP service.
- Persist and read interactions from a lightweight local SQLite database.
- Package everything in a Docker image that can be built and run locally. :contentReference[oaicite:1]{index=1}


## 2. Repository structure (high-level)

- `app/` – FastAPI application (routes, models, DB access, pagination helpers).
- `contracts/` – API contract examples and sample payloads.
- `infra/` – AWS CDK example showing API Gateway + Lambda + DynamoDB.
- `lambda/` – Lambda-oriented code aligned with the CDK stack.
- `slides/` – Architecture slides for the overall GenAI customer-interactions platform.
- `tests/` – Unit tests for the Interactions API.
- `Dockerfile` – Container image definition for the FastAPI service.
- `requirements.txt` – Python dependencies.

# 3. Interactions API

Minimal implementation of `GET /interactions/{account_number}` for a technical challenge.

This project:

- Runs an HTTP API using **FastAPI**.
- Reads interaction data from a local **SQLite** database.
- Returns JSON with **cursor-based pagination**.
- Is containerized with **Docker**.


## 3.1. Requirements

- Docker installed.
- Optionally, Python 3.12+ if you want to run it without Docker.



## 3.2. Build the image

In the project root (where the `Dockerfile` lives):

```bash
docker build -t interactions-api .
```



## 3.3. Run the container

```bash
docker run -p 8080:8080 interactions-api
```

This will:

- Start the FastAPI server on port `8080`.
- Create a local `interactions.db` SQLite file if it does not exist.
- Insert a few seed rows for accounts `ACC-001` and `ACC-002`.



## 4. Test the API

### 4.1. Using `curl`

Get the first page of interactions for account `ACC-001`:

```bash
curl "http://localhost:8080/interactions/ACC-001?limit=2"
```

Example response:

```json
{
  "account_number": "ACC-001",
  "items": [
    {
      "id": 1,
      "account_number": "ACC-001",
      "timestamp": "2025-11-14T10:00:00Z",
      "reason": "billing",
      "solution": "invoice resent via email",
      "summary": "Customer called about missing invoice; agent resent it.",
      "channel": "voice",
      "agent_id": "agent-123",
      "addressed_by": "AGENT"
    },
    {
      "id": 2,
      "account_number": "ACC-001",
      "timestamp": "2025-11-14T11:15:00Z",
      "reason": "technical_support",
      "solution": "modem rebooted and line tested",
      "summary": "Customer reported connectivity issues; agent rebooted modem.",
      "channel": "voice",
      "agent_id": "agent-456",
      "addressed_by": "AGENT"
    }
  ],
  "next_cursor": "eyJsYXN0X2lkIjoyfQ=="
}
```

Use the `next_cursor` value as the `cursor` parameter to get the next page:

```bash
curl "http://localhost:8080/interactions/ACC-001?limit=2&cursor=eyJsYXN0X2lkIjoyfQ=="
```

If there are no more interactions, `next_cursor` will be `null`.

### 4.2. Using Postman

1. Create a new `GET` request.
2. URL: `http://localhost:8080/interactions/ACC-001`
3. Add query params:
   - `limit` = `2`
   - optionally `cursor` with the value returned by the previous call.
4. Send the request and inspect the JSON response.



## 5. Run without Docker (optional)

If you want to run the server directly:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.api:app --reload --port 8080
```

Then use the same curl or Postman calls as above.



## 6. Optional: AWS CDK example (API Gateway + Lambda + DynamoDB)

The `infra/` folder contains a minimal AWS CDK example that shows how this
API could be deployed using API Gateway, Lambda and DynamoDB.

> This CDK code is not wired to the FastAPI container. It is only meant to
> demonstrate **Infrastructure as Code** skills.

### 6.1. Install CDK dependencies

```bash
cd infra
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 6.2. Synthesize the template

```bash
cdk synth
```

From here you could deploy with `cdk deploy` (after configuring your AWS
account and region), but that is intentionally outside the scope of this
minimal example.


# Autor: Juan Esteban Mejía Velásquez
