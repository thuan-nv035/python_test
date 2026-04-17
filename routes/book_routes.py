import threading
import time

from flask import Blueprint, request, jsonify, Flask
from sqlalchemy.exc import SQLAlchemyError

from models import db, Seat

book_bp = Blueprint('book_bp', __name__)


@book_bp.route('/book', methods=['POST'])
def book_seat():
    data = request.get_json()
    seat_id = data.get('seat_id')
    user_id = data.get('user_id')

    try:
        seat = db.session.query(Seat).filter(Seat.id == seat_id).with_for_update().first()
        print('seat', seat)
        if not seat:
            return jsonify({'error': 'Ghe khong ton tai'}), 404

        if seat.is_booked:
            return jsonify({'error': 'ghe nay da co nguoi day roi'}), 400

        seat.is_booked = True
        seat.user_id = user_id

        db.session.commit()
        return jsonify({'message': f'dat ghe {seat.seat_code} thanh cong!'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Loi he thong, vui long thu lai'}), 500


def release_seat_after_timeout(app, seat_id):
    with app.app_context():
        time.sleep(30)  # Giữ ghế trong 30 giây để test
        seat = Seat.query.get(seat_id)
        if seat and seat.status == 'reserved':
            seat.status = 'available'
            seat.user_id = None
            db.session.commit()
            print(f"--- Ghế {seat.seat_code} đã tự động giải phóng do hết hạn! ---")


app = Flask(__name__)


@book_bp.route('/reserve', methods=['POST'])
def reserve_seat(release_seat_task=None):
    data = request.get_json()
    seat_id = data.get('seat_id')
    user_id = data.get('user_id')

    seat = db.session.query(Seat).filter(Seat.id == seat_id).with_for_update().first()

    if not seat or seat.status != 'availabe':
        return jsonify({'error': 'Ghe khong san sang'}), 400

    seat.status = 'reserve'
    seat.user_id = user_id
    db.session.commit()

    release_seat_task.apply_async(args=[seat_id], countdown=30)
    return jsonify({'message': 'Ghe da duoc giu trong 30s. Hay thanh toan'})
