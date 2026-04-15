from flask import Blueprint, render_template, request, jsonify

from models import Score, db

game_bp = Blueprint('game_bp', __name__)


@game_bp.route('')
def game_snake():
    return render_template('snake.html')


@game_bp.route('/save-score', methods=['POST'])
def save_score():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    new_score = Score(username="Người chơi", points=data['score'])
    db.session.add(new_score)
    db.session.commit()
    return jsonify({"status": "success"})


@game_bp.route('/get-score')
def get_score():
    top_score = Score.query.order_by(Score.points.desc()).first()
    if top_score:
        return jsonify({"username": top_score.username, "points": top_score.points})
    return jsonify({"points": 0})  # Sửa lỗi trả về None bạn gặp lúc nãy
