from os.path import exists
from json import load, dump


class Session:
    def __init__(self, client):
        self.client = client

    def doesSessionExist(self):
        return self.client.session_name and exists(f"{self.client.session_name}.fb")

    def loadSessionData(self):
        return load(open(f"{self.client.session_name}.fb", encoding="UTF-8"))

    def saveSession(self, playerInfo):
        data = {"restore_key": self.client.restore_key,
                "passport": self.client.passport,
                "udid": self.client.udid,
                "mobile_model": self.client.mobile_model,
                "player": {"id": playerInfo["id"], "name": playerInfo["name"], "invite_key": playerInfo["invite_key"]}}
        dump(data, open(f"{self.client.session_name}.fb", "w"), indent=4)
