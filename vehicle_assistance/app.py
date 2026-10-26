from flask import Flask, render_template
import os


from modules.web_utils import generate_csrf_token
from modules.db_init import init_database, check_database, ensure_schema_updates
from routes.user_routes import register_user_routes
from routes.staff_routes import register_staff_routes
from routes.admin_routes import register_admin_routes  

app = Flask(__name__)
app.secret_key = os.environ.get ('SECRET_KEY','a-secure-dev-key')

# Initialize database
init_database()
ensure_schema_updates()

# CSRF token for templates
@app.context_processor
def inject_csrf_token():
    return {'csrf_token': generate_csrf_token()}

# Routes
@app.route('/')
def home():
    return render_template('home.html')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found!'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Server error!'), 500

# Register routes
register_user_routes(app)
register_staff_routes(app)
register_admin_routes(app)

# Run app (Render compatible)
if __name__ == '__main__':
    print('=' * 50)
    print('Vehicle Breakdown Assistance System')
    print('=' * 50)
    print('Server starting...')
    print('=' * 50)

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 10000))
    )