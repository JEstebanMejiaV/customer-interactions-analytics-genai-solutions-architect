from app import db


def test_init_db_creates_db_and_seed(tmp_path):
    # Usamos una base de datos temporal para no tocar nada "real"
    test_db_path = tmp_path / "interactions_test.db"
    db.DB_PATH = str(test_db_path)

    db.init_db()

    assert test_db_path.exists()

    # Y la tabla interactions existe y tiene datos de seed
    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'"
    )
    assert cur.fetchone() is not None

    cur.execute("SELECT COUNT(*) FROM interactions")
    (count,) = cur.fetchone()
    assert count >= 1

    conn.close()
