from tinydb import TinyDB, Query

# Programs and Activities databases
class Activities():
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Activities()
        return cls._instance

    def __init__(self):
        self.activities = TinyDB("data/activities.json")
        self.query = Query()

    def load(self, name, default):
        if name and default is None:
            activities = self.activities.search(self.query.name == name)
            if len(activities) > 0:
                return activities[0]
        elif default is not None:
            if len(self.activities.search(self.query.default == True)) > 0:
                return self.activities.search(self.query.default == True)[0]
            return None
        return None

    def save(self, name, activity):
        # if saved activity is "default", reset existing default activity to "non-default"
        if activity.get("default", False) is True:
            self.activities.update({'default': False})
        if self.activities.search(self.query.name == name) == []:
            self.activities.insert(activity)
        else:
            self.activities.update(activity, self.query.name == activity["name"])

    def delete(self, name):
        activities = self.activities.search(self.query.name == name)
        if len(activities) > 0:
            activity = activities[0]
            if activity.get("default", False) is True:
                self.activities.update({'default': True}, self.query.stock == True)
            self.activities.remove(self.query.name == activity["name"])

    def list(self):
        return self.activities.all()
