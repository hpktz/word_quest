from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random

discover_bp = Blueprint('discover', __name__)

@discover_bp.route('/dashboard/discover')
@login_required
def discover():
    return render_template('dashboard/discover.html')