import urllib.parse
from pymongo import MongoClient

password = "250ALph@"
cluster = MongoClient(f"mongodb+srv://thomas:{urllib.parse.quote_plus(password)}@cluster0-3zi0v.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["agent_simulation"]

class DataProxy():
    def __init__(self):
        self.dataProxy = db["simulation"]

    def write(self, info):
        self.dataProxy.find_and_modify(query={"_id": 0}, update={"$set": {"name": "Thomas", "Score": info}})






















































