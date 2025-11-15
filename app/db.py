import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = os.getenv("DB_PATH", "interactions.db")


def get_connection() -> sqlite3.Connection:
    """
    Returns a SQLite connection with Row factory so we can get dict-like rows.

    Dejé esto como función en lugar de usar un pool porque:
    - Es suficiente para el reto.
    - Más adelante sería fácil cambiar a otro backend (ej, DynamoDB).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initialize the database if needed and insert some seed data.

    También sirve como evidencia de "uso": cada vez que levantamos el contenedor,
    si la base aún no existe, se crea con unos pocos registros de prueba.
    """
    db_file = Path(DB_PATH)

    # Creación de carpeta si fuera necesario (por si usamos rutas tipo data/interactions.db)
    if db_file.parent and not db_file.parent.exists():
        db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    cur = conn.cursor()

    # Intento inicial: usar "ts" como nombre de columna.
    # Al final dejé "timestamp" para que calce mejor con el contrato de la API,
    # pero mantuve el comentario como rastro del ensayo y error.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            reason TEXT,
            solution TEXT,
            summary TEXT,
            channel TEXT,
            agent_id TEXT,
            addressed_by TEXT
        )
        """
    )

    # Si ya hay datos, no volvemos a insertar el seed.
    cur.execute("SELECT COUNT(*) AS n FROM interactions")
    row = cur.fetchone()
    if row["n"] == 0:
        seed_data: List[Dict[str, Any]] = [
            {
                "account_number": "ACC-001",
                "timestamp": "2025-11-14T10:00:00Z",
                "reason": "billing",
                "solution": "invoice resent via email",
                "summary": "Customer called about missing invoice; agent resent it.",
                "channel": "voice",
                "agent_id": "agent-123",
                "addressed_by": "AGENT",
            },
            {
                "account_number": "ACC-001",
                "timestamp": "2025-11-14T11:15:00Z",
                "reason": "technical_support",
                "solution": "modem rebooted and line tested",
                "summary": "Customer reported connectivity issues; agent rebooted modem.",
                "channel": "voice",
                "agent_id": "agent-456",
                "addressed_by": "AGENT",
            },
            {
                "account_number": "ACC-002",
                "timestamp": "2025-11-13T09:30:00Z",
                "reason": "plan_change",
                "solution": "plan upgraded to premium",
                "summary": "Customer requested upgrade to a higher data plan.",
                "channel": "chat",
                "agent_id": "agent-789",
                "addressed_by": "AGENT",
            },
        ]

        for item in seed_data:
            cur.execute(
                """
                INSERT INTO interactions (
                    account_number, timestamp, reason, solution, summary,
                    channel, agent_id, addressed_by
                )
                VALUES (:account_number, :timestamp, :reason, :solution, :summary,
                        :channel, :agent_id, :addressed_by)
                """,
                item,
            )

        conn.commit()

    conn.close()
