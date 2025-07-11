import json
import os

CLIENTS_FILE = "clients.json"

def load_clients():
    if not os.path.exists(CLIENTS_FILE):
        return {}
    with open(CLIENTS_FILE, "r") as f:
        return json.load(f)

def get_client_config(client_id):
    clients = load_clients()
    return clients.get(client_id, None)
