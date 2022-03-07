from tinydb import TinyDB, Query
from tinydb.operations import delete

# Programs and Activities databases
class Activities():
    _instance = None
        
    @classmethod
    def get_instance(cls):
        if cls._instance == None:
            cls._instance = Activities()
        return cls._instance

    def __init__(self):
        self.activities = TinyDB("data/activities.json")
        self.query = Query()

    def load(self, name):
        return self.activities.search(self.query.name == name)[0]

    def save(self, activity):
        if self.activities.search(self.query.name == activity["name"]) == []:
            self.activities.insert(activity)
        else:
            self.activities.update(activity, self.query.name == activity["name"])

    def delete(self, activity):
        activities.remove(self.query.name == activity["name"])


    def list(self):
        return self.activities.all()
    
    def init_default(self):
        activities_collection = self.activities.search(self.query.stock == True)
        if len(activities_collection) == 0:
            activity = {
                "name": "default",
                "stock": True,
                "codeFont": 'ubuntumono',
                "description": None,
                "drawerEnabled": True,
                "exec": {
                    "camera": True,
                    "log": True,
                },
                "fontSize": 'Medio',
                "showName": True,
                "maxBlocks": None,
            }
            self.save(activity)
 
