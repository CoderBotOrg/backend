# class Program
import subprocess
 
class Program:

    def run(code, mode, temp_files_dict):

        tmp_folder_path = temp_files_dict["tmp_folder_path"]
        status_fileName = temp_files_dict["status_fileName"]
        prog_gen_commands_fileName = temp_files_dict["prog_gen_commands_fileName"]

        try:

            if mode == "fullExec":
                is_execFull = "is_execFull = True\n"
            else: # mode == stepByStep
                is_execFull = "is_execFull = False\n"

            headerFile = is_execFull + '\n\
\n\
import json\n\
from os import getpid, rename\n\
import sys\n\
import signal\n\
with open("' + tmp_folder_path + status_fileName + '", "r") as fh:\n\
 data_coderbotStatus = json.loads(fh.read())\n\
\n\
def saveStatus():\n\
 with open("' + tmp_folder_path + status_fileName + '.tmp", "w") as fh:\n\
  fh.write(json.dumps(data_coderbotStatus))\n\
  rename("' + tmp_folder_path + status_fileName + '.tmp", "' + tmp_folder_path + status_fileName + '")\n\
\n\
data_coderbotStatus["prog_gen"]["currentBlockId"] = None\n\
data_coderbotStatus["prog_gen"]["status"] = "loading"\n\
data_coderbotStatus["prog_gen"]["pid"] = getpid()\n\
saveStatus()\n\
print("####### "+str(data_coderbotStatus["prog_gen"]["pid"]))\n\
print("###### LAUNCHED")\n\
print("###### IMPORTING program.py MODULE...")\n\
\n\
from prog_gen_commands import Commands\n\
\n\
print("###### MODULE IMPORTED")\n\
data_coderbotStatus["prog_gen"]["status"] = "running"\n\
saveStatus()\n\
\n\
def do_command(sig, stack):\n\
 global is_execFull\n\
 with open("' + tmp_folder_path + prog_gen_commands_fileName + '", "r") as fh:\n\
  data_prog_gen_commands = json.loads(fh.read())\n\
\n\
 if data_prog_gen_commands["command"] == "change_mode":\n\
  if data_prog_gen_commands["argument"] == "fullExec":\n\
   is_execFull = True\n\
   data_coderbotStatus["prog_gen"]["status"] = "running"\n\
  elif data_prog_gen_commands["argument"] == "stepByStep":\n\
   is_execFull = False\n\
   data_coderbotStatus["prog_gen"]["status"] = "running"\n\
  else:\n\
   pass # Ignore if the argument is unknown\n\
 else:\n\
  pass # Ignore if the command is unknown\n\
 saveStatus()\n\
def do_terminate(sig, stack):\n\
 data_coderbotStatus["prog_gen"] = {}\n\
 data_coderbotStatus["prog_handler"]["mode"] = "stop"\n\
 saveStatus()\n\
 print("######### PROGRAM TERMINATED")\n\
 sys.exit(0)\n\
signal.signal(signal.SIGUSR1, do_command)\n\
signal.signal(signal.SIGTERM, do_terminate)\n\
\n'

            footerFile = 'data_coderbotStatus["prog_gen"] = {}\ndata_coderbotStatus["prog_handler"]["mode"] = "stop"\nsaveStatus()\nprint("######### PROGRAM TERMINATED")'

            code = headerFile + code + footerFile

            print("######## PREPARING THE FILE...")
            with open("_coderbot_generated_program.tmp.py", "w") as fh:
                fh.write(code)
            print("######## THE FILE IS READY")
            print("######## LAUNCHING...")
            subprocess.Popen(["python3", "_coderbot_generated_program.tmp.py"])

            return {"ok":True,"description":""}
        except Exception as e:
            return {"ok":False,"error_code":500,"description":"ProblemOnLauchingTheGeneratedProgram"}



