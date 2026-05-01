import os
from flask import Flask

app = Flask(__name__)
app.secret_key = os.environ.get("SCOUTING_SECRET_KEY", "dev-secret-key-change-me")
