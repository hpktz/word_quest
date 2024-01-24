from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import logging as logging
from datetime import datetime, timedelta
import locale

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

user_data_bp = Blueprint('user_data', __name__)

@user_data_bp.route('/dashboard/profile')
@login_required
def user_profile():
    return render_template('dashboard/profile.html')

@user_data_bp.route('/dashboard/profile/<int:user_id>')
@login_required
def users_profile(user_id):
    pass