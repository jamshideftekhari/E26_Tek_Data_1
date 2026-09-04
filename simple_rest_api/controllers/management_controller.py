from flask import Blueprint, jsonify, request

from services import management_service

management_bp = Blueprint("management", __name__, url_prefix="/management")


@management_bp.post("/rooms")
def create_room():
    room = management_service.create_room(request.get_json())
    return jsonify(room), 201


@management_bp.get("/rooms")
def list_rooms():
    return jsonify(management_service.list_rooms())


@management_bp.post("/allocation/run")
def run_allocation():
    return jsonify(management_service.run_allocation())


@management_bp.get("/schedule")
def get_full_schedule():
    return jsonify(management_service.get_full_schedule())


@management_bp.get("/priorities-summary")
def get_priorities_summary():
    return jsonify(management_service.get_priorities_summary())
