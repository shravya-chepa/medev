from flask import Blueprint, render_template

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')
