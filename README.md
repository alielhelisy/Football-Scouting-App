# Software Engineering Final Project

**Student 1:** Ali Elhelisy | **ID:** 220303928  
**Student 2:** Mazen Mohamed | **ID:** 220303940
---

## Project Overview

A multi-user Flask web application for football scouts to manage players and create match reports. Each scout manages their own private list of players organised by position. An Admin role can view and manage all scouts' data.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.14 + Flask |
| Database | Microsoft SQL Server 2022 (SQLEXPRESS) |
| DB Driver | pyodbc + ODBC Driver 17 for SQL Server |
| Frontend | Jinja2 HTML templates + plain CSS |
| Testing | pytest |

---

## Project Structure

```
scouting_app/
├── app.py                        ← Entry point (registers all route modules)
├── app_instance.py               ← Flask app object
├── utils.py                      ← Shared helpers (login_required, is_admin, etc.)
├── models.py                     ← Business logic (pure, testable)
├── db.py                         ← SQL Server connection + wrapper
├── routes/
│   ├── auth.py                   ← register, login, logout, account
│   ├── admin.py                  ← admin account management
│   ├── players.py                ← dashboard, player CRUD, detail
│   ├── reports.py                ← create report, edit comment
│   └── search.py                 ← multi-position search
├── static/
│   └── style.css                 ← All styling
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html            ← Tactical pitch board
│   ├── players_by_position.html  ← Player table + action bar
│   ├── add_player.html
│   ├── edit_player.html
│   ├── player_detail.html        ← Report history + player bio
│   ├── create_report.html
│   ├── edit_comment.html
│   ├── search.html
│   ├── account_info.html
│   ├── admin_accounts.html
│   └── admin_add_account.html
└── tests/
    └── test_logic.py             ← Unit tests (business logic only)
```

---

## Database Schema

```sql
users
  id            INT IDENTITY PK
  username      NVARCHAR(100) UNIQUE
  password_hash NVARCHAR(64)
  role          NVARCHAR(10)   -- 'SCOUT' or 'ADMIN'

players
  id             INT IDENTITY PK
  user_id        INT FK -> users.id
  name           NVARCHAR(100)
  gender         NVARCHAR(10)
  team           NVARCHAR(100)
  position       NVARCHAR(10)   -- GK | CB | FB | 6ER | 8ER | WIDE | CF
  other_position NVARCHAR(10)
  first_name     NVARCHAR(100)
  last_name      NVARCHAR(100)
  nationality    NVARCHAR(100)
  birthday       DATE
  height         INT
  weight         INT
  foot           NVARCHAR(10)   -- Right | Left | Both

reports
  id             INT IDENTITY PK
  player_id      INT FK -> players.id  ON DELETE CASCADE
  rating         INT (1-5)
  minutes_played INT
  goals_scored   INT
  received_cards NVARCHAR(10)   -- None | Yellow | Red
  rated_position NVARCHAR(10)
  comments       NVARCHAR(MAX)
  created_at     DATETIME DEFAULT GETDATE()
```

---

## Positions

| Key | Display |
|---|---|
| GK | Goalkeeper |
| CB | Center Back |
| FB | Full Back |
| 6ER | 6er (Defensive Mid) |
| 8ER | 8er (Box-to-Box Mid) |
| WIDE | Wide Player |
| CF | Center Forward |

---

## Features

### Authentication
- Register / Login / Logout with sessions and cookies
- Delete own account (removes all player and report data)

### Scout Role
- Dashboard shows a tactical pitch board with player cards per position
- Click a position to see all own players in a table
- Row selection with action bar: Add Player, Edit, Delete, Details, Edit Comment
- Add / Edit Player — Display Name, Gender, Main Position, Other Position, Team, plus optional fields (First Name, Last Name, Nationality, Birthday, Height, Weight, Foot)
- Delete — removes player and all linked reports (ON DELETE CASCADE)
- Details — full report history + player bio card
- Create Report — Rating (1-5), Minutes Played, Goals Scored, Received Cards, Rated Position, Comments
- Edit Comment — update the latest report's comment
- Search — filter by name, club, and/or multiple positions

### Admin Role
- Sees ALL players from ALL scouts
- Extra Scout column in player tables
- Create Report dropdown shows all players with scout names
- Account management: add scouts, change roles, delete accounts

---

## User Stories

| ID | Story | Acceptance Criteria |
|---|---|---|
| US1 | As a scout, I want to add a player with their name, team, and position so I can track prospects | Player appears on the dashboard in the correct position; empty name shows an error |
| US2 | As a scout, I want to create a match report for a player so I can record what I observed | Report saved with all fields; visible in the Details page |
| US3 | As a scout, I want to see a player's average rating across all reports so I can assess their level | Average displayed on the player detail page |
| US4 | As a scout, I want to filter players by position so I can quickly find who I need | Only players matching the selected position are shown |
| US5 | As a scout, I want to edit or delete a player so I can keep my data accurate | Updates reflect immediately; deletion removes player and all reports |

---

## Business Logic (models.py)

| Function | Description |
|---|---|
| validate_player_name | Not empty, max 100 chars |
| validate_team | Strips whitespace, max 100 chars |
| validate_position | Must be one of the 7 valid position keys, or empty string |
| validate_stars | Integer between 1 and 5 |
| validate_non_negative_int | Number >= 0 (minutes, goals) |
| validate_cards | None, Yellow, or Red only |
| compute_average_stars | Average of report ratings |
| filter_players_by_position | Filter player list by position key |
| stars_display | Convert float average to star string |

---

## Unit Tests (tests/test_logic.py)

Tests cover business logic only — no routes, no database, no Flask context.

### What is tested

| Group | Tests |
|---|---|
| validate_player_name | valid name, empty raises, whitespace-only raises, too long raises |
| validate_team | strips whitespace, empty returns empty, None returns empty |
| validate_position | all 7 valid keys, lowercase accepted, invalid raises, empty allowed |
| validate_stars | 1-5 valid, 0 raises, 6 raises, string number, non-numeric raises |
| validate_non_negative_int | valid, zero valid, negative raises, string number, non-numeric raises |
| validate_cards | None/Yellow/Red valid, invalid raises |
| compute_average_stars | single, multiple, empty list, decimal |
| filter_players_by_position | correct filter, empty returns all, no match, case insensitive |
| stars_display | full stars, empty stars, partial, rounding |

### Run Tests

```
cd "D:\Ali\University\4th Semester\Software Engineering\Project\scouting_app"
pytest tests/test_logic.py -v
```

---

## Setup

### Step 1 — Install dependencies

```
pip install flask pyodbc pytest
```

### Step 2 — Create the database (one time only)

Open SSMS, connect to `localhost\SQLEXPRESS`, then run:

```sql
CREATE DATABASE ScoutingApp;
```

### Step 3 — Run the app

```
cd /d "D:\Ali\University\4th Semester\Software Engineering\Project\scouting_app"
```

```
python app.py
```

Open browser at: http://127.0.0.1:5000

---

## Reset Database

Run in SSMS if you need a clean slate:

```sql
USE ScoutingApp;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS users;
```

Then restart the app — tables recreate automatically.

---

## SQL Server Connection Details

| Setting | Value |
|---|---|
| Server | localhost\SQLEXPRESS |
| Database | ScoutingApp |
| Driver | ODBC Driver 17 for SQL Server |
| Authentication | Windows Authentication |

---

## Git Commit Convention

All commits reference the related user story ID:

```
Add player form with name, team, position [US1]
Create report form with full match stats [US2]
Compute average rating from reports [US3]
Position filter on players list [US4]
Edit and delete player functionality [US5]
```

---

## Grading Checklist

- [x] Flask web application
- [x] Register, Login, Logout with sessions and cookies
- [x] Multi-user — each scout sees only their own data
- [x] Full CRUD on Players entity
- [x] Raw SQL only, no ORM
- [x] 3 tables: users, players, reports — linked via user_id
- [x] Admin role sees all data across all scouts
- [x] Unit tests on business logic only (no routes tested)
- [x] GitHub Projects Kanban with user stories US1–US5
- [x] Git commits referencing user story IDs
