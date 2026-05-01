from flask import render_template, request, redirect, url_for, session, flash
from app_instance import app
from db import get_db
from utils import hash_password, login_required, is_admin


@app.route("/admin/accounts")
@login_required
def admin_accounts():
    if not is_admin():
        flash("Admin access required.", "error")
        return redirect(url_for("dashboard"))

    users = get_db().execute(
        "SELECT u.id, u.username, u.name, u.surname, u.email, u.role, COUNT(p.id) AS player_count "
        "FROM users u LEFT JOIN players p ON p.user_id = u.id "
        "WHERE u.id <> ? "
        "GROUP BY u.id, u.username, u.name, u.surname, u.email, u.role "
        "ORDER BY u.username",
        (session["user_id"],)
    ).fetchall()
    return render_template("admin_accounts.html", users=users)


@app.route("/admin/accounts/add", methods=["GET", "POST"])
@login_required
def admin_add_account():
    if not is_admin():
        flash("Admin access required.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        name     = request.form.get("name", "").strip()
        surname  = request.form.get("surname", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")
        role     = request.form.get("role", "SCOUT")
        if role not in ("SCOUT", "ADMIN"):
            role = "SCOUT"

        if not username or not name or not surname or not email or not password:
            flash("All fields are required.", "error")
            return render_template("admin_add_account.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("admin_add_account.html")

        db = get_db()
        if db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
            flash("Username already taken.", "error")
            return render_template("admin_add_account.html")
        if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            flash("Email already used.", "error")
            return render_template("admin_add_account.html")

        db.execute(
            "INSERT INTO users (username, name, surname, email, password_hash, role) VALUES (?, ?, ?, ?, ?, ?)",
            (username, name, surname, email, hash_password(password), role)
        )
        db.commit()
        flash(f"Account '{username}' created.", "success")
        return redirect(url_for("admin_accounts"))

    return render_template("admin_add_account.html")


@app.route("/admin/accounts/<int:user_id>/role", methods=["POST"])
@login_required
def admin_update_account_role(user_id):
    if not is_admin():
        flash("Admin access required.", "error")
        return redirect(url_for("dashboard"))

    role = request.form.get("role", "SCOUT")
    if role not in ("SCOUT", "ADMIN"):
        flash("Invalid role selected.", "error")
        return redirect(url_for("admin_accounts"))
    if user_id == session["user_id"] and role != "ADMIN":
        flash("You cannot remove your own admin role.", "error")
        return redirect(url_for("admin_accounts"))

    db = get_db()
    user = db.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        flash("Account not found.", "error")
        return redirect(url_for("admin_accounts"))
    if user["username"].lower() == "admin":
        flash("The main admin account cannot be changed.", "error")
        return redirect(url_for("admin_accounts"))

    db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    db.commit()
    flash(f"Account '{user['username']}' role changed to {role}.", "success")
    return redirect(url_for("admin_accounts"))


@app.route("/admin/accounts/<int:user_id>/delete", methods=["POST"])
@login_required
def admin_delete_account(user_id):
    if not is_admin():
        flash("Admin access required.", "error")
        return redirect(url_for("dashboard"))
    if user_id == session["user_id"]:
        flash("You cannot delete your own admin account here.", "error")
        return redirect(url_for("admin_accounts"))

    db = get_db()
    user = db.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        flash("Account not found.", "error")
        return redirect(url_for("admin_accounts"))
    if user["username"].lower() == "admin":
        flash("The main admin account cannot be deleted.", "error")
        return redirect(url_for("admin_accounts"))

    db.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    flash(f"Account '{user['username']}' has been deleted.", "success")
    return redirect(url_for("admin_accounts"))
