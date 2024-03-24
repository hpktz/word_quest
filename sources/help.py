from flask import Blueprint, render_template, redirect, url_for, jsonify, request, session, abort
from flask_login import login_user, login_required, logout_user, current_user
from root import *
import random as random
import logging as logging
from datetime import datetime, timedelta
import locale

help_bp = Blueprint('help', __name__)

@help_bp.route('/dashboard/help')
def index():
    return render_template('help/menu.html')

@help_bp.route('/dashboard/help/create')
def create():
    return render_template('help/create.html')

@help_bp.route('/dashboard/help/discover')
def discover():
    return render_template('help/discover.html')

@help_bp.route('/dashboard/help/play')
def games():
    return render_template('help/play.html')

@help_bp.route('/dashboard/help/quests')
def quests():
    return render_template('help/quests.html')

@help_bp.route('/dashboard/help/profile')
def profile():
    return render_template('help/profile.html')