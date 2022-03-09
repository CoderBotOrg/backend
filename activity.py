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

    def load(self, name, default):
        if name:
            return self.activities.search(self.query.name == name)[0]
        elif default is not None:
            return self.activities.search(self.query.default == True)[0]

    def save(self, activity):
        if self.activities.search(self.query.name == activity["name"]) == []:
            self.activities.insert(activity)
        else:
            if activity["default"] == True:
                default_activity = self.load(None, True)
                default_activity["default"] = False
                self.activities.update(default_activity, self.query.name == default_activity["name"])
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
                "capsSwitch": True,
                "bodyFont": "Roboto",
                "availableViews": [],
                "viewSource": None,
                "autoRecVideo": None,
                "toolbox": {
                    "kind": "flyoutToolbox",
                    "contents": []
                },
                "buttons": [
                {
                    "action": "clearProgramDlg",
                    "icon": "clear",
                    "label": "message.activity_program_clear",
                    "type": "text",
                },
                {
                    "action": 'saveProgram',
                    "icon": 'save',
                    "label": 'message.activity_program_save',
                    "type": 'text',
                },
                {
                    "action": 'toggleSaveAs',
                    "icon": 'edit',
                    "label": 'message.activity_program_save_as',
                    "type": 'text',
                },
                {
                    "action": 'loadProgramList',
                    "icon": 'folder_open',
                    "label": 'message.activity_program_load',
                    "type": 'text',
                },
                {
                    "action": 'runProgram',
                    "icon": 'play_arrow',
                    "label": 'message.activity_program_run',
                    "type": 'text',
                },
                {
                    "action": 'getProgramCode',
                    "icon": 'code',
                    "label": 'message.activity_program_show_code',
                    "type": 'text',
                },
                {
                    "action": 'exportProgram',
                    "icon": 'fa-file-export',
                    "label": 'message.activity_program_export',
                    "type": 'text',
                },
                {
                    "action": 'pickFile',
                    "icon": 'fa-file-import',
                    "label": 'message.activity_program_import',
                    "type": 'text',
                }],
            }
            self.save(activity)
 
