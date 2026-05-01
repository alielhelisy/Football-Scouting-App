"""
Migration: adds new player fields and updates report ratings for half-point values.
Run once: python migrate.py
"""
from app import app
from db import get_db

MIGRATIONS = [
    "IF COL_LENGTH('users','name') IS NULL ALTER TABLE users ADD name NVARCHAR(100) NULL",
    "IF COL_LENGTH('users','surname') IS NULL ALTER TABLE users ADD surname NVARCHAR(100) NULL",
    "IF COL_LENGTH('users','email') IS NULL ALTER TABLE users ADD email NVARCHAR(255) NULL",
    "IF COL_LENGTH('players','gender')         IS NULL ALTER TABLE players ADD gender         NVARCHAR(10)  NOT NULL DEFAULT 'Male'",
    "IF COL_LENGTH('players','other_position')  IS NULL ALTER TABLE players ADD other_position NVARCHAR(10)  NOT NULL DEFAULT ''",
    "IF COL_LENGTH('players','first_name')      IS NULL ALTER TABLE players ADD first_name     NVARCHAR(100) NOT NULL DEFAULT ''",
    "IF COL_LENGTH('players','last_name')       IS NULL ALTER TABLE players ADD last_name      NVARCHAR(100) NOT NULL DEFAULT ''",
    "IF COL_LENGTH('players','nationality')     IS NULL ALTER TABLE players ADD nationality    NVARCHAR(100) NOT NULL DEFAULT ''",
    "IF COL_LENGTH('players','birthday')        IS NULL ALTER TABLE players ADD birthday       DATE NULL",
    "IF COL_LENGTH('players','height')          IS NULL ALTER TABLE players ADD height         INT NULL",
    "IF COL_LENGTH('players','weight')          IS NULL ALTER TABLE players ADD weight         INT NULL",
    "IF COL_LENGTH('players','foot')            IS NULL ALTER TABLE players ADD foot           NVARCHAR(10)  NOT NULL DEFAULT ''",
]

RATING_MIGRATIONS = [
    """
    DECLARE @constraint_name NVARCHAR(128);
    SELECT @constraint_name = cc.name
    FROM sys.check_constraints cc
    JOIN sys.columns c ON c.object_id = cc.parent_object_id AND c.column_id = cc.parent_column_id
    WHERE cc.parent_object_id = OBJECT_ID('reports') AND c.name = 'rating';
    IF @constraint_name IS NOT NULL
        EXEC('ALTER TABLE reports DROP CONSTRAINT ' + QUOTENAME(@constraint_name));
    """,
    "IF COL_LENGTH('reports','rating') IS NOT NULL ALTER TABLE reports ALTER COLUMN rating DECIMAL(2,1) NOT NULL",
    """
    IF OBJECT_ID('reports', 'U') IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_reports_rating_half_steps')
        ALTER TABLE reports ADD CONSTRAINT CK_reports_rating_half_steps
        CHECK (rating BETWEEN 1 AND 5 AND rating * 2 = FLOOR(rating * 2))
    """,
]

with app.app_context():
    db = get_db()
    for sql in MIGRATIONS + RATING_MIGRATIONS:
        db.execute(sql.strip())
    db.commit()
    print("Migration complete - player columns and half-point ratings are ready.")