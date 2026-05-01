import pyodbc
import datetime
from flask import g

SERVER   = r'localhost\SQLEXPRESS'
DATABASE = 'ScoutingApp'
DRIVER   = 'ODBC Driver 17 for SQL Server'


def _connect():
    conn_str = (
        f'DRIVER={{{DRIVER}}};'
        f'SERVER={SERVER};'
        f'DATABASE={DATABASE};'
        f'Trusted_Connection=yes;'
        f'Encrypt=no;'
    )
    return pyodbc.connect(conn_str)


# ── Row wrapper ───────────────────────────────────────────────────────────────

class _Row(dict):
    """Dict-like row supporting both key and index access."""
    def __init__(self, cols, values):
        super().__init__(zip(cols, values))
        self._cols = cols
        self._vals = list(values)
        # Convert datetime objects to strings so templates can slice them
        for k, v in list(self.items()):
            if isinstance(v, (datetime.datetime, datetime.date)):
                self[k] = v.strftime('%Y-%m-%d %H:%M:%S')

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._vals[key]
        # Case-insensitive fallback
        try:
            return super().__getitem__(key)
        except KeyError:
            for k in self:
                if k.lower() == str(key).lower():
                    return super().__getitem__(k)
            raise

    def keys(self):
        return self._cols


# ── Cursor wrapper ────────────────────────────────────────────────────────────

class _Cursor:
    def __init__(self, cursor):
        self._c = cursor

    def _cols(self):
        return [d[0] for d in self._c.description] if self._c.description else []

    def fetchone(self):
        try:
            row = self._c.fetchone()
        except pyodbc.ProgrammingError:
            return None
        if row is None:
            return None
        return _Row(self._cols(), row)

    def fetchall(self):
        try:
            rows = self._c.fetchall()
        except pyodbc.ProgrammingError:
            return []
        cols = self._cols()
        return [_Row(cols, r) for r in rows]

    @property
    def lastrowid(self):
        self._c.execute("SELECT SCOPE_IDENTITY()")
        val = self._c.fetchone()[0]
        return int(val) if val is not None else None


# ── Connection wrapper ────────────────────────────────────────────────────────

class _DB:
    def __init__(self, conn):
        self._conn = conn
        self._cur  = conn.cursor()

    def execute(self, sql, params=()):
        if params:
            self._cur.execute(sql, list(params))
        else:
            self._cur.execute(sql)
        return _Cursor(self._cur)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


# ── Flask helpers ─────────────────────────────────────────────────────────────

def get_db():
    if 'db' not in g:
        g.db = _DB(_connect())
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ── Schema creation ───────────────────────────────────────────────────────────

_SCHEMA = [
    """
    IF OBJECT_ID('reports', 'U') IS NULL
    CREATE TABLE reports (
        id             INT IDENTITY(1,1) PRIMARY KEY,
        player_id      INT           NOT NULL,
        rating         DECIMAL(2,1) NOT NULL CHECK(rating BETWEEN 1 AND 5 AND rating * 2 = FLOOR(rating * 2)),
        minutes_played INT           NOT NULL DEFAULT 0,
        goals_scored   INT           NOT NULL DEFAULT 0,
        received_cards NVARCHAR(10)  NOT NULL DEFAULT 'None',
        rated_position NVARCHAR(20)  NOT NULL,
        comments       NVARCHAR(MAX),
        created_at     DATETIME      NOT NULL DEFAULT GETDATE(),
        FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
    )
    """,
    """
    IF OBJECT_ID('players', 'U') IS NULL
    CREATE TABLE players (
        id             INT IDENTITY(1,1) PRIMARY KEY,
        user_id        INT           NOT NULL,
        name           NVARCHAR(100) NOT NULL,
        gender         NVARCHAR(10)  NOT NULL DEFAULT 'Male',
        team           NVARCHAR(100) NOT NULL DEFAULT '',
        position       NVARCHAR(10)  NOT NULL DEFAULT '',
        other_position NVARCHAR(10)  NOT NULL DEFAULT '',
        first_name     NVARCHAR(100) NOT NULL DEFAULT '',
        last_name      NVARCHAR(100) NOT NULL DEFAULT '',
        nationality    NVARCHAR(100) NOT NULL DEFAULT '',
        birthday       DATE NULL,
        height         INT NULL,
        weight         INT NULL,
        foot           NVARCHAR(10)  NOT NULL DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """,
    """
    IF OBJECT_ID('users', 'U') IS NULL
    CREATE TABLE users (
        id            INT IDENTITY(1,1) PRIMARY KEY,
        username      NVARCHAR(100) UNIQUE NOT NULL,
        name          NVARCHAR(100) NULL,
        surname       NVARCHAR(100) NULL,
        email         NVARCHAR(255) NULL,
        password_hash NVARCHAR(64)  NOT NULL,
        role          NVARCHAR(10)  NOT NULL DEFAULT 'SCOUT'
    )
    """,
]


def init_db(app):
    with app.app_context():
        db = get_db()
        # Create tables in dependency order (users first, then players, then reports)
        for stmt in reversed(_SCHEMA):
            db.execute(stmt.strip())
        db.commit()
