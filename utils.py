"""
Shared helpers used across all route modules.
"""
import hashlib
from functools import wraps
from flask import session, redirect, url_for
from db import get_db


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def is_admin() -> bool:
    return session.get("role") == "ADMIN"


def get_player_or_404(player_id):
    if is_admin():
        return get_db().execute(
            "SELECT p.*, u.username as scout_name FROM players p "
            "JOIN users u ON p.user_id = u.id WHERE p.id = ?",
            (player_id,)
        ).fetchone()
    return get_db().execute(
        "SELECT p.*, u.username as scout_name FROM players p "
        "JOIN users u ON p.user_id = u.id WHERE p.id = ? AND p.user_id = ?",
        (player_id, session["user_id"])
    ).fetchone()
