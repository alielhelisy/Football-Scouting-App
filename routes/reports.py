from flask import render_template, request, redirect, url_for, session, flash
from app_instance import app
from db import get_db
from utils import login_required, is_admin, get_player_or_404
from models import (
    validate_stars, validate_non_negative_int, validate_cards, validate_position,
    POSITIONS, CARD_OPTIONS, RATING_OPTIONS, RATING_DESCRIPTIONS,
)


@app.route("/reports/create", methods=["GET", "POST"])
@login_required
def create_report():
    db = get_db()
    if is_admin():
        players = db.execute(
            "SELECT p.*, u.username as scout_name FROM players p "
            "JOIN users u ON p.user_id = u.id ORDER BY p.name"
        ).fetchall()
    else:
        players = db.execute(
            "SELECT p.*, u.username as scout_name FROM players p "
            "JOIN users u ON p.user_id = u.id WHERE p.user_id = ? ORDER BY p.name",
            (session["user_id"],)
        ).fetchall()

    if request.method == "POST":
        player_id = request.form.get("player_id", "")
        try:
            player_id = int(player_id)
            rating    = validate_stars(request.form.get("rating"))
            minutes   = validate_non_negative_int(request.form.get("minutes_played", 0), "Minutes Played")
            goals     = validate_non_negative_int(request.form.get("goals_scored", 0), "Goals Scored")
            cards     = validate_cards(request.form.get("received_cards", "None"))
            rated_pos = validate_position(request.form.get("rated_position", ""))
        except ValueError as e:
            flash(str(e), "error")
            return render_template("create_report.html", players=players,
                                   positions=POSITIONS, card_options=CARD_OPTIONS,
                                   rating_options=RATING_OPTIONS,
                                   rating_descriptions=RATING_DESCRIPTIONS)

        player = get_player_or_404(player_id)
        if not player:
            flash("Player not found.", "error")
            return render_template("create_report.html", players=players,
                                   positions=POSITIONS, card_options=CARD_OPTIONS,
                                   rating_options=RATING_OPTIONS,
                                   rating_descriptions=RATING_DESCRIPTIONS)

        comments = request.form.get("comments", "").strip()
        db.execute(
            "INSERT INTO reports "
            "(player_id, rating, minutes_played, goals_scored, received_cards, rated_position, comments) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (player_id, rating, minutes, goals, cards, rated_pos, comments)
        )
        db.commit()
        flash("Report saved.", "success")
        return redirect(url_for("player_detail", player_id=player_id))

    return render_template("create_report.html", players=players,
                           positions=POSITIONS, card_options=CARD_OPTIONS,
                           rating_options=RATING_OPTIONS,
                           rating_descriptions=RATING_DESCRIPTIONS)


@app.route("/players/<int:player_id>/edit_comment", methods=["GET", "POST"])
@login_required
def edit_comment(player_id):
    player = get_player_or_404(player_id)
    if not player:
        flash("Player not found.", "error")
        return redirect(url_for("dashboard"))

    db = get_db()
    latest = db.execute(
        "SELECT TOP 1 * FROM reports WHERE player_id = ? ORDER BY created_at DESC",
        (player_id,)
    ).fetchone()

    if not latest:
        flash("No report to edit yet.", "error")
        return redirect(url_for("players_by_position", pos_key=player["position"]))

    if request.method == "POST":
        new_comment = request.form.get("comment", "").strip()
        db.execute("UPDATE reports SET comments = ? WHERE id = ?", (new_comment, latest["id"]))
        db.commit()
        flash("Comment updated.", "success")
        return redirect(url_for("players_by_position", pos_key=player["position"]))

    return render_template("edit_comment.html", player=player, latest=latest,
                           pos_display=POSITIONS.get(player["position"], player["position"]))
