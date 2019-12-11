import requests
import json

server_url = "https://island_of_agents.atke.a.intuit.com/xanadu"
headers = {
    "Content-Type": "application/json"
}

environment = {'Test1': '0',
               'Test2': '1',
               'HW1': '2',
               'HW2': '3'}


class ServerProxy:

    def __init__(self, env_name):
        self.env_name = env_name;
        self.env_id = self.set_env_id(env_name);

    def create(self):
        body = {"env_name": self.env_name}
        url = server_url + "/api/simulations/create"
        return requests.post(url=url, json=body, headers=headers);
        # TODO: data = json.load(response)

    def start(self):
        body = {"env_name": self.env_name}
        url = server_url + f"/api/simulations/{self.env_name}/start"
        return requests.post(url=url, json=body, headers=headers);

    def agent_action(self, agent_id, action, mode):
        body = {"action": action,
                "mode": mode}
        url = server_url + f"/api/simulations/{self.env_id}/agents/{agent_id}/action"
        return requests.post(url=url, json=body, headers=headers);

    def agent_status(self, agent_id):
        body = {}
        url = server_url + f"/api/simulations/{self.env_id}/agents/{agent_id}/status"
        return requests.get(url=url, json=body, headers=headers);

    def step(self):
        url = server_url + f"/api/simulations/{self.env_id}/step"
        return requests.put(url, json="{}", headers=headers);

    def set_env_id(self, env_name):
        return environment[env_name];
