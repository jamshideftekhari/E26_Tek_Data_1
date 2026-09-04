from flask import Flask, jsonify

from config import PORT
from controllers.management_controller import management_bp
from controllers.student_controller import student_bp
from controllers.teacher_controller import teacher_bp
from services.errors import NotFoundError


def create_app():
    app = Flask(__name__)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(management_bp)

    @app.errorhandler(NotFoundError)
    def handle_not_found(error):
        return jsonify({"error": str(error)}), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
