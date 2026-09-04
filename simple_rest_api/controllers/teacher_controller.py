from flask import Blueprint, jsonify, request

from services import teacher_service

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.post("/courses")
def create_course():
    course = teacher_service.create_course(request.get_json())
    return jsonify(course), 201


@teacher_bp.get("/courses")
def list_courses():
    return jsonify(teacher_service.list_courses())


@teacher_bp.get("/courses/<int:course_id>/schedule")
def get_course_schedule(course_id):
    return jsonify(teacher_service.get_course_schedule(course_id))


@teacher_bp.get("/courses/<int:course_id>/class-list")
def get_class_list(course_id):
    return jsonify(teacher_service.get_class_list(course_id))
