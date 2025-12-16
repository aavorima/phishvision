from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv
from database import db

load_dotenv()

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///phishvision.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# CORS configuration - allow browser extensions and frontend
CORS(app,
     supports_credentials=True,
     origins=[
         "http://localhost:3000",
         "http://127.0.0.1:3000",
         "chrome-extension://*",
         "moz-extension://*"
     ],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
db.init_app(app)

# Import models first
import models

# Import and register blueprints
from routes import campaign_routes, analyzer_routes, tracking_routes, dashboard_routes, template_routes, soc_routes, risk_routes, employee_routes, landing_routes, qrcode_routes, sms_routes, auth_routes, settings_routes, extension_routes, feedback_routes, threat_feed_routes, vulnerability_routes, program_routes, hvs_routes, campaign_report_routes

app.register_blueprint(campaign_routes.bp)
app.register_blueprint(analyzer_routes.bp)
app.register_blueprint(tracking_routes.bp)
app.register_blueprint(dashboard_routes.bp)
app.register_blueprint(template_routes.bp)
app.register_blueprint(soc_routes.bp)
app.register_blueprint(risk_routes.bp)
app.register_blueprint(employee_routes.bp)
app.register_blueprint(landing_routes.bp)  # Credential harvesting landing pages
app.register_blueprint(qrcode_routes.bp)   # QR code phishing (quishing)
app.register_blueprint(sms_routes.bp)      # SMS phishing (smishing)
app.register_blueprint(auth_routes.bp)     # Authentication routes
app.register_blueprint(settings_routes.bp) # Settings routes
app.register_blueprint(extension_routes.bp) # Browser extension API
app.register_blueprint(feedback_routes.bp)  # Feedback and learning API
app.register_blueprint(threat_feed_routes.bp)  # Community Threat Intelligence feed
app.register_blueprint(vulnerability_routes.bp)  # Vulnerability profiling API
app.register_blueprint(program_routes.bp)  # Campaign program management API
app.register_blueprint(hvs_routes.bp)      # Human Vulnerability Score (HVS) API
app.register_blueprint(campaign_report_routes.bp)  # Campaign Awareness Reports API

@app.route('/')
def index():
    return jsonify({
        'name': 'PhishVision API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
