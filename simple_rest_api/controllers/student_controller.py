from flask import Blueprint, jsonify, request

from services import student_service

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.post("/students")
def create_student():
    student = student_service.create_student(request.get_json())
    return jsonify(student), 201


@student_bp.post("/students/<int:student_id>/priorities")
def submit_priorities(student_id):
    priorities = request.get_json().get("priorities", [])
    return jsonify(student_service.submit_priorities(student_id, priorities))


@student_bp.get("/students/<int:student_id>/schedule")
def get_student_schedule(student_id):
    return jsonify(student_service.get_student_schedule(student_id))
