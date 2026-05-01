from flask import render_template, request, session
from app_instance import app
from db import get_db
from utils import login_required, is_admin
from models import compute_average_stars, POSITIONS, VALID_POSITIONS


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    results    = []
    selected   = []
    name_query = ""
    club_query = ""
    searched   = False

    if request.method == "POST":
        searched   = True
        name_query = request.form.get("name", "").strip()
        club_query = request.form.get("club", "").strip()
        selected   = [p.upper() for p in request.form.getlist("positions")
                      if p.upper() in VALID_POSITIONS]

        if selected or name_query or club_query:
            db = get_db()
            where  = []
            params = []

            if not is_admin():
                where.append("p.user_id = ?")
                params.append(session["user_id"])
            if selected:
                placeholders = ",".join("?" * len(selected))
                where.append(f"p.position IN ({placeholders})")
                params.extend(selected)
            if name_query:
                where.append("p.name LIKE ?")
                params.append(f"%{name_query}%")
            if club_query:
                where.append("p.team LIKE ?")
                params.append(f"%{club_query}%")

            where_sql = " AND ".join(where)
            rows = db.execute(
                f"SELECT p.*, u.username as scout_name FROM players p "
                f"JOIN users u ON p.user_id = u.id "
                f"WHERE {where_sql} ORDER BY p.name",
                params
            ).fetchall()

            for p in rows:
                last = db.execute(
                    "SELECT TOP 1 rating, comments FROM reports "
                    "WHERE player_id = ? ORDER BY created_at DESC",
                    (p["id"],)
                ).fetchone()
                all_rep = db.execute(
                    "SELECT rating FROM reports WHERE player_id = ?", (p["id"],)
                ).fetchall()
                avg = compute_average_stars(all_rep)
                rating = int(avg) if avg == int(avg) else avg
                results.append({
                    "id":          p["id"],
                    "name":        p["name"],
                    "club":        p["team"],
                    "position":    POSITIONS.get(p["position"], p["position"]),
                    "rating":      rating,
                    "last_review": last["comments"] if last and last["comments"] else "",
                    "last_by":     p["scout_name"],
                })

    return render_template("search.html", positions=POSITIONS, results=results,
                           selected=selected, name_query=name_query,
                           club_query=club_query, searched=searched)
