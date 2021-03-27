import jwt
from bson.objectid import ObjectId
from general import db
from flask import jsonify
import json


def generate_token(username, role, create_time):
    return jwt.encode({"username": username, "role": role, "time": create_time}, "secret", algorithm="HS256")


def token_decode(token):
    return jwt.decode(token, key="secret", algorithms="HS256")


def response(note, data, status):
    f = j_load()
    f["note"] = note
    f["data"] = data
    response = jsonify(f)
    response.status_code = status
    return response


def check_user(username):
    col = db()["Users"]
    doc = col.find_one({"username": username})
    if doc:
        return True
    else:
        return False


def check_token(token):
    var = jwt.decode(token,  key="secret", algorithm="HS256")
    return var


def check_list_exist(username, list_name):
    col = db()["Lists"]
    if col.find_one({"username": username, "list_name": list_name}):
        return True
    else:
        return False


def encode_password(param):
    return jwt.encode({"password": param}, key="password", algorithm="HS256")


def j_load():
    with open("temp.json", "r") as j_file:
        return json.load(j_file)


def token_generator(username, role, create_time):
    return jwt.encode({"username": username, "role": role, "time": create_time},  key="secret",
                      algorithm="HS256")


def session_to_json(param):
    return {
        "id": ObjectId(param["_id"]).__str__(),
        "username": param["username"],
        "token": param["token"]
    }


def list_to_json(param):
    return {
        "id": ObjectId(param["_id"]).__str__(),
        "username": param["username"],
        "list_name": param["list_name"],
    }


def todo_to_json(param):
    return {
        "id": ObjectId(param["_id"]).__str__(),
        "username": param["username"],
        "list_name": param["list_name"],
        "title": param["title"],
        "status": param["status"],
    }


def create_user(username, password, name, req_time):
    col = db()["Users"]
    data = {"username": username, "password": encode_password(password), "name": name,
            "created_at": req_time, "role": "guest"}
    x = col.insert_one(data)
    y = create_session(username, req_time)
    if x and y:
        return y
    else:
        return False


def check_permission(role, module, method):
    col = db()["Roles"]
    doc = col.find_one({"role": role, "module": module})
    if method in doc["methods"]:
        return True
    else:
        return False


def create_session(username, login_time):
    token = token_generator(username=username, role="guest", create_time=login_time)
    col1 = db()["Session"]
    create_device = col1.insert_one({"time": login_time, "username": username, "token": token})
    if create_device:
        return token
    else:
        return False


def find_by_id(collection, _id):
    return db()[collection].find_one({"_id": ObjectId(_id)})


def login(params, login_time):
    if params["username"] and params["password"]:
        col = db()["Users"]
        user = col.find_one({"username": params["username"], "password": encode_password(params["password"])})
        if user:
            c = create_session(params["username"], login_time)
            if c:
                return c
        else:
            return False
    else:
        return False


class error():
    def bad_request(self):
        return response("Bad Request.", "", 400)

    def not_found(self):
        return response("Not Found.", "", 404)

    def unauthorized(self):
        return response("Permission Denied.", "", 401)

    def forbidden(self):
        return response("Forbidden.", "", 403)

    def payment_required(self):
        return response("Payment Required.", "",402)
