"""
"""

from flask import jsonify
import json
from coderbot import CoderBot
from program import ProgramEngine, Program
from config import Config
import connexion
import time
import sqlite3
from tinydb import TinyDB, Query
from tinydb.operations import delete

bot_config = Config.get()
bot = CoderBot.get_instance(
    servo=(bot_config.get("move_motor_mode") == "servo"),
    motor_trim_factor=float(bot_config.get("move_motor_trim", 1.0)),
)

prog = None
prog_engine = ProgramEngine.get_instance()


def stop():
    bot.stop()
    return "ok"


def move(data):
    print(data)
    bot.move(speed=data["speed"], elapse=data["elapse"])
    return 200


def turn(data):
    print(data)
    bot.turn(speed=data["speed"], elapse=data["elapse"])
    return 200


def status():
    return {
        "status": "ok", "internetConnectivity": True, "temp": "40", "uptime": "5h", "status": "ok", "internetConnectivity": True, "temp": "40", "uptime": "5h"}


# Hardware and software information
def info():
    return {
        "model": 1,
        "serial": 2,
        "cbVersion": 3,
        "backendVersion": 4,
        "vueVersion": 5,
        "kernel": 6,
    }

def exec(data):
    prog = prog_engine.create(data["name"], data["code"])
    return json.dumps(prog.execute())

def editSettings(data):
    return "ok"

def restoreSettings():
    with open('defaultConfig.json') as f:
        Config.write(json.loads(f.read()))
    bot_config = Config.get()
    return "ok"


db = TinyDB("db.json")
query = Query()

def save(data):
    o = json.dumps(data)
    p = json.loads(o)
    if(db.search(query.name == p["name"]) == []):
        db.insert(p)
    else:
        db.update(p, query.name == p["name"])

def load(name):
    return db.search(query.name == name)[0]

def delete(data):
    db.remove(query.name == data["name"])

def list():
    return db.all()

db.insert({"dom_code": "<xml xmlns=\"http://www.w3.org/1999/xhtml\"><variables><variable type=\"\" id=\",46fU~j08oojjbw,kof`\">spazio_libero</variable></variables><block type=\"controls_whileUntil\" id=\"18\" x=\"-6\" y=\"95\"><field name=\"MODE\">WHILE</field><value name=\"BOOL\"><block type=\"logic_boolean\" id=\"8\"><field name=\"BOOL\">TRUE</field></block></value><statement name=\"DO\"><block type=\"variables_set\" id=\"+.ndl3CthRQ~=B/JKR^u\"><field name=\"VAR\" id=\",46fU~j08oojjbw,kof`\" variabletype=\"\">spazio_libero</field><value name=\"VALUE\"><block type=\"coderbot_adv_pathAhead\" id=\"43\"></block></value><next><block type=\"text_print\" id=\"34\"><value name=\"TEXT\"><block type=\"variables_get\" id=\"HvuukI#y0|2p~0G!J^1,\"><field name=\"VAR\" id=\",46fU~j08oojjbw,kof`\" variabletype=\"\">spazio_libero</field></block></value><next><block type=\"controls_if\" id=\"j2kyA19rSa;+oDM_|TW1\"><mutation else=\"1\"></mutation><value name=\"IF0\"><block type=\"logic_operation\" id=\".h3ecm+6-QkNKadH^K^x\"><field name=\"OP\">AND</field><value name=\"A\"><block type=\"logic_compare\" id=\"?y*$N(f@|9rhe.mOI}Tw\"><field name=\"OP\">GT</field><value name=\"A\"><block type=\"variables_get\" id=\"j(v,2aQSE^A_2Um!%r%j\"><field name=\"VAR\" id=\",46fU~j08oojjbw,kof`\" variabletype=\"\">spazio_libero</field></block></value><value name=\"B\"><block type=\"math_number\" id=\"]@VPRw![OoT^Q6^@}+W]\"><field name=\"NUM\">30</field></block></value></block></value><value name=\"B\"><block type=\"logic_compare\" id=\"!E.x/E#B,Eqe=[6!!UpQ\"><field name=\"OP\">NEQ</field><value name=\"A\"><block type=\"variables_get\" id=\"1|EJ6P/9-k+=y!xD!n59\"><field name=\"VAR\" id=\",46fU~j08oojjbw,kof`\" variabletype=\"\">spazio_libero</field></block></value><value name=\"B\"><block type=\"math_number\" id=\"!3n*B?S(XK~u$1}#F:~N\"><field name=\"NUM\">60</field></block></value></block></value></block></value><statement name=\"DO0\"><block type=\"coderbot_adv_move\" id=\"#SW!Qq8M:4),17-S5HXx\"><field name=\"ACTION\">FORWARD</field><value name=\"SPEED\"><block type=\"math_number\" id=\"ZIc[_OhSH1e.mz]:tL,?\"><field name=\"NUM\">100</field></block></value><value name=\"ELAPSE\"><block type=\"math_number\" id=\"-j(8o/#PiEQEY5L2zbT:\"><field name=\"NUM\">0.2</field></block></value></block></statement><statement name=\"ELSE\"><block type=\"coderbot_adv_move\" id=\"e#qON.)K9J9!}_W`xlWx\"><field name=\"ACTION\">RIGHT</field><value name=\"SPEED\"><block type=\"math_number\" id=\")C53Vd7c_sC*PsSn0VCM\"><field name=\"NUM\">100</field></block></value><value name=\"ELAPSE\"><block type=\"math_number\" id=\"E3zjXN1SRNL5~IQJ|aRQ\"><field name=\"NUM\">0.2</field></block></value></block></statement></block></next></block></next></block></statement></block></xml>", "code": "spazio_libero = None\n\n\nwhile True:\n  get_prog_eng().check_end()\n  spazio_libero = get_cam().path_ahead()\n  get_cam().set_text(spazio_libero)\n  if spazio_libero > 30 and spazio_libero != 60:\n    get_bot().forward(speed=100, elapse=0.2)\n  else:\n    get_bot().right(speed=100, elapse=0.2)\n", "name": "path_ahead"})