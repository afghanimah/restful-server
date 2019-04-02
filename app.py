from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

from app_base import Session
from user import User
from room import Room
from message import Message

app = Flask(__name__)
CORS(app)

#admin, admin
users = [
    User(0, "admin", "103ed64fd2ec3a053dd50bca44ddf7ed6cdeedf83963c44044b494ea69afa52e")
]

rooms = [
    Room(0, "Main Room", "Initial room you connect to.", 100, "admin")
]

messages = []

@app.route("/message", methods = ["POST"])
def send_message():
    session = Session()
    r = request.get_json(force=True)
    user = r.get("user")
    room_id = r.get("room_id")
    message = r.get("message")
    if message == None or message == "":
        session.close()
        return jsonify({"success": False})
    
    msg = Message(len(session.query(Message).all()), user, message, room_id, datetime.now())
    session.add(msg)
    session.commit()

    msgs = session.query(Message).filter(Message.room_id == room_id).all()
    msgs = [x.to_dict() for x in msgs]

    session.close()
    return jsonify({"messages": msgs})

@app.route("/rooms/enter", methods = ["POST"])
def enter_room():
    session = Session()
    r = request.get_json(force=True)
    user_id = r.get("user_id")
    room_id = r.get("room_id")

    r = session.query(Room).filter(Room.id == room_id).all()
    if len(r) == 0:
        session.close()
        return jsonify({"success": False})
    if len(r[0].users) >= r[0].space:
        session.close()
        return jsonify({"success": False})
    r[0].users.append(session.query(User).filter(User.id == user_id).all()[0])
    room = r[0].to_dict()
    session.commit()
    session.close()
    return jsonify({"room": room})

@app.route("/rooms/exit", methods = ["POST"])
def exit_room():
    session = Session()
    r = request.get_json(force=True)
    user_id = r.get("user_id")
    room_id = r.get("room_id")

    r = session.query(Room).filter(Room.id == room_id).all()
    if len(r) == 0:
        session.close()
        return jsonify({"success": False})
    if len(r[0].users) >= r[0].space:
        session.close()
        return jsonify({"success": False})
    r[0].users.remove(session.query(User).filter(User.id == user_id).all()[0])

    session.commit()
    session.close()
    return jsonify({"success": True})

@app.route("/rooms/<int:room_id>", methods = ["GET"])
def get_room(room_id):
    session = Session()
    r = session.query(Room).filter(Room.id == room_id).all()
    if len(r) == 0:
        session.close()
        return jsonify({"room": None})
    room = r[0].to_dict()
    session.close()
    return jsonify({"room": room})

@app.route("/register", methods = ["PUT"])
def register():
    session = Session()
    r = request.get_json(force=True)
    un = r.get("username")
    pw = r.get("password")

    u = session.query(User).filter(User.name == un).all()
    if len(u) > 0:
        session.close()
        return jsonify({"success": False})
    
    u = User(len(session.query(User).all()),un, pw)
    session.add(u)
    user = u.to_dict()
    session.commit()
    session.close()
    return jsonify({"success": True, "user": user})

@app.route("/login", methods = ["POST"])
def login():
    session = Session()
    r = request.get_json(force=True)
    un = r.get("username")
    pw = r.get("password")

    u = session.query(User).filter(User.name == un and User.password == pw).all()
    if len(u) == 0:
        session.close()
        return jsonify({"success": False})
    user = u[0].to_dict()
    session.close()
    return jsonify({"success": True, "user": user})

@app.route("/connect", methods = ["POST"])
def connect():
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)