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
import program

import cloud_api_robot_client
from cloud_api_robot_client.apis.tags import robot_sync_api
from cloud_api_robot_client.model.activity import Activity
from cloud_api_robot_client.model.program import Program
from cloud_api_robot_client.model.robot_data import RobotData
from cloud_api_robot_client.model.setting import Setting

SYNC_UPSTREAM = 'u'
SYNC_DOWNSTREAM = 'd'
SYNC_BIDIRECTIONAL = 'b'

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
            host = "http://192.168.1.7:8090/api/v1",
        )
        # Configure Bearer authorization: coderbot_auth
        self.configuration.access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IkNaMVFtVGM1WGZIV2NfQ1dPVG9kcm1QaXZFNFJ2ckFXaFZ3T28yTm85eDAifQ.eyJpc3MiOiJDb2RlckJvdCBDbG91ZCBBUEkiLCJpYXQiOjE2Nzc3MDI4NjIsImV4cCI6MTcwOTIzODg2MiwiYXVkIjoic3QtYXBpLmNvZGVyYm90Lm9yZyIsInN1YiI6InRwWkpYNFlsNElZd21QSzhEd2JmIiwiZW1haWwiOiJ0cFpKWDRZbDRJWXdtUEs4RHdiZkBib3RzLmNvZGVyYm90Lm9yZyIsInBpY3R1cmUiOiJodHRwczovL3N0LWFwcC5jb2RlcmJvdC5vcmcvcGljdHVyZXMvbm9waWMifQ.WlrYd-n6-WWHUxlz1kqnGl8TkjspVWn1UhKK_RIWyIJVlczD1GkqT4uqkHl2aGnp9I_E2SETUvC3dWkkUBG7qHvUIIZVaVhGpfiQy7WMekEdMnXtsPxK8NsWjHYUTbqz2dyz2Z1eQi5Ydhj4niEWsKCAT2BG-nwTIDxu-uxKrah6AtCGGyGKCQu0qje-qUNCxT5S1Y5RT10XS4Ewl2ROsMr1M6P3EVa0VoSJ26QZlh5jIz-8fhyGspxBHFEnZF-p95vEGCQp6M7epwoesDGVlX4AxEEpPk7c_Pd4c2gNLx1nhpkV26sT_c_NESNTM42tVyH9ZjQ5fxCUOEi_ELJ2vQ'
        self.start()

    def run(self):
        while(True):
            logging.info("run.sync.begin")
            settings = Config.read()
            syncmodes = settings.get("syncmodes", {"settings": "n", "activities": "n", "programs": "n"})
            sync_period = int(settings.get("sync_period", "60"))

            # Enter a context with an instance of the API client
            with cloud_api_robot_client.ApiClient(self.configuration) as api_client:
                # Create an instance of the API class
                api_instance = robot_sync_api.RobotSyncApi(api_client)
                
                self.sync_settings(api_instance, syncmodes["settings"])
                self.sync_activities(api_instance, syncmodes["activities"])
                self.sync_programs(api_instance, syncmodes["programs"])

            sleep(sync_period)
            logging.info("run.sync.end")

    def sync_settings(self, api_instance, syncmode):
        try:
            # Create an instance of the API class
            api_response = api_instance.get_robot_setting()
            cloud_setting_object = api_response.body
            cloud_setting = json.loads(cloud_setting_object.get('data'))
            local_setting = Config.read()
            local_most_recent = datetime.fromisoformat(cloud_setting_object["modified"]).timestamp() < Config.modified()
            logging.info("settings.syncing: " + cloud_setting_object.get("id") + " name: " + cloud_setting_object.get("id"))
            if cloud_setting != local_setting:
                if syncmode == SYNC_UPSTREAM or (syncmode == SYNC_BIDIRECTIONAL and local_most_recent):
                    body = Setting(
                        id = cloud_setting_object.get('id'),
                        org_id = cloud_setting_object.get('org_id'),
                        name = cloud_setting_object.get('name'),
                        description = cloud_setting_object.get('description'),
                        data = json.dumps(local_setting),
                        modified = datetime.now().isoformat(),
                        status = cloud_setting_object.get('status'),
                    )
                    api_response = api_instance.set_robot_setting(body)
                    logging.info("settings.upstream")
                if syncmode == SYNC_DOWNSTREAM: # setting, down
                    Config.write(cloud_setting.data.setting) 
                    logging.info("settings.downstream")
        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling settings RobotSyncApi: %s\n" % e)

    def sync_activities(self, api_instance, syncmode):
        activities = Activities.get_instance().list()
        try:
            # Get robot activities
            api_response = api_instance.get_robot_activities()
            cloud_activities = api_response.body
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
                logging.info("activities.syncing: " + str(al.get("id")) + " name: " + str(al.get("name")))
                ac = a_c_m.get(al.get("id"))
                if ac is not None and ac.get("data") != al.get("data"):
                    al["modified"] = al.get("modified", datetime.now(tz=timezone.utc).isoformat()) 
                    local_activity_more_recent = datetime.fromisoformat(ac.get("modified")).timestamp() < datetime.fromisoformat(al.get("modified")).timestamp()
                    if syncmode == SYNC_UPSTREAM or (local_activity_more_recent and syncmode == SYNC_BIDIRECTIONAL):
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
                        logging.info("activities.update.upstream: " + al.get("name"))
                    elif syncmode == "d" or (not local_activity_more_recent and syncmode == SYNC_BIDIRECTIONAL):
                        al["data"] = ac.get("data")
                        al["modified"] = ac.get("modified")
                        Activities.get_instance().save(al.get("name"), al)
                        logging.info("activities.update.downstream: " + al.get("name"))
                elif ac is None and syncmode in [SYNC_UPSTREAM, SYNC_BIDIRECTIONAL]:
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
                    al["id"] = api_response.body["id"]
                    al["org_id"] = api_response.body["org_id"]
                    Activities.get_instance().save(al.get("name"), al)
                    logging.info("activities.create.upstream: " + al.get("name"))
                elif ac is None and syncmode in [SYNC_DOWNSTREAM]:
                    Activities.get_instance().delete(al.get("name"))
                    logging.info("activities.delete.downstream: " + al.get("name"))
            for k, ac in a_c_m.items():
                if a_l_m.get(k) is None and syncmode in [SYNC_DOWNSTREAM, SYNC_BIDIRECTIONAL]:
                    Activities.get_instance().save(ac.get("name"), ac)
                    logging.info("activities.create.downstream: " + ac.get("name"))

        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling activities RobotSyncApi: %s\n" % e)

    def sync_programs(self, api_instance, syncmode):
        programs = list()
        programs_to_be_deleted = list()
        for p in ProgramEngine.get_instance().prog_list(active_only=False):
            if not p.get("default"):
                if p.get("status") == program.PROGRAM_STATUS_ACTIVE:
                    programs.append(p)
                elif p.get("status") == program.PROGRAM_STATUS_DELETED:
                    programs_to_be_deleted.append(p)

        try:
            # Get robot activities
            api_response = api_instance.get_robot_programs()
            cloud_programs = api_response.body
            # cloud activities
            p_c_m = {} # activities_cloud_map 
            for p in cloud_programs:
                if p.get("status") == program.PROGRAM_STATUS_ACTIVE:
                    p_c_m[p.get("id")] = p

            p_l_m = {} # activities_local_map 
            # local activities no id
            for p in programs:
                #logging.info("programs.local: " + str(p.get("id")) + " name: " + p.get("name"))
                if p.get("id") is not None:
                    p_l_m[p.get("id")] = p

            # manage programs present locally and in "active" status
            for pl in programs:
                pc = p_c_m.get(pl.get("id"))
                pc_pl_equals = (pc is not None and 
                                pc.get("name") == pl.get("name") and 
                                pc.get("code") == pl.get("code") and 
                                pc.get("dom_code") == pl.get("dom_code") and
                                pc.get("status") == pl.get("status"))
                logging.info("programs.syncing: " + str(pl.get("id")) + " name: " + pl.get("name"))

                if pc is not None and not pc_pl_equals:
                    pl["modified"] = pl.get("modified", datetime.now(tz=timezone.utc).isoformat()) 
                    local_program_more_recent = datetime.fromisoformat(pc.get("modified")).timestamp() < datetime.fromisoformat(pl.get("modified")).timestamp()
                    if syncmode == SYNC_UPSTREAM or (local_program_more_recent and syncmode == SYNC_BIDIRECTIONAL) and not to_be_deleted:
                        pc["data"] = pl.get("data")
                        pc["modified"] = pl.get("modified")
                        body = Program(
                            id=pc.get("id"),
                            org_id=pc.get("org_id"),
                            name=pl.get("name"),
                            description=pl.get("description"),
                            code=pl.get("code"),
                            dom_code=pl.get("dom_code"),
                            modified=pl.get("modified").isoformat(),
                            status='active',
                        )
                        #logging.info("run.activities.cloud.saving")
                        api_response = api_instance.set_robot_program(pc.get("id"), body)
                        logging.info("programs.update.upstream: " + pl.get("name"))
                    elif syncmode == "d" or (not local_program_more_recent and syncmode == SYNC_BIDIRECTIONAL):
                        pl["data"] = pc.get("data")
                        pl["modified"] = pc.get("modified")
                        ProgramEngine.get_instance().save(program.Program.from_dict(pl))
                        logging.info("programs.update.downstream: " + pl.get("name"))
                elif pc is None and syncmode in [SYNC_UPSTREAM, SYNC_BIDIRECTIONAL]:
                    body = Program(
                        id="",
                        org_id="",
                        name=pl.get("name"),
                        description=pl.get("description", ""),
                        code=pl.get("code"),
                        dom_code=pl.get("dom_code"),
                        modified=pl.get("modified", datetime.now(tz=timezone.utc).isoformat()),
                        status="active",
                    )
                    api_response = api_instance.create_robot_program(body=body)
                    pl["id"] = api_response.body["id"]
                    pl["org_id"] = api_response.body["org_id"]
                    ProgramEngine.get_instance().save(program.Program.from_dict(pl))
                    logging.info("programs.create.upstream: " + pl.get("name"))
                elif pc is None and syncmode in [SYNC_DOWNSTREAM]:
                    ProgramEngine.get_instance().delete(pl.get("name"))
                    logging.info("programs.delete.downstream: " + pl.get("name"))

            # manage programs not present locally in "active" status
            for k, pc in p_c_m.items():
                if p_l_m.get(k) is None and syncmode in [SYNC_DOWNSTREAM, SYNC_BIDIRECTIONAL]:
                    pl = program.Program(name=pc.get("name"), 
                                         code=pc.get("code"), 
                                         dom_code=pc.get("dom_code"), 
                                         default=False, 
                                         id=pc.get("id"), 
                                         modified=datetime.fromisoformat(pc.get("modified")),
                                         status=pc.get("status"))
                    ProgramEngine.get_instance().save(pl)
                    logging.info("programs.create.downstream: " + pc.get("name"))

            # manage programs to be deleted locally and upstream
            for pl in programs_to_be_deleted:
                if p.get("id") is not None:
                    logging.info("programs.delete.upstream: " + pl.get("name"))
                    api_response = api_instance.delete_robot_program(path_params={"program_id":pl.get("id")})
                # delete locally permanently
                ProgramEngine.get_instance().delete(pl.get("name"), logical=False)

        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling programs RobotSyncApi: %s\n" % e)