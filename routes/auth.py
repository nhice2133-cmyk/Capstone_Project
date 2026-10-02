"""
SMART ENTRY — Auth Routes
Handles admin login and logout using Flask-Login + Flask-Bcrypt.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from database.database import get_admin_by_username

auth_bp = Blueprint("auth", __name__)


class AdminUser(UserMixin):
    """Minimal Flask-Login User wrapper for admin accounts."""

    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from app import bcrypt  # imported here to avoid circular imports
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin_row = get_admin_by_username(username)
        if admin_row and bcrypt.check_password_hash(admin_row["password_hash"], password):
            login_user(AdminUser(admin_row), remember=False)
            return redirect(url_for("dashboard.home"))
        flash("Invalid username or password.", "error")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    from app import bcrypt  # imported here to avoid circular imports
    from database.database import get_admin_by_id, update_admin_password

    if request.method == "POST":
        current_pw = request.form.get("current_password", "")
        new_pw = request.form.get("new_password", "")
        confirm_pw = request.form.get("confirm_password", "")

        admin_row = get_admin_by_id(current_user.id)

        if not admin_row:
            flash("Admin account not found.", "error")
            return redirect(url_for("auth.change_password"))

        if not bcrypt.check_password_hash(admin_row["password_hash"], current_pw):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("auth.change_password"))

        if len(new_pw) < 6:
            flash("New password must be at least 6 characters.", "error")
            return redirect(url_for("auth.change_password"))

        if new_pw != confirm_pw:
            flash("New passwords do not match.", "error")
            return redirect(url_for("auth.change_password"))

        if current_pw == new_pw:
            flash("New password must be different from the current one.", "error")
            return redirect(url_for("auth.change_password"))

        new_hash = bcrypt.generate_password_hash(new_pw).decode("utf-8")
        update_admin_password(current_user.id, new_hash)
        flash("Password changed successfully!", "success")
        return redirect(url_for("dashboard.home"))

    return render_template("admin/change_password.html")
