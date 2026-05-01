from app_instance import app
from db import close_db, init_db

# Register all route modules
import routes.auth
import routes.admin
import routes.players
import routes.reports
import routes.search

app.teardown_appcontext(close_db)

if __name__ == "__main__":
    init_db(app)
    app.run(debug=True)
