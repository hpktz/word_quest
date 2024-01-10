from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random

quests_bp = Blueprint('quests', __name__)

@quests_bp.route('/dashboard/quests')
@login_required
def quests():
    return render_template('dashboard/quests.html')
