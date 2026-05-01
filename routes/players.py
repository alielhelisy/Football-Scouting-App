from flask import render_template, request, redirect, url_for, session, flash
from app_instance import app
from db import get_db
from utils import login_required, is_admin, get_player_or_404
from models import (
    validate_player_name, validate_team,
    compute_average_stars, stars_display,
    POSITIONS, VALID_POSITIONS, FOOT_OPTIONS, GENDER_OPTIONS,
)


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    if is_admin():
        rows = db.execute(
            "SELECT p.*, u.username as scout_name FROM players p "
            "JOIN users u ON p.user_id = u.id ORDER BY p.position, p.name"
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT p.*, u.username as scout_name FROM players p "
            "JOIN users u ON p.user_id = u.id "
            "WHERE p.user_id = ? ORDER BY p.position, p.name",
            (session["user_id"],)
        ).fetchall()

    by_pos = {k: [] for k in POSITIONS}
    for p in rows:
        pos = (p["position"] or "").upper()
        if pos in by_pos:
            by_pos[pos].append(p)

    return render_template("dashboard.html", positions=POSITIONS, by_pos=by_pos,
                           admin=is_admin())


@app.route("/positions/<pos_key>")
@login_required
def players_by_position(pos_key):
    pos_key = pos_key.upper()
    if pos_key not in VALID_POSITIONS:
        flash("Invalid position.", "error")
        return redirect(url_for("dashboard"))

    db = get_db()
    if is_admin():
        rows = db.execute(
            "SELECT p.*, u.username as scout_name FROM players p "
            "JOIN users u ON p.user_id = u.id WHERE p.position = ? ORDER BY p.name",
            (pos_key,)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT p.*, u.username as scout_name FROM players p "
            "JOIN users u ON p.user_id = u.id "
            "WHERE p.user_id = ? AND p.position = ? ORDER BY p.name",
            (session["user_id"], pos_key)
        ).fetchall()

    players = []
    for p in rows:
        last = db.execute(
            "SELECT TOP 1 comments FROM reports WHERE player_id = ? ORDER BY created_at DESC",
            (p["id"],)
        ).fetchone()
        players.append({
            "id":          p["id"],
            "name":        p["name"],
            "position":    p["position"],
            "scout_name":  p["scout_name"],
            "last_review": last["comments"] if last and last["comments"] else "",
        })

    return render_template(
        "players_by_position.html",
        players=players,
        pos_key=pos_key,
        pos_display=POSITIONS[pos_key],
        admin=is_admin(),
    )


@app.route("/players/add", methods=["GET", "POST"])
@login_required
def add_player():
    preset_pos = request.args.get("position", "").upper()
    if request.method == "POST":
        try:
            name = validate_player_name(request.form.get("name", ""))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("add_player.html", positions=POSITIONS,
                                   foot_options=FOOT_OPTIONS, gender_options=GENDER_OPTIONS,
                                   preset_pos=preset_pos)

        position       = request.form.get("position", "").upper()
        other_position = request.form.get("other_position", "").upper()
        gender         = request.form.get("gender", "Male")
        team           = validate_team(request.form.get("team", ""))
        first_name     = request.form.get("first_name", "").strip()
        last_name      = request.form.get("last_name", "").strip()
        nationality    = request.form.get("nationality", "").strip()
        birthday       = request.form.get("birthday", "") or None
        foot           = request.form.get("foot", "")
        try:
            height = int(request.form.get("height") or 0) or None
            weight = int(request.form.get("weight") or 0) or None
        except ValueError:
            height = weight = None

        db = get_db()
        db.execute(
            "INSERT INTO players "
            "(user_id, name, gender, team, position, other_position, "
            " first_name, last_name, nationality, birthday, height, weight, foot) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (session["user_id"], name, gender, team, position, other_position,
             first_name, last_name, nationality, birthday, height, weight, foot)
        )
        db.commit()
        flash(f"Player '{name}' created.", "success")
        redirect_pos = position if position in VALID_POSITIONS else list(POSITIONS.keys())[0]
        return redirect(url_for("players_by_position", pos_key=redirect_pos))

    return render_template("add_player.html", positions=POSITIONS,
                           foot_options=FOOT_OPTIONS, gender_options=GENDER_OPTIONS,
                           preset_pos=preset_pos)


@app.route("/players/<int:player_id>/edit", methods=["GET", "POST"])
@login_required
def edit_player(player_id):
    player = get_player_or_404(player_id)
    if not player:
        flash("Player not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        try:
            name = validate_player_name(request.form.get("name", ""))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("edit_player.html", player=player, positions=POSITIONS,
                                   foot_options=FOOT_OPTIONS, gender_options=GENDER_OPTIONS)

        position       = request.form.get("position", "").upper()
        other_position = request.form.get("other_position", "").upper()
        gender         = request.form.get("gender", "Male")
        team           = validate_team(request.form.get("team", ""))
        first_name     = request.form.get("first_name", "").strip()
        last_name      = request.form.get("last_name", "").strip()
        nationality    = request.form.get("nationality", "").strip()
        birthday       = request.form.get("birthday", "") or None
        foot           = request.form.get("foot", "")
        try:
            height = int(request.form.get("height") or 0) or None
            weight = int(request.form.get("weight") or 0) or None
        except ValueError:
            height = weight = None

        db = get_db()
        db.execute(
            "UPDATE players SET name=?, gender=?, team=?, position=?, other_position=?, "
            "first_name=?, last_name=?, nationality=?, birthday=?, height=?, weight=?, foot=? "
            "WHERE id=? AND user_id=?",
            (name, gender, team, position, other_position, first_name, last_name,
             nationality, birthday, height, weight, player_id, session["user_id"])
        )
        db.commit()
        flash("Player updated.", "success")
        redirect_pos = position if position in VALID_POSITIONS else list(POSITIONS.keys())[0]
        return redirect(url_for("players_by_position", pos_key=redirect_pos))

    return render_template("edit_player.html", player=player, positions=POSITIONS,
                           foot_options=FOOT_OPTIONS, gender_options=GENDER_OPTIONS)


@app.route("/players/<int:player_id>/delete", methods=["POST"])
@login_required
def delete_player(player_id):
    player = get_player_or_404(player_id)
    if not player:
        flash("Player not found.", "error")
        return redirect(url_for("dashboard"))
    get_db().execute("DELETE FROM players WHERE id = ?", (player_id,))
    get_db().commit()
    flash(f"Player '{player['name']}' deleted.", "success")
    pos = player["position"] if player["position"] in VALID_POSITIONS else list(POSITIONS.keys())[0]
    return redirect(url_for("players_by_position", pos_key=pos))


@app.route("/players/<int:player_id>")
@login_required
def player_detail(player_id):
    player = get_player_or_404(player_id)
    if not player:
        flash("Player not found.", "error")
        return redirect(url_for("dashboard"))

    db = get_db()
    reports = db.execute(
        "SELECT * FROM reports WHERE player_id = ? ORDER BY created_at DESC",
        (player_id,)
    ).fetchall()
    avg = compute_average_stars(reports)

    return render_template(
        "player_detail.html",
        player=player,
        pos_display=POSITIONS.get(player["position"], player["position"]),
        reports=reports,
        avg_stars=avg,
        stars_str=stars_display(avg),
        positions=POSITIONS,
        admin=is_admin(),
    )


@app.route("/players/<int:player_id>/reports/<int:report_id>/delete", methods=["POST"])
@login_required
def delete_report(player_id, report_id):
    player = get_player_or_404(player_id)
    if not player:
        flash("Player not found.", "error")
        return redirect(url_for("dashboard"))
    get_db().execute("DELETE FROM reports WHERE id = ? AND player_id = ?", (report_id, player_id))
    get_db().commit()
    flash("Report deleted.", "success")
    return redirect(url_for("player_detail", player_id=player_id))
