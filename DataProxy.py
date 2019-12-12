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

    def read(self, proxy):
        collection = db[proxy.env_name]

    def write_simulation_info(self, agent_list, proxy):
        collection = db[proxy.env_name]
        agent_info = self.create_write_post(agent_list)
        db_post = {"$set": agent_info}
        db_id = {"_id": proxy.env_id}
        collection.update_one(db_id, db_post, True)

    def create_write_post(self, agent_list):
        data = dict()
        for agent in agent_list:
            info = {"payloads_completed": agent.completeded_payloads,
                    "agent_id": agent.agent_id,
                    "type": agent.type,
                    "status": agent.state.value,
                    "last_action": agent.last_action.bit}
            data[f'{agent.agent_id}'] = info

        return data

    def read_agent_info(self, env_name):
        env_name = env_name_mapping[env_name.upper()]
        collection = db[env_name]
        id = environment[env_name]
        results = collection.find_one({"_id": id})
        return results
