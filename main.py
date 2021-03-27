from flask_restful import Resource, Api
from flask import Flask, request
from bson.objectid import ObjectId
import time
from general import db
import function

app = Flask(__name__)
api = Api(app)


class Register(Resource):

    def post(self):
        try:
            sys_time = time.time()
            if request.json["username"] and request.json["password"] and request.json["name"]:
                if not function.check_user(request.json["username"]):
                    create_user = function.create_user(request.json["username"], request.json["password"],
                                                       request.json["name"], sys_time.__str__())
                    if create_user:
                        data = {"token": create_user}
                        return function.response("User Success Created.", data, 200)
                else:
                    return function.error.not_found(self)
            else:
                return function.error.bad_request(self)
        except():
            return function.error.bad_request(self)


class Login(Resource):
    def get(self):
        return time.time()

    def post(self):
        created_times = time.time().__str__()
        login = function.login(request.json, created_times)
        if login:
            token = {"token": login}
            return function.response("Login Success.", token, 200)
        else:
            return function.error.not_found(self)


class Todo(Resource):
    def get(self):
        try:
            if request.json["token"] and request.json["list_name"]:
                token_data = function.token_decode(request.json["token"])
                if function.check_permission(token_data["role"], "todo", "get"):
                    col = db()["Todo"]
                    u_list = col.find({"username": token_data["username"], "list_name": request.json["list_name"]})
                    data = []
                    for li in u_list:
                        data.append(function.todo_to_json(li))
                    lists = {"lists": data}
                    return function.response("Success.", lists, 200)
        except:
            return function.error.bad_request(self)

    def post(self):
        try:
            if request.json["token"] and request.json["list_name"] and request.json["title"]:
                token_data = function.token_decode(request.json["token"])
                if function.check_permission(token_data["role"], "todo", "post"):
                    if function.check_list_exist(token_data["username"], request.json["list_name"]):
                        col = db()["Todo"]
                        insert = col.insert_one({"username": token_data["username"],
                                                 "list_name": request.json["list_name"], "title": request.json["title"], "status": 0})
                        if insert:
                            return function.response("Todo Created", "", 200)
                    else:
                        return function.error.not_found(self)
                else:
                    return function.error.unauthorized(self)
            else:
                return function.error.bad_request(self)
        except:
            return function.error.bad_request(self)

    def delete(self):
        try:
            if request.json["token"] and request.json["id"]:
                token_data = function.token_decode(request.json["token"])
                if function.check_permission(token_data["role"], "todo", "delete"):
                    if function.find_by_id("Todo", request.json["id"]):
                        print(token_data["username"])
                        my_query = {"username": token_data["username"], "_id": ObjectId(request.json["id"])}
                        col = db()["Todo"]
                        if col.delete_one(my_query):
                            return function.response("Item Deleted.", "", 200)
                    return function.error.not_found(self)
                else:
                    return function.error.unauthorized(self)
        except:
            return function.error.bad_request(self)

    def put(self):
        if request.json["token"] and request.json["id"] and request.json["status"]:
            token_data = function.token_decode(request.json["token"])
            if function.check_permission(token_data["role"], "list", "put"):
                if function.find_by_id("Todo", request.json["id"]):
                    col = db()["Todo"]
                    req = {"_id": ObjectId(request.json["id"]), "username": token_data["username"]}
                    new = {"$set": {"status": request.json["status"]}}
                    update_request = col.update_one(req, new)
                    if update_request:
                        return function.response("Success.", "", 200)
                    else:
                        return function.error.not_found(self)
                else:
                    return function.error.not_found(self)
            else:
                return function.error.unauthorized(self)
        else:
            return function.error.bad_request(self)
    def patch(self):
        if request.json["token"] and request.json["id"] and request.json["title"]:
            token_data = function.token_decode(request.json["token"])
            if function.check_permission(token_data["role"], "list", "put"):
                if function.find_by_id("Todo", request.json["id"]):
                    col = db()["Todo"]
                    req = {"_id": ObjectId(request.json["id"]), "username": token_data["username"]}
                    new = {"$set": {"title": request.json["title"]}}
                    update_request = col.update_one(req, new)
                    if update_request:
                        return function.response("Success.", "", 200)
                    else:
                        return function.error.not_found(self)
                else:
                    return function.error.not_found(self)
            else:
                return function.error.unauthorized(self)
        else:
            return function.error.bad_request(self)

class List(Resource):

    def get(self):
        if request.json["token"]:
            token_data = function.token_decode(request.json["token"])
            if function.check_permission(token_data["role"], "list", "get"):
                col = db()["Lists"]
                u_list = col.find({"username": token_data["username"]})
                data = []
                for li in u_list:
                    data.append(function.list_to_json(li))
                lists = {"lists": data}
                return function.response("Success.", lists, 200)
            else:
                return function.error.unauthorized(self)
        else:
            return function.error.bad_request(self)

    def post(self):
        try:
            if request.json["token"] and request.json["list_name"]:
                token_data = function.token_decode(request.json["token"])
                if function.check_permission(token_data["role"], "list", "post"):
                    if not function.check_list_exist(token_data["username"], request.json["list_name"]):
                        col = db()["Lists"]
                        insert = col.insert_one({"username": token_data["username"],
                                                 "list_name": request.json["list_name"]})
                        if insert:
                            return function.response("List Created", "", 200)
                        else:
                            return function.error.not_found(self)
                    else:
                        return function.error.bad_request(self)
                else:
                    return function.error.unauthorized(self)
            else:
                return function.error.bad_request(self)
        except:
            return function.error.bad_request(self)

    def delete(self):
        try:
            if request.json["token"] and request.json["list_name"]:
                token_data = function.token_decode(request.json["token"])
                if function.check_permission(token_data["role"], "list", "delete"):
                    if function.check_list_exist(token_data["username"], request.json["list_name"]):
                            my_query = {"username": token_data["username"], "list_name": request.json["list_name"]}
                            col = db()["Lists"]
                            st =col.delete_one(my_query)
                            if st:
                                return function.response("List Deleted.", "", 200)
                    return function.error.not_found(self)
                else:
                    return function.error.unauthorized(self)
            else:
                return function.error.bad_request(self)
        except:
            return function.error.bad_request(self)

    def put(self):
        if request.json["token"] and request.json["id"] and request.json["list_name"]:
            token_data = function.token_decode(request.json["token"])
            if function.check_permission(token_data["role"], "list", "put"):
                if function.find_by_id("Lists", request.json["id"]):
                    col = db()["Lists"]
                    req = {"_id": ObjectId(request.json["id"]), "username": token_data["username"]}
                    new = {"$set": {"list_name": request.json["list_name"]}}
                    update_request = col.update_one(req, new)
                    if update_request:
                        return function.response("Success.", "", 200)
                    else:
                        return function.error.bad_request(self)
                else:
                    return function.error.not_found(self)
            else:
                return function.error.unauthorized(self)
        else:
            return function.error.bad_request(self)

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Todo, '/todo')
api.add_resource(List, '/list')

if __name__ == '__main__':
    app.run(port=5000, host='127.0.0.1', debug=True)
