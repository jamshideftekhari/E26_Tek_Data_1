from models import room_model
from services import allocation_service


def create_room(data):
    return room_model.create_room(
        name=data["name"], capacity=data["capacity"], time_slot=data["time_slot"]
    )


def list_rooms():
    return room_model.get_all_rooms()


def run_allocation():
    return allocation_service.run_allocation()


def get_full_schedule():
    return allocation_service.get_full_schedule()


def get_priorities_summary():
    return allocation_service.priorities_summary()
