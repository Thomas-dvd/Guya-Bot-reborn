import json

import requests

API_URL = "https://aaronlem.ovh/api"


class AaronApi:
    def __init__(self):
        self.token = None
        self.headers = None
        self.login()

    def login(self):
        r = requests.post(f"{API_URL}/login", json={"email": "guyabot@aaron.ovh", "password": "S]#6S9im{L}zU58i"})
        if r.status_code == 200:
            self.token = json.loads(r.text)["token"]
            self.headers = {'Authorization': f'Bearer {self.token}',
                            'Content-Type': 'application/json',
                            'accept': 'application/json'}
        else:
            self.token = None
            raise Exception("Impossible de se connecter à Arron")

        print("Connected to Aaron")

    def get_user(self, username):
        url = f"{API_URL}/player?pseudo={username}"
        payload = {"populate": {"path": "colorData", "populate": ["color", "country"]}}
        r = requests.request("GET", url, headers=self.headers, json=payload)
        if not r.ok:
            return {
                "exist": False
            }

        data = json.loads(r.text)
        for country in data["colorData"]:
            if country["color"]["color"] == "green":
                green = country
                break
        else:
            raise Exception("Impossible de trouver le serveur green")
        return {
            "exist": True,
            "country": green["country"]["name"],
            "last_connection": green["last_connection"]
        }


if __name__ == '__main__':
    print(AaronApi().get_user("Tominix356"))
