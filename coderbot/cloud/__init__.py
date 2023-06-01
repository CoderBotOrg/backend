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
from activity import Activities, ACTIVITY_KIND_USER, ACTIVITY_KIND_STOCK, ACTIVITY_STATUS_ACTIVE, ACTIVITY_STATUS_DELETED
from program import ProgramEngine
import program
import activity

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
            # logging.info("settings.syncing: " + cloud_setting_object.get("id", "") + " name: " + cloud_setting_object.get("name", ""))
            if cloud_setting != local_setting:
                if sync_mode == SYNC_UPSTREAM or (sync_mode == SYNC_BIDIRECTIONAL and local_most_recent):
                    body = Setting(
                        id = cloud_setting_object.get('id'),
                        org_id = cloud_setting_object.get('org_id'),
                        name = cloud_setting_object.get('name'),
                        description = cloud_setting_object.get('description'),
                        data = json.dumps(local_setting),
                        kind = local_setting.get("kind", "stock"),
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
        activities_local_user = list()
        activities_local_stock = list()
        activities_local_to_be_deleted = list()
        activities_local_map = {}
        for a in Activities.get_instance().list(active_only=False):
            if a.get("kind") == ACTIVITY_KIND_USER:
                if a.get("status") == ACTIVITY_STATUS_ACTIVE:
                    activities_local_user.append(a)
                    if a.get("id") is not None:
                        activities_local_map[a.get("id")] = a
                elif a.get("status") == ACTIVITY_STATUS_DELETED:
                    activities_local_to_be_deleted.append(a)
            else:
                activities_local_stock.append(a)
                if a.get("id") is not None:
                    activities_local_map[a.get("id")] = a
        try:
            # Get robot activities
            api_response = api_instance.get_robot_activities()
            cloud_activities = api_response.body
            # cloud activities
            activities_cloud_map = {}
            for a in cloud_activities:
               if a.get("status") == ACTIVITY_STATUS_ACTIVE:
                    activities_cloud_map[a.get("id")] = a

            # loop through local
            for al in activities_local_user:
                logging.info("activities.syncing: " + str(al.get("id")) + " name: " + str(al.get("name")))
                ac = activities_cloud_map.get(al.get("id"))
                ac_al_equals = (ac is not None and ac.get("data") == al.get("data"))
                if ac is not None and not ac_al_equals:
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
                            kind = al.get("kind", "stock"),
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
                        kind=al.get("kind", "stock"),
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

            for k, ac in activities_cloud_map.items():
                if activities_local_map.get(k) is None and sync_mode in [SYNC_DOWNSTREAM, SYNC_BIDIRECTIONAL]:
                    logging.info("activities.create.downstream: " + ac.get("name"))
                    activity = json.loads(ac.get("data"))
                    activity["id"] = ac.get("id")
                    activity["org_id"] = ac.get("org_id")
                    activity["name"] = ac.get("name")
                    activity["description"] = ac.get("description")
                    activity["kind"] = ac.get("kind")
                    activity["status"] = ac.get("status")
                    Activities.get_instance().save(ac.get("name"), activity)

            # manage local user activities to be deleted locally and upstream
            for al in activities_local_to_be_deleted:
                if al.get("id") is not None:
                    logging.info("activities.delete.upstream: " + al.get("name"))
                    api_response = api_instance.delete_robot_program(path_params={"activity_id":al.get("id")})
                # delete locally permanently
                Activities.get_instance().delete(al.get("name"), logical=False)

            # manage local stock activities to be deleted locally
            for al in activities_local_stock:
                # logging.info("activities.check.stock.locally: " + al.get("name") + " id: " + str(al.get("id")))
                if al.get("id") is not None and activities_cloud_map.get(al.get("id")) is None:
                    logging.info("activities.delete.stock.locally: " + al.get("name"))
                    # delete locally permanently
                    Activities.get_instance().delete(al.get("name"), logical=False)

        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling activities RobotSyncApi: %s\n" % e)

    def sync_programs(self, api_instance, sync_mode):
        programs_local_user = list()
        programs_local_stock = list()
        programs_local_map = {}  
        programs_local_to_be_deleted = list()
        for p in ProgramEngine.get_instance().prog_list(active_only=False):
            if p.get("kind") == program.PROGRAM_KIND_USER:
                if p.get("status") == program.PROGRAM_STATUS_ACTIVE:
                    programs_local_user.append(p)
                    if p.get("id") is not None:
                        programs_local_map[p.get("id")] = p
                elif p.get("status") == program.PROGRAM_STATUS_DELETED:
                    programs_local_to_be_deleted.append(p)
            else:
                programs_local_stock.append(p)
                if p.get("id") is not None:
                    programs_local_map[p.get("id")] = p
                
        try:
            # Get cloud programs
            api_response = api_instance.get_robot_programs()
            cloud_programs = api_response.body
            # cloud programs in a map id : program
            programs_cloud_map = {} # programs_cloud_map 
            for p in cloud_programs:
                if p.get("status") == program.PROGRAM_STATUS_ACTIVE:
                    programs_cloud_map[p.get("id")] = p

            # sync local user programs
            # manage user programs present locally and in "active" status
            for pl in programs_local_user:
                pc = programs_cloud_map.get(pl.get("id"))
                pc_pl_equals = (pc is not None and 
                                pc.get("name") == pl.get("name") and 
                                pc.get("code") == pl.get("code") and 
                                pc.get("dom_code") == pl.get("dom_code") and
                                pc.get("status") == pl.get("status"))
                logging.info("programs.syncing: " + str(pl.get("id")) + " name: " + pl.get("name"))

                if pc is not None and not pc_pl_equals:
                    # cloud program exists and is different from local
                    pl["modified"] = pl.get("modified", datetime.now(tz=timezone.utc).isoformat()) 
                    local_program_more_recent = datetime.fromisoformat(pc.get("modified")).timestamp() < datetime.fromisoformat(pl.get("modified")).timestamp()
                    if sync_mode == SYNC_UPSTREAM or (local_program_more_recent and sync_mode == SYNC_BIDIRECTIONAL) and not to_be_deleted:
                        # cloud program exists and is less recent
                        pc["data"] = pl.get("data")
                        pc["modified"] = pl.get("modified")
                        body = Program(
                            id=pc.get("id"),
                            org_id=pc.get("org_id"),
                            name=pl.get("name"),
                            description=pl.get("description"),
                            code=pl.get("code"),
                            dom_code=pl.get("dom_code"),
                            kind=pl.get("kind"),
                            modified=pl.get("modified").isoformat(),
                            status='active',
                        )
                        #logging.info("run.activities.cloud.saving")
                        api_response = api_instance.set_robot_program(pc.get("id"), body)
                        logging.info("programs.update.upstream: " + pl.get("name"))
                    elif sync_mode == SYNC_DOWNSTREAM or (not local_program_more_recent and sync_mode == SYNC_BIDIRECTIONAL):
                        # cloud program exists and is more recent
                        pl["data"] = pc.get("data")
                        pl["modified"] = pc.get("modified")
                        ProgramEngine.get_instance().save(program.Program.from_dict(pl))
                        logging.info("programs.update.downstream: " + pl.get("name"))
                elif pc is None and sync_mode in [SYNC_UPSTREAM, SYNC_BIDIRECTIONAL]:
                    # cloud program does not exist
                    body = Program(
                        id="",
                        org_id="",
                        name=pl.get("name"),
                        description=pl.get("description", ""),
                        code=pl.get("code"),
                        dom_code=pl.get("dom_code"),
                        kind=pl.get("kind"),
                        modified=pl.get("modified", datetime.now(tz=timezone.utc).isoformat()),
                        status="active",
                    )
                    api_response = api_instance.create_robot_program(body=body)
                    pl["id"] = api_response.body["id"]
                    pl["org_id"] = api_response.body["org_id"]
                    ProgramEngine.get_instance().save(program.Program.from_dict(pl))
                    logging.info("programs.create.upstream: " + pl.get("name"))
                elif pc is None and sync_mode in [SYNC_DOWNSTREAM]:
                    # cloud program does not exist, delete locally since sync_mode is downstream
                    ProgramEngine.get_instance().delete(pl.get("name"))
                    logging.info("programs.delete.downstream: " + pl.get("name"))

            # manage cloud programs not present locally in "active" status
            for k, pc in programs_cloud_map.items():
                if programs_local_map.get(k) is None and sync_mode in [SYNC_DOWNSTREAM, SYNC_BIDIRECTIONAL]:
                    pl = program.Program(name=pc.get("name"), 
                                         code=pc.get("code"), 
                                         dom_code=pc.get("dom_code"), 
                                         kind=pc.get("kind"),
                                         id=pc.get("id"), 
                                         modified=datetime.fromisoformat(pc.get("modified")),
                                         status=pc.get("status"))
                    ProgramEngine.get_instance().save(pl)
                    logging.info("programs.create.downstream: " + pc.get("name"))

            # manage local user programs to be deleted locally and upstream
            for pl in programs_local_to_be_deleted:
                if pl.get("id") is not None:
                    logging.info("programs.delete.upstream: " + pl.get("name"))
                    api_response = api_instance.delete_robot_program(path_params={"program_id":pl.get("id")})
                # delete locally permanently
                ProgramEngine.get_instance().delete(pl.get("name"), logical=False)

            # manage local stock programs to be deleted locally
            for pl in programs_local_stock:
                # logging.info("programs.check.stock.locally: " + pl.get("name") + " id: " + str(pl.get("id")))
                if pl.get("id") is not None and programs_cloud_map.get(pl.get("id")) is None:
                    logging.info("programs.delete.stock.locally: " + pl.get("name"))
                    # delete locally permanently
                    ProgramEngine.get_instance().delete(pl.get("name"), logical=False)

        except cloud_api_robot_client.ApiException as e:
            logging.warn("Exception when calling programs RobotSyncApi: %s\n" % e)