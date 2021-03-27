def db():
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")
    return client["selle"]
