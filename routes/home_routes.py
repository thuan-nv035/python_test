from flask import Blueprint, render_template

home_bp = Blueprint('home_bp', __name__)


@home_bp.route('')
def home():
    return 'chao mung den voi trang chu'


@home_bp.route('/who-is-milion')
def who_is_milion():
    return render_template('who_is_million..html')
