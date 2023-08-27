import logging
from tinydb import TinyDB, Query
from threading import Lock
from datetime import datetime
# Programs and Activities databases

ACTIVITY_STATUS_DELETED = "deleted"
ACTIVITY_STATUS_ACTIVE = "active"
ACTIVITY_KIND_STOCK = "stock"
ACTIVITY_KIND_USER = "user"

class Activity():
    def __init__(self, name, description, data, kind, status):
        self._name = name
        self._description = description
        self._data = data
        self._kind = kind
        self._status = status
    
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
        self.lock = Lock()
        self.permanentlyRemoveDeletedActivities()

    def load(self, name, default, active_only=True):
        with self.lock: 
            if name and default is None:
                activities = []
                if active_only:
                    activities = self.activities.search((self.query.name == name) & (self.query.status == ACTIVITY_STATUS_ACTIVE))
                else:
                    activities = self.activities.search(self.query.name == name)
                if len(activities) > 0:
                    return activities[0]
            elif default is not None:
                if len(self.activities.search(self.query.default == True)) > 0:
                    return self.activities.search(self.query.default == True)[0]
                return None
            return None

    def save(self, name, activity):
        with self.lock: 
            # if saved activity is "default", reset existing default activity to "non-default"
            if activity.get("default", False) is True:
                self.activities.update({'default': False})
            if self.activities.search(self.query.name == name) == []:
                self.activities.insert(activity)
            else:
                self.activities.update(activity, self.query.name == name)

    def delete(self, name, logical = True):
        with self.lock: 
            activities = self.activities.search(self.query.name == name)
            if len(activities) > 0:
                activity = activities[0]
                if activity.get("default", False) is True:
                    self.activities.update({'default': True}, self.query.stock == True)
                if logical:
                    activity["status"] = ACTIVITY_STATUS_DELETED
                    activity["modified"] = datetime.now().isoformat()
                    self.activities.update(activity, self.query.name == name)
                else:
                    self.activities.remove(self.query.name == name)

    def permanentlyRemoveDeletedActivities(self):
        for a in self.list(active_only=False):
            logging.info("checking: " + a["name"])
            if a["status"] == ACTIVITY_STATUS_DELETED:
                logging.info("deleting: " + a["name"])
                self.delete(a["name"], logical=False)

    def list(self, active_only = True):
        with self.lock: 
            if active_only:
                return self.activities.search(self.query.status == ACTIVITY_STATUS_ACTIVE)
            else:
                return self.activities.all()
