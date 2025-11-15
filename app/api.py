import base64
import json
import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .db import get_connection, init_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interactions-api")

app = FastAPI(
    title="Interactions API",
    description="Minimal interactions history API for a technical challenge.",
    version="0.1.0",
)


class InteractionItem(BaseModel):
    id: int
    account_number: str
    timestamp: str
    reason: Optional[str] = None
    solution: Optional[str] = None
    summary: Optional[str] = None
    channel: Optional[str] = None
    agent_id: Optional[str] = None
    addressed_by: Optional[str] = None


class InteractionsResponse(BaseModel):
    account_number: str
    items: List[InteractionItem]
    next_cursor: Optional[str] = None


def encode_cursor(last_id: int) -> str:
    """
    Encode a cursor as base64 JSON.

    Al principio consideré usar OFFSET para paginación,
    pero con muchos datos se vuelve más costoso.
    Dejo aquí la versión con 'cursor' basada en id.
    """
    payload = {"last_id": last_id}
    raw = json.dumps(payload)
    return base64.b64encode(raw.encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str) -> int:
    """
    Decode cursor from base64 JSON to last_id integer.
    """
    try:
        raw = base64.b64decode(cursor.encode("utf-8")).decode("utf-8")
        payload = json.loads(raw)
        last_id = int(payload.get("last_id", 0))
        return last_id
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to decode cursor %s: %s", cursor, exc)
        raise HTTPException(status_code=400, detail="Invalid cursor") from exc


@app.on_event("startup")
async def startup_event() -> None:
    # Esto se ejecuta cuando se levanta la app dentro del contenedor.
    logger.info("Starting up Interactions API. Ensuring DB is initialized.")
    init_db()


@app.get(
    "/interactions/{account_number}",
    response_model=InteractionsResponse,
    summary="Get interactions for an account with cursor-based pagination",
)
async def get_interactions(
    account_number: str,
    limit: int = Query(10, gt=0, le=100, description="Max items per page"),
    cursor: Optional[str] = Query(
        None, description="Opaque pagination cursor from previous response"
    ),
) -> InteractionsResponse:
    """
    Minimal GET endpoint that:
    - Reads from SQLite.
    - Returns JSON.
    - Supports cursor-based pagination.

    Ejemplo de llamada:
    GET /interactions/ACC-001?limit=2
    """
    logger.info(
        "Fetching interactions for account=%s limit=%s cursor_raw=%s",
        account_number,
        limit,
        cursor,
    )

    last_id = 0
    if cursor:
        last_id = decode_cursor(cursor)

    conn = get_connection()
    cur = conn.cursor()
    """
    Versión con cursor basado en id.
    Dejo un comentario de la versión anterior con OFFSET como rastro de iteración:
    
    SELECT ... WHERE account_number=? ORDER BY id ASC LIMIT ? OFFSET ?
    
    Pero finalmente usé la condición "id > last_id" para evitar problemas
    de rendimiento con muchas filas
    """
    sql = """
        SELECT
            id,
            account_number,
            timestamp,
            reason,
            solution,
            summary,
            channel,
            agent_id,
            addressed_by
        FROM interactions
        WHERE account_number = ?
            AND id > ?
        ORDER BY id ASC
        LIMIT ?
    """

    cur.execute(sql, (account_number, last_id, limit))
    rows = cur.fetchall()
    conn.close()

    if not rows and last_id == 0:
        # Si primera página y no hay resultados, devolvemos 404 para ser explícitos.
        raise HTTPException(
            status_code=404, detail="No interactions for this account")

    items: List[InteractionItem] = [
        InteractionItem(**dict(row)) for row in rows
    ]

    # Si devolvimos menos de limit, no generamos next_cursor.
    if len(rows) == limit:
        new_last_id = rows[-1]["id"]
        next_cursor = encode_cursor(new_last_id)
    else:
        next_cursor = None

    response = InteractionsResponse(
        account_number=account_number,
        items=items,
        next_cursor=next_cursor,
    )

    logger.debug(
        "Returning %s interactions for account=%s next_cursor=%s",
        len(items),
        account_number,
        next_cursor,
    )

    return response
