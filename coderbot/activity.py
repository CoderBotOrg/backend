import logging
import uuid
from tinydb import TinyDB, Query
from threading import Lock
from datetime import datetime
# Programs and Activities databases

ACTIVITY_STATUS_DELETED = "deleted"
ACTIVITY_STATUS_ACTIVE = "active"
ACTIVITY_KIND_STOCK = "stock"
ACTIVITY_KIND_USER = "user"

    
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

    def load(self, id, default, active_only=True):
        with self.lock: 
            if id and default is None:
                activities = []
                if active_only:
                    activities = self.activities.search((self.query.id == id) & (self.query.status == ACTIVITY_STATUS_ACTIVE))
                else:
                    activities = self.activities.search(self.query.id == id)
                if len(activities) > 0:
                    return activities[0]
            elif default is not None:
                if len(self.activities.search(self.query.default == True)) > 0:
                    return self.activities.search(self.query.default == True)[0]
                return None
            return None

    def save(self, activity):
        if activity.get("id") is None:
            activity["id"] = str(uuid.uuid4())
        with self.lock: 
            # if saved activity is "default", reset existing default activity to "non-default"
            if activity.get("default", False) is True:
                self.activities.update({'default': False})
            if self.activities.search(self.query.id == activity.get("id")) == []:
                self.activities.insert(activity)
            else:
                self.activities.update(activity, self.query.id == activity.get("id"))
        activity = self.activities.search(self.query.id == activity.get("id"))[0]
        logging.info("updating/creating activity: %s", str(activity))
        return activity

    def delete(self, id, logical = True):
        with self.lock: 
            activities = self.activities.search(self.query.id == id)
            if len(activities) > 0:
                activity = activities[0]
                if activity.get("default", False) is True:
                    self.activities.update({'default': True}, self.query.kind == ACTIVITY_KIND_STOCK)
                if logical:
                    activity["status"] = ACTIVITY_STATUS_DELETED
                    activity["modified"] = datetime.now().isoformat()
                    self.activities.update(activity, self.query.id == id)
                else:
                    self.activities.remove(self.query.id == id)

    def permanentlyRemoveDeletedActivities(self):
        for a in self.list(active_only=False):
            logging.info("checking: " + a["id"])
            if a["status"] == ACTIVITY_STATUS_DELETED:
                logging.info("deleting: " + a["name"])
                self.delete(a["id"], logical=False)

    def list(self, active_only = True):
        with self.lock: 
            if active_only:
                return self.activities.search(self.query.status == ACTIVITY_STATUS_ACTIVE)
            else:
                return self.activities.all()
