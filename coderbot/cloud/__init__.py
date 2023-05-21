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
from cloud_api_robot_client.model.robot_register_data import RobotRegisterData
from cloud_api_robot_client.model.robot_credentials import RobotCredentials

SYNC_UPSTREAM = 'u'
SYNC_DOWNSTREAM = 'd'
SYNC_BIDIRECTIONAL = 'b'

AUTH_FILE = "data/auth.json"

class CloudManager(threading.Thread):
    _instance = None

    _auth = {}

    @classmethod
    def get_auth(cls):
        return cls._auth

    @classmethod
    def read_auth(cls):
        with open(AUTH_FILE, 'r') as f:
          cls._auth = json.load(f)
          f.close()
          return cls._auth

    @classmethod
    def write_auth(cls, auth):
        cls._auth = auth
        f = open(AUTH_FILE, 'w')
        json.dump(cls._auth, f)
        return cls._auth

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
        try:
            self.read_auth()
        except FileNotFoundError:
            self.write_auth({})
        self.start()

    def run(self):
        while(True):
            settings = Config.read()
            logging.info("run.sync.begin")
            sync_modes = settings.get("sync_modes", {"settings": "n", "activities": "n", "programs": "n"})
            sync_period = int(settings.get("sync_period", "60"))

            token = self.get_token_or_register(settings)
            self.configuration.access_token = token

            # Enter a context with an instance of the API client
            with cloud_api_robot_client.ApiClient(self.configuration) as api_client:
                # Create an instance of the API class
                api_instance = robot_sync_api.RobotSyncApi(api_client)
                
                self.sync_settings(api_instance, sync_modes["settings"])
                self.sync_activities(api_instance, sync_modes["activities"])
                self.sync_programs(api_instance, sync_modes["programs"])

            sleep(sync_period)
            logging.info("run.sync.end")

    def get_token_or_register(self, settings):
        logging.info("run.check.token")
        token = self.get_auth().get("token")
        reg_otp = settings.get("reg_otp")
        logging.info("otp_reg:" + reg_otp)
        try:
            if token is None and reg_otp is not None:
                with cloud_api_robot_client.ApiClient(self.configuration) as api_client:
                    api_instance = robot_sync_api.RobotSyncApi(api_client)
                    body = RobotRegisterData(
                        otp=reg_otp,
                    )
                    api_response = api_instance.register_robot(body=body)
                    logging.info(api_response.body)
                    token = api_response.body.get("token")
                    self.write_auth({"token":token})
            return token
        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling register_robot RobotSyncApi: %s\n" % e)

    def sync_settings(self, api_instance, sync_mode):
        try:
            # Create an instance of the API class
            api_response = api_instance.get_robot_setting()
            cloud_setting_object = api_response.body
            cloud_setting = json.loads(cloud_setting_object.get('data'))

            local_setting = Config.read()
            local_most_recent = datetime.fromisoformat(cloud_setting_object.get("modified", "2000-01-01T00:00:00.000000")).timestamp() < Config.modified()
            logging.info("settings.syncing: " + cloud_setting_object.get("id", "") + " name: " + cloud_setting_object.get("name", ""))
            if cloud_setting != local_setting:
                if sync_mode == SYNC_UPSTREAM or (sync_mode == SYNC_BIDIRECTIONAL and local_most_recent):
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
                if sync_mode == SYNC_DOWNSTREAM: # setting, down
                    Config.write(cloud_setting.data.setting) 
                    logging.info("settings.downstream")
        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling settings RobotSyncApi: %s\n" % e)

    def sync_activities(self, api_instance, sync_mode):
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
                    if sync_mode == SYNC_UPSTREAM or (local_activity_more_recent and sync_mode == SYNC_BIDIRECTIONAL):
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
                    elif sync_mode == "d" or (not local_activity_more_recent and sync_mode == SYNC_BIDIRECTIONAL):
                        al["data"] = ac.get("data")
                        al["modified"] = ac.get("modified")
                        Activities.get_instance().save(al.get("name"), al)
                        logging.info("activities.update.downstream: " + al.get("name"))
                elif ac is None and sync_mode in [SYNC_UPSTREAM, SYNC_BIDIRECTIONAL]:
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
                elif ac is None and sync_mode in [SYNC_DOWNSTREAM]:
                    Activities.get_instance().delete(al.get("name"))
                    logging.info("activities.delete.downstream: " + al.get("name"))
            for k, ac in a_c_m.items():
                if a_l_m.get(k) is None and sync_mode in [SYNC_DOWNSTREAM, SYNC_BIDIRECTIONAL]:
                    Activities.get_instance().save(ac.get("name"), ac)
                    logging.info("activities.create.downstream: " + ac.get("name"))

        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling activities RobotSyncApi: %s\n" % e)

    def sync_programs(self, api_instance, sync_mode):
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
            p_c_m = {} # programs_cloud_map 
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
                logging.info("programs.syncing: " + str(pl.get("id")) + " name: " + pl.get("name") + " sync_mode: " + sync_mode + " pc: " + str(pc))

                if pc is not None and not pc_pl_equals:
                    pl["modified"] = pl.get("modified", datetime.now(tz=timezone.utc).isoformat()) 
                    local_program_more_recent = datetime.fromisoformat(pc.get("modified")).timestamp() < datetime.fromisoformat(pl.get("modified")).timestamp()
                    if sync_mode == SYNC_UPSTREAM or (local_program_more_recent and sync_mode == SYNC_BIDIRECTIONAL) and not to_be_deleted:
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
                    elif sync_mode == SYNC_DOWNSTREAM or (not local_program_more_recent and sync_mode == SYNC_BIDIRECTIONAL):
                        pl["data"] = pc.get("data")
                        pl["modified"] = pc.get("modified")
                        ProgramEngine.get_instance().save(program.Program.from_dict(pl))
                        logging.info("programs.update.downstream: " + pl.get("name"))
                elif pc is None and sync_mode in [SYNC_UPSTREAM, SYNC_BIDIRECTIONAL]:
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
                elif pc is None and sync_mode in [SYNC_DOWNSTREAM]:
                    ProgramEngine.get_instance().delete(pl.get("name"))
                    logging.info("programs.delete.downstream: " + pl.get("name"))

            # manage programs not present locally in "active" status
            for k, pc in p_c_m.items():
                if p_l_m.get(k) is None and sync_mode in [SYNC_DOWNSTREAM, SYNC_BIDIRECTIONAL]:
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