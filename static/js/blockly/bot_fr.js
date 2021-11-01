'use strict';

Blockly.Msg.CODERBOT_MOVE_FORWARD = "avancer";
Blockly.Msg.CODERBOT_MOVE_BACKWARD = "reculer";
Blockly.Msg.CODERBOT_MOVE_LEFT = "tourner à gauche";
Blockly.Msg.CODERBOT_MOVE_RIGHT = "tourner à droite";
Blockly.Msg.CODERBOT_MOVE_ADV_MOVE = "déplacer le robot";
Blockly.Msg.CODERBOT_MOVE_MOTION_MOVE = "déplacer le robot (motion control)";
Blockly.Msg.CODERBOT_MOVE_MOTION_TURN = "tourner le robot (motion control)";
Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR = "contrôler les moteurs :";
Blockly.Msg.CODERBOT_MOVE_ADV_SPEED = "vitesse"
Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_SPEED_LEFT = "vitesse à gauche"
Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_SPEED_RIGHT = "vitesse à droite"
Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_STEPS_LEFT = "pas à gauche"
Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_STEPS_RIGHT = "pas à droite"
Blockly.Msg.CODERBOT_MOVE_ADV_ELAPSE = "durant"
Blockly.Msg.CODERBOT_MOVE_MOTION_DIST = "distance"
Blockly.Msg.CODERBOT_MOVE_MOTION_ANGLE = "angle"
Blockly.Msg.CODERBOT_MOVE_ADV_TIP_FORWARD = "en avant"
Blockly.Msg.CODERBOT_MOVE_ADV_TIP_BACKWARD = "en arrière"
Blockly.Msg.CODERBOT_MOVE_ADV_TIP_RIGHT = "à droite"
Blockly.Msg.CODERBOT_MOVE_ADV_TIP_LEFT = "à gauche"
Blockly.Msg.CODERBOT_MOVE_ADV_TIP_TAIL= " avec une vitesse (0-100%) durant (secondes)"
Blockly.Msg.CODERBOT_MOVE_MOTION_MOVE_TIP = "déplace le robot, en utilisant la caméra pour controller"
Blockly.Msg.CODERBOT_MOVE_MOTION_TURN_TIP = "tourne le robot, en utilisant la caméra pour controller"
Blockly.Msg.CODERBOT_MOVE_SERVO = "move servo";
Blockly.Msg.CODERBOT_MOVE_SERVO_1 = "1";
Blockly.Msg.CODERBOT_MOVE_SERVO_2 = "2";
Blockly.Msg.CODERBOT_MOVE_SERVO_ANGLE = "angle";
Blockly.Msg.CODERBOT_MOVE_SERVO_TIP_TAIL= " servo angle (90..90°)"
Blockly.Msg.CODERBOT_MOVE_STOP = "stop";
Blockly.Msg.CODERBOT_SAY = "dit";
Blockly.Msg.CODERBOT_LOCALE_EN = "English";
Blockly.Msg.CODERBOT_LOCALE_IT = "Italian";
Blockly.Msg.CODERBOT_LOCALE_FR = "French";
Blockly.Msg.CODERBOT_LOCALE_ES = "Spanish";
Blockly.Msg.CODERBOT_PHOTO_TAKE = "prend une photo";
Blockly.Msg.CODERBOT_VIDEO_REC = "démarre l'enregistrement vidéo";
Blockly.Msg.CODERBOT_VIDEO_STOP = "arrête l'enregistrement vidéo";
Blockly.Msg.CODERBOT_SLEEP = "attend pendant";
Blockly.Msg.CODERBOT_SENSOR_PATHAHEAD = "chemin devant";
Blockly.Msg.CODERBOT_SENSOR_FINDLINE = "trouve la ligne";
Blockly.Msg.CODERBOT_SENSOR_FINDFACE = "trouve un visage";
Blockly.Msg.CODERBOT_SENSOR_FINDSIGNAL = "trouve un signal";
Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_FIND = "trouve";
Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_COLOR = "de cette couleur";
Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_DIST = "la distance";
Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_ANGLE = "l'angle";
Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_BOTH = "la distance et l'angle";
Blockly.Msg.CODERBOT_SENSOR_FINDFACE_X = "abscisse";
Blockly.Msg.CODERBOT_SENSOR_FINDFACE_Y = "ordonnée";
Blockly.Msg.CODERBOT_SENSOR_FINDFACE_SIZE = "taille";
Blockly.Msg.CODERBOT_SENSOR_FINDFACE_ALL = "x, y, taille (sous forme de liste)";
Blockly.Msg.CODERBOT_SENSOR_AVERAGE = "get image average";
Blockly.Msg.CODERBOT_SENSOR_AVERAGE_HUE = "Hue";
Blockly.Msg.CODERBOT_SENSOR_AVERAGE_SATURATION = "Saturation";
Blockly.Msg.CODERBOT_SENSOR_AVERAGE_VALUE = "Value (brightness)";
Blockly.Msg.CODERBOT_SENSOR_AVERAGE_ALL = "HSV (as list)";
Blockly.Msg.CODERBOT_SENSOR_FINDLOGO = "trouve le logo";
Blockly.Msg.CODERBOT_SENSOR_FINDCLASS = "trouve le class";
Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_FIND = "trouve le text";
Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_ACCEPT_ALPHA = "Alpha (A..Z)";
Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_ACCEPT_NUM = "Numeric (0..9)";
Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_ACCEPT_ALPHANUM = "Alphanumeric (A..Z;0..9)";
Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_ACCEPT_UNSPEC = "Any";
Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_COLOR = "background color";
Blockly.Msg.CODERBOT_SENSOR_FINDQRCODE = "trouve le Bar/QRCode";
Blockly.Msg.CODERBOT_SENSOR_FINDARCODE = "trouve le AR Code";
Blockly.Msg.CODERBOT_AUDIO_RECORD_FILE_NAME = "record as file";
Blockly.Msg.CODERBOT_AUDIO_RECORD_FILE_ELAPSE = " of seconds";
Blockly.Msg.CODERBOT_AUDIO_PLAY_FILE = "play file";
Blockly.Msg.CODERBOT_AUDIO_HEAR = "hear sound";
Blockly.Msg.CODERBOT_AUDIO_HEAR_LEVEL = " of level";
Blockly.Msg.CODERBOT_AUDIO_HEAR_ELAPSE = "for up to seconds";
Blockly.Msg.CODERBOT_AUDIO_LISTEN = "listen";
Blockly.Msg.CODERBOT_AUDIO_LISTEN_MODEL_SIMPLE = "simple commands";
Blockly.Msg.CODERBOT_AUDIO_LISTEN_MODEL_MEDIUM = "medium commands";
Blockly.Msg.CODERBOT_AUDIO_LISTEN_MODEL_ADV = "advance commands";
Blockly.Msg.CODERBOT_SONAR_GET_DISTANCE = "get distance with";
Blockly.Msg.CODERBOT_SONAR_SENSOR_1 = "sonar 1";
Blockly.Msg.CODERBOT_SONAR_SENSOR_2 = "sonar 2";
Blockly.Msg.CODERBOT_SONAR_SENSOR_3 = "sonar 3";
Blockly.Msg.CODERBOT_EVENT_WHEN = "when";
Blockly.Msg.CODERBOT_EVENT_WITH = "with";
Blockly.Msg.CODERBOT_EVENT_PUBLISH = "publish";
Blockly.Msg.CODERBOT_EVENT_ON_TOPIC = "on topic";
Blockly.Msg.CODERBOT_EVENT_GENERATOR = "event generator";
Blockly.Msg.CODERBOT_CONVERSATION_PARSE = "parse";

