import os
from flask import Flask, session
from flask_wtf.csrf import CSRFProtect

from src.database import init_database, seed_all

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
csrf = CSRFProtect(app)


def initialize_database():
    try:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("WARNING: DATABASE_URL not set. Database features will be unavailable.")
            return False
        init_database()
        seed_all()
        return True
    except Exception as e:
        print(f"WARNING: Database initialization failed: {e}")
        return False


db_initialized = initialize_database()


@app.context_processor
def inject_company_resources():
    if 'player_id' in session:
        try:
            from src.company_resources import get_company_resources
            resources = get_company_resources(session['player_id'])
            return {'company_resources': resources}
        except Exception:
            pass
    return {'company_resources': None}


from src.routes.auth import auth_bp
from src.routes.core import core_bp
from src.routes.scenarios import scenarios_bp
from src.routes.inventory import inventory_bp
from src.routes.social import social_bp
from src.routes.api import api_bp
from src.routes.finance import finance_bp

app.register_blueprint(auth_bp)
app.register_blueprint(core_bp)
app.register_blueprint(scenarios_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(social_bp)
app.register_blueprint(api_bp)
app.register_blueprint(finance_bp)


@app.after_request
def add_cache_control(response):
    if 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
