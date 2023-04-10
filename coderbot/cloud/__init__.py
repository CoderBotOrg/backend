# Sync CoderBot configuration with remote Cloud configuration
#
# For all configuration entities (settings, activities, programs):
#   check sync mode (upstream, downstream, both)
#   if up:
#     compare entity, if different, push changes
#   if down:
#     compare entity, if different, pull changes
#   if both:
#     compare entity, if different, take most recent and push/pull changes
#

import threading
from datetime import datetime, timezone
import logging
import json
from time import sleep

from config import Config
from activity import Activities
from program import ProgramEngine

import cloud_api_robot_client
from cloud_api_robot_client.apis.tags import robot_sync_api
from cloud_api_robot_client.model.activity import Activity
from cloud_api_robot_client.model.program import Program
from cloud_api_robot_client.model.robot_data import RobotData
from cloud_api_robot_client.model.setting import Setting

class CloudManager(threading.Thread):
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CloudManager()
        return cls._instance

    def __init__(self):
        threading.Thread.__init__(self)
        # Defining the host is optional and defaults to https://api.coderbot.org/api/v1
        # See configuration.py for a list of all supported configuration parameters.
        self.configuration = cloud_api_robot_client.Configuration(
            host = "http://192.168.1.8:8090/api/v1",
            # Configure Bearer authorization: coderbot_auth
        )
        self.configuration.access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IkNaMVFtVGM1WGZIV2NfQ1dPVG9kcm1QaXZFNFJ2ckFXaFZ3T28yTm85eDAifQ.eyJpc3MiOiJDb2RlckJvdCBDbG91ZCBBUEkiLCJpYXQiOjE2Nzc3MDI4NjIsImV4cCI6MTcwOTIzODg2MiwiYXVkIjoic3QtYXBpLmNvZGVyYm90Lm9yZyIsInN1YiI6InRwWkpYNFlsNElZd21QSzhEd2JmIiwiZW1haWwiOiJ0cFpKWDRZbDRJWXdtUEs4RHdiZkBib3RzLmNvZGVyYm90Lm9yZyIsInBpY3R1cmUiOiJodHRwczovL3N0LWFwcC5jb2RlcmJvdC5vcmcvcGljdHVyZXMvbm9waWMifQ.WlrYd-n6-WWHUxlz1kqnGl8TkjspVWn1UhKK_RIWyIJVlczD1GkqT4uqkHl2aGnp9I_E2SETUvC3dWkkUBG7qHvUIIZVaVhGpfiQy7WMekEdMnXtsPxK8NsWjHYUTbqz2dyz2Z1eQi5Ydhj4niEWsKCAT2BG-nwTIDxu-uxKrah6AtCGGyGKCQu0qje-qUNCxT5S1Y5RT10XS4Ewl2ROsMr1M6P3EVa0VoSJ26QZlh5jIz-8fhyGspxBHFEnZF-p95vEGCQp6M7epwoesDGVlX4AxEEpPk7c_Pd4c2gNLx1nhpkV26sT_c_NESNTM42tVyH9ZjQ5fxCUOEi_ELJ2vQ'

        self.start()

    def run(self):
        while(True):
            logging.info("run.begin")
            settings = Config.read()
            syncmodes = settings.get("syncmodes", {"settings": "n", "activities": "n", "programs": "n"})
            # Enter a context with an instance of the API client
            with cloud_api_robot_client.ApiClient(self.configuration) as api_client:
                # Create an instance of the API class
                api_instance = robot_sync_api.RobotSyncApi(api_client)
                
                self.sync_settings(api_instance, syncmodes["settings"])

                self.sync_activities(api_instance, syncmodes["activities"])

                self.sync_programs(api_instance, syncmodes["programs"])

            sleep(10)
            logging.info("run.end")

    def sync_settings(self, api_instance, syncmode):
        try:
            # Create an instance of the API class
            api_response = api_instance.get_robot_setting()
            cloud_setting_object = api_response.body
            cloud_setting = json.loads(cloud_setting_object.get('data'))
            local_setting = Config.read()
            local_most_recent = datetime.fromisoformat(cloud_setting_object["modified"]).timestamp() < Config.modified()
            if cloud_setting != local_setting:
                if syncmode == "u" or (syncmode == "b" and local_most_recen):
                    body = Setting(
                        id=api_response.body.get('id'),
                        org_id=api_response.body.get('org_id'),
                        name=api_response.body.get('name'),
                        description=api_response.body.get('description'),
                        data=json.dumps(setting),
                        modified=datetime.now().isoformat(),
                        status=api_response.body.get('status'),
                    )
                    api_response = api_instance.set_robot_setting(body)
                    logging.info("run.4")
                if syncmode == 'd': # setting, down
                    logging.info("cloud_setting: ", str(cloud_setting.data.setting))
                    Config.write(cloud_setting.data.setting) 
        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling RobotSyncApi: %s\n" % e)

    def sync_activities(self, api_instance, syncmode):
        activities = Activities.get_instance().list()
        try:
            # Get robot activities
            api_response = api_instance.get_robot_activities()
            cloud_activities = api_response.body
            logging.info("run.activities.cloud" + str(cloud_activities))
            # cloud activities
            a_c_m = {} # activities_cloud_map 
            for a in cloud_activities:
                a_c_m[a.get("id")] = a

            a_l_m = {} # activities_local_map 
            # local activities no id
            for a in activities:
                if a.get("id") is not None:
                    a_l_m[a.get("id")] = a

            # loop through local
            for al in activities:
                logging.info("syncing: " + str(al.get("id")))
                ac = a_c_m.get(al.get("id"))
                if ac is not None:
                    al["modified"] = al.get("modified", datetime.now(tz=timezone.utc).isoformat()) 
                    local_activity_more_recent = datetime.fromisoformat(ac.get("modified")).timestamp() < datetime.fromisoformat(al.get("modified")).timestamp()
                    if syncmode == "u" or (local_activity_more_recent and syncmode == 'b'):
                        ac["data"] = al.get("data")
                        ac["modified"] = al.get("modified")
                        body = Activity(
                            id=ac.get("id"),
                            org_id=ac.get("org_id"),
                            name=al.get("name"),
                            description=al.get("description"),
                            data=json.dumps(al.get("data")),
                            modified=al.get("modified").isoformat(),
                            status='active',
                        )
                        #logging.info("run.activities.cloud.saving")
                        api_response = api_instance.set_robot_activity(ac.get("id"), body)
                        #logging.info("run.activities.cloud.saved")
                    elif syncmode == "d" or (not local_activity_more_recent and syncmode == 'b'):
                        al["data"] = ac.get("data")
                        al["modified"] = ac.get("modified")
                        Activities.get_instance().save(al.get("name"), al)
                        logging.info("run.activities.local.saved: " + ac.get("name"))
                elif ac is None and syncmode in ['u', 'b']:
                    #logging.info("activity:" + str(al))
                    body = Activity(
                        id="",
                        org_id="",
                        name=al.get("name"),
                        description=al.get("description"),
                        data=json.dumps(al),
                        modified=al.get("modified", datetime.now(tz=timezone.utc).isoformat()),
                        status="active",
                    )
                    api_response = api_instance.create_robot_activity(body=body)
                    logging.info("run.activities.cloud.created: " + str(api_response.body["id"]))
                    al["id"] = api_response.body["id"]
                    al["org_id"] = api_response.body["org_id"]
                    logging.info("run.activities.saving_local: " + al.get("name"))
                    Activities.get_instance().save(al.get("name"), al)
                elif ac is None and syncmode in ['d']:
                    logging.info("run.activities.deleting_local: " + al.get("name"))
                    Activities.get_instance().delete(al.get("name"))
            for ac, k in a_c_m.items():
                if a_l_m.get(k) is None and syncmode in ['d', 'b']:
                    Activities.get_instance().save(ac.get("name"), ac)
                    logging.info("run.activities.local.saved: " + ac.get("name"))

        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling RobotSyncApi: %s\n" % e)

    def sync_programs(self, api_client, syncmode):
        pass
