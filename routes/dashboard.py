"""
SMART ENTRY — Dashboard Routes
Admin home page and real-time summary stats.
"""
from flask import Blueprint, render_template, jsonify, flash, redirect, url_for
import os
import shutil
from config import Config
from flask_login import login_required
from database import database as db

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/admin")
@dashboard_bp.route("/admin/dashboard")
@login_required
def home():
    stats = {
        "today_visitors": db.get_todays_visitor_count(),
        "currently_inside": db.get_currently_inside_count(),
        "pending_alerts": db.count_unresolved_alerts(),
        "total_enrolled": db.count_students(),
    }
    recent_logs = db.get_recent_logs(limit=8)
    return render_template("admin/dashboard.html", stats=stats, recent_logs=recent_logs)


@dashboard_bp.route("/admin/stats/json")
@login_required
def stats_json():
    """AJAX endpoint — returns live summary stats for auto-refresh."""
    return jsonify({
        "today_visitors": db.get_todays_visitor_count(),
        "currently_inside": db.get_currently_inside_count(),
        "pending_alerts": db.count_unresolved_alerts(),
        "total_enrolled": db.count_students(),
    })


@dashboard_bp.route("/admin/system/reset", methods=["POST"])
@login_required
def system_reset():
    """Wipe all user data for testing."""
    # 1. DB Reset
    db.factory_reset()
    
    # 2. Delete face data
    if os.path.exists(Config.FACE_DATA_DIR):
        for item in os.listdir(Config.FACE_DATA_DIR):
            item_path = os.path.join(Config.FACE_DATA_DIR, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                
    # 3. Delete snapshots
    if os.path.exists(Config.ALERTS_SNAPSHOT_DIR):
        for item in os.listdir(Config.ALERTS_SNAPSHOT_DIR):
            item_path = os.path.join(Config.ALERTS_SNAPSHOT_DIR, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
                
    # 4. Delete model file
    if os.path.exists(Config.LBPH_MODEL_PATH):
        os.remove(Config.LBPH_MODEL_PATH)
        
    # 5. Clear memory cooldowns and reload blank model
    import routes.kiosk as kiosk_module
    kiosk_module._last_alert_time.clear()
    kiosk_module._last_unknown_face.clear()
    kiosk_module._last_recognized_time.clear()
    kiosk_module._reload_recognizer()
    
    flash("System data has been completely wiped for testing.", "success")
    return redirect(url_for("dashboard.home"))
