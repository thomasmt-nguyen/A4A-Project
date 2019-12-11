import urllib.parse
from pymongo import MongoClient

statement = "250ALph@"
cluster = MongoClient(
    f"mongodb+srv://thomas:{urllib.parse.quote_plus(statement)}@cluster0-3zi0v.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["agent_simulation"]

environment = {'Test1': '0',
               'Test2': '1',
               'HW1': '2',
               'HW2': '3'}

env_name_mapping = {
               'TEST1': 'Test1',
               'TEST2': 'Test2',
               'HW1': 'HW1',
               'HW2': 'HW2'
}

class DataProxy:

    def write(self, agent, proxy):
        collection = db[proxy.env_name]
        id = agent.agent_id + int(proxy.env_id) * 10
        db_post = {"$set":
                    {
                        "completed_paylods": agent.completeded_payloads
                    }
                }
        db_id = {"_id": id}
        collection.update_one(db_id, db_post, True)


    def read(self, proxy):
        collection = db[proxy.env_name]


    def write_agent_info(self, agent_list, proxy):
        collection = db[proxy.env_name]
        agent_info = self.create_write_post(agent_list, proxy)
        db_post = {"$set": agent_info}
        db_id = {"_id": proxy.env_id}
        collection.update_one(db_id, db_post, True)


    def create_write_post(self, agent_list):
        data = dict()
        for agent in agent_list:
            info = { "payloads_completed": agent.completeded_payloads}
            data[f'{agent.agent_id}'] = info

        print(data)
        return data

    def read_agent_info(self, env_name):

        env_name = env_name_mapping[env_name.upper()]
        collection = db[env_name]
        id = environment[env_name]
        results = collection.find_one({"_id": id})
        print(results)
        return results



