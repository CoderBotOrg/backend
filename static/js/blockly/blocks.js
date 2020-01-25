/**
  * CoderBot, a didactical, programmable robot
  * Copyright (C) 2014,2015  Roberto Previtera <info@coderbot.org>
  *
  * This program is free software: you can redistribute it and/or modify
  * it under the terms of the GNU General Public License as published by
  * the Free Software Foundation, either version 3 of the License.
  *
  * This program is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  *
  * You should have received a copy of the GNU General Public License
  * along with this program.  If not, see <http://www.gnu.org/licenses/>.
  */

'use strict';

Blockly.HSV_SATURATION=.99;
Blockly.HSV_VALUE=.99;

// Extensions to Blockly's language and Python generator.

Blockly.Blocks['coderbot_repeat'] = {
  /**
   * Block for repeat n times (internal number).
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.CONTROLS_REPEAT_HELPURL);
    this.setColour(120);
    var di = this.appendDummyInput();
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
    	di.appendField(new Blockly.FieldImage('/images/blocks/loop_repeat.png', 32, 32, '*'));
    } else {
        di.appendField(Blockly.Msg.CONTROLS_REPEAT_TITLE_REPEAT)
    }		
    di.appendField(new Blockly.FieldTextInput('10',
            Blockly.FieldTextInput.nonnegativeIntegerValidator), 'TIMES');
    if(CODERBOT_PROG_LEVEL.indexOf("basic")<0) {
        di.appendField(Blockly.Msg.CONTROLS_REPEAT_TITLE_TIMES);
    }
    var si = this.appendStatementInput('DO');
    if(CODERBOT_PROG_LEVEL.indexOf("basic")<0) {
    	si.appendField(Blockly.Msg.CONTROLS_REPEAT_INPUT_DO);
    }
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(Blockly.Msg.CONTROLS_REPEAT_TOOLTIP);
  }
};

Blockly.Python['coderbot_repeat'] = function(block) {
  // Repeat n times (internal number).
  var repeats = parseInt(block.getFieldValue('TIMES'), 10);
  var branch = Blockly.Python.statementToCode(block, 'DO');
  branch = Blockly.Python.addLoopTrap(branch, block.id) ||
      Blockly.Python.LOOP_PASS;
  var loopVar = Blockly.Python.variableDB_.getDistinctName(
      'count', Blockly.Variables.NAME_TYPE);
  var code = 'for ' + loopVar + ' in range(' + repeats + '):\n' + branch;
  return code;
};

Blockly.Python['text_print'] = function(block) {
  // Print statement.
  var argument0 = Blockly.Python.valueToCode(block, 'TEXT',
      Blockly.Python.ORDER_NONE) || '\'\'';
  return 'get_cam().set_text(' + argument0 + ')\n';
};


Blockly.Blocks['coderbot_moveForward'] = {
  // Block for moving forward.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Move');
    this.setColour(40);
    var di = this.appendDummyInput()
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
        di.appendField(new Blockly.FieldImage('/images/blocks/move_forward.png', 32, 32, '*'));
    } else {
        di.appendField(Blockly.Msg.CODERBOT_MOVE_FORWARD)
    }
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('CoderBot_moveForwardTooltip');
  }
};


Blockly.Python['coderbot_moveForward'] = function(block) {
  // Generate Python for moving forward.
  if(CODERBOT_PROG_MOVE_MOTION) {
    return 'get_motion().move(dist=' + CODERBOT_MOV_FW_DEF_ELAPSE + ')\n';

  } else {
    return 'get_bot().forward(speed=' + CODERBOT_MOV_FW_DEF_SPEED + ', elapse=' + CODERBOT_MOV_FW_DEF_ELAPSE + ')\n';
  }
};

Blockly.Blocks['coderbot_moveBackward'] = {
  // Block for moving forward.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Move');
    this.setColour(40);
    var di = this.appendDummyInput()
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
        di.appendField(new Blockly.FieldImage('/images/blocks/move_backward.png', 32, 32, '*'));
    } else {
        di.appendField(Blockly.Msg.CODERBOT_MOVE_BACKWARD)
    }
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('CoderBot_moveBackwardTooltip');
  }
};

Blockly.Python['coderbot_moveBackward'] = function(block) {
  // Generate Python for moving forward.
  if(CODERBOT_PROG_MOVE_MOTION) {    
    return 'get_motion().move(dist=' + (-CODERBOT_MOV_FW_DEF_ELAPSE) + ')\n';
    
  } else {
    return 'get_bot().backward(speed=' + CODERBOT_MOV_FW_DEF_SPEED + ', elapse=' + CODERBOT_MOV_FW_DEF_ELAPSE + ')\n';
  }
};

Blockly.Blocks['coderbot_turnLeft'] = {
  // Block for turning left.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Turn');
    this.setColour(40);
    var di = this.appendDummyInput()
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
        di.appendField(new Blockly.FieldImage('/images/blocks/move_left.png', 32, 32, '*'));
    } else {
        di.appendField(Blockly.Msg.CODERBOT_MOVE_LEFT);
    }
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_turnTooltip'));
  }
};

Blockly.Python['coderbot_turnLeft'] = function(block) {
  // Generate Python for turning left.
  if(CODERBOT_PROG_MOVE_MOTION) {
    return 'get_motion().turn(angle=' + (-CODERBOT_MOV_TR_DEF_ELAPSE) + ')\n';
  } else if(CODERBOT_PROG_MOVE_MPU) {
    return 'get_bot().turn_angle(speed=' + (-CODERBOT_MOV_TR_DEF_SPEED) + ', angle=' + CODERBOT_MOV_TR_DEF_ELAPSE + ')\n';
  } else {
    return 'get_bot().left(speed=' + CODERBOT_MOV_TR_DEF_SPEED + ', elapse=' + CODERBOT_MOV_TR_DEF_ELAPSE + ')\n';
  }
};

Blockly.Blocks['coderbot_turnRight'] = {
  // Block for turning right.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Turn');
    this.setColour(40);
    var di = this.appendDummyInput()
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
        di.appendField(new Blockly.FieldImage('/images/blocks/move_right.png', 32, 32, '*'));
    } else {
        di.appendField(Blockly.Msg.CODERBOT_MOVE_RIGHT)
    }
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_turnTooltip'));
  }
};

Blockly.Python['coderbot_turnRight'] = function(block) {
  // Generate Python for turning left or right.
  if(CODERBOT_PROG_MOVE_MOTION) {
    return 'get_motion().turn(angle=' + CODERBOT_MOV_TR_DEF_ELAPSE + ')\n';
  } else if(CODERBOT_PROG_MOVE_MPU) {
    return 'get_bot().turn_angle(speed=' + CODERBOT_MOV_TR_DEF_SPEED + ', angle=' + CODERBOT_MOV_TR_DEF_ELAPSE + ')\n';
  } else {
    return 'get_bot().right(speed=' + CODERBOT_MOV_TR_DEF_SPEED + ', elapse=' + CODERBOT_MOV_TR_DEF_ELAPSE + ')\n';
  } 
};

Blockly.Blocks['coderbot_audio_say'] = {
  // Block for text to speech.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Say');
    this.setColour(220);
    var vi = this.appendValueInput('TEXT');
    vi.setCheck(["String", "Number", "Date"]);
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
        vi.appendField(new Blockly.FieldImage('/images/blocks/say.png', 32, 32, '*'));
    } else {
    	vi.appendField(Blockly.Msg.CODERBOT_SAY);
    }
    vi.appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_LOCALE_EN, 'en'],
			                      [Blockly.Msg.CODERBOT_LOCALE_IT, 'it'],
                                              [Blockly.Msg.CODERBOT_LOCALE_FR, 'fr'],
					      [Blockly.Msg.CODERBOT_LOCALE_ES, 'es']]), 'LOCALE')

    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_sayTooltip'));
  }
};

Blockly.Python['coderbot_audio_say'] = function(block) {
  // Generate Python for turning left or right.
  var text = Blockly.Python.valueToCode(block, 'TEXT',
      Blockly.Python.ORDER_NONE) || '\'\'';
  var locale = block.getFieldValue('LOCALE');
  return 'get_audio().say(' + text + ', locale="' + locale + '")\n';
};

Blockly.Blocks['coderbot_sleep'] = {
  // Block for text to sleep.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Sleep');
    this.setColour(290);
    this.appendValueInput('ELAPSE')
        .setCheck(["Number"])
        .appendField(Blockly.Msg.CODERBOT_SLEEP);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_sleepTooltip'));
  }
};

Blockly.Python['coderbot_sleep'] = function(block) {
  // Generate Python for sleeping.
  var elapse = Blockly.Python.valueToCode(block, 'ELAPSE',
      Blockly.Python.ORDER_NONE) || '\'\'';
  return 'get_cam().sleep(' + elapse + ')\n';
};

Blockly.Blocks['coderbot_adv_move'] = {
  // Block for moving forward.
  init: function() {
    var ACTIONS =
        [[Blockly.Msg.CODERBOT_MOVE_ADV_TIP_FORWARD, 'FORWARD'],
        [Blockly.Msg.CODERBOT_MOVE_ADV_TIP_BACKWARD, 'BACKWARD'],
        [Blockly.Msg.CODERBOT_MOVE_ADV_TIP_LEFT, 'LEFT'],
        [Blockly.Msg.CODERBOT_MOVE_ADV_TIP_RIGHT, 'RIGHT']]
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Move');
    this.setColour(40);
    
    this.appendDummyInput("ACTION")
       .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_MOVE)
       .appendField(new Blockly.FieldDropdown(ACTIONS), 'ACTION');
    this.appendValueInput('SPEED')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_SPEED);
    this.appendValueInput('ELAPSE')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_ELAPSE);
    this.setInputsInline(true);
    // Assign 'this' to a variable for use in the tooltip closure below.
    var thisBlock = this;
    this.setTooltip(function() {
      var mode = thisBlock.getFieldValue('ACTION');
      var TOOLTIPS = {
        FORWARD: Blockly.Msg.CODERBOT_MOVE_ADV_TIP_FORWARD,
        BACKWARD: Blockly.Msg.CODERBOT_MOVE_ADV_TIP_BACKWARD,
        LEFT: Blockly.Msg.CODERBOT_MOVE_ADV_TIP_LEFT,
        RIGHT: Blockly.Msg.CODERBOT_MOVE_ADV_TIP_RIGHT,
      };
      return TOOLTIPS[mode] + Blockly.Msg.CODERBOT_MOVE_ADV_TIP_TAIL;
    });
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }
};

Blockly.Python['coderbot_adv_move'] = function(block) {
  // Generate Python for moving forward.
  var OPERATORS = {
    FORWARD: ['forward'],
    BACKWARD: ['backward'],
    LEFT: ['left'],
    RIGHT: ['right']
  };
  var tuple = OPERATORS[block.getFieldValue('ACTION')];
  var action = tuple[0];
  var speed = Blockly.Python.valueToCode(block, 'SPEED', Blockly.Python.ORDER_NONE);
  var elapse = Blockly.Python.valueToCode(block, 'ELAPSE', Blockly.Python.ORDER_NONE);
  var code = "get_bot()." + action + "(speed=" + speed + ", elapse="+elapse+")\n";
  return code;
};

Blockly.Blocks['coderbot_motion_move'] = {
  // Block for moving forward.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Move');
    this.setColour(40);

    this.appendValueInput('DIST')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_MOTION_MOVE + " " + Blockly.Msg.CODERBOT_MOVE_MOTION_DIST);
    this.setInputsInline(true);
    // Assign 'this' to a variable for use in the tooltip closure below.
    var thisBlock = this;
    this.setTooltip(function() {
      return Blockly.Msg.CODERBOT_MOVE_MOTION_MOVE_TIP;
    });
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }
};

Blockly.Python['coderbot_motion_move'] = function(block) {
  // Generate Python for moving forward.
  var dist = Blockly.Python.valueToCode(block, 'DIST', Blockly.Python.ORDER_NONE);
  var code = "get_motion().move(dist=" + dist + ")\n";
  return code;
};

Blockly.Blocks['coderbot_motion_turn'] = {
  // Block for moving forward.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Move');
    this.setColour(40);

    this.appendValueInput('ANGLE')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_MOTION_TURN + " " + Blockly.Msg.CODERBOT_MOVE_MOTION_ANGLE);
    this.setInputsInline(true);
    // Assign 'this' to a variable for use in the tooltip closure below.
    var thisBlock = this;
    this.setTooltip(function() {
      return Blockly.Msg.CODERBOT_MOVE_MOTION_TURN_TIP;
    });
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }
};

Blockly.Python['coderbot_motion_turn'] = function(block) {
  // Generate Python for moving forward.
  var angle = Blockly.Python.valueToCode(block, 'ANGLE', Blockly.Python.ORDER_NONE);
  var code = "get_motion().turn(angle=" + angle + ")\n";
  return code;
};

Blockly.Blocks['coderbot_adv_motor'] = {
  // Block for moving forward.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Motor');
    this.setColour(40);
    
    this.appendValueInput('SPEED_LEFT')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR + " " + Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_SPEED_LEFT);
    this.appendValueInput('SPEED_RIGHT')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_SPEED_RIGHT);
    this.appendValueInput('ELAPSE')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_ELAPSE);
    this.appendValueInput('STEPS_LEFT')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_STEPS_LEFT);
    this.appendValueInput('STEPS_RIGHT')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_STEPS_RIGHT);
    this.setInputsInline(true);
    // Assign 'this' to a variable for use in the tooltip closure below.
    var thisBlock = this;
    this.setTooltip(function() {
      var mode = thisBlock.getFieldValue('ACTION');
      return TOOLTIPS[mode] + Blockly.Msg.CODERBOT_MOVE_ADV_TIP_TAIL;
    });
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }
};

Blockly.Python['coderbot_adv_motor'] = function(block) {
  // Generate Python for moving forward.
  var speed_left = Blockly.Python.valueToCode(block, 'SPEED_LEFT', Blockly.Python.ORDER_NONE);
  var speed_right = Blockly.Python.valueToCode(block, 'SPEED_RIGHT', Blockly.Python.ORDER_NONE);
  var elapse = Blockly.Python.valueToCode(block, 'ELAPSE', Blockly.Python.ORDER_NONE);
  var steps_left = Blockly.Python.valueToCode(block, 'STEPS_LEFT', Blockly.Python.ORDER_NONE);
  var steps_right = Blockly.Python.valueToCode(block, 'STEPS_RIGHT', Blockly.Python.ORDER_NONE);
  var code = "get_bot().motor_control(speed_left=" + speed_left + ", speed_right=" + speed_right + ", elapse=" + elapse + ", steps_left=" + steps_left + ", steps_right=" + steps_right + ")\n";
  return code;
};

Blockly.Blocks['coderbot_adv_move_enc'] = {
  // Block for moving forward.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Motor');
    this.setColour(40);
    
    this.appendValueInput('SPEED')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR + " " + Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_SPEED);
    this.appendValueInput('DISTANCE')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_MOVE_ADV_MOTOR_DISTANCE);
    this.setInputsInline(true);
    // Assign 'this' to a variable for use in the tooltip closure below.
    var thisBlock = this;
    this.setTooltip(function() {
      var mode = thisBlock.getFieldValue('ACTION');
      return TOOLTIPS[mode] + Blockly.Msg.CODERBOT_MOVE_ADV_TIP_TAIL;
    });
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }
};

Blockly.Python['coderbot_adv_move_enc'] = function(block) {
  // Generate Python for moving forward.
  var speed = Blockly.Python.valueToCode(block, 'SPEED', Blockly.Python.ORDER_NONE);
  var distance = Blockly.Python.valueToCode(block, 'DISTANCE', Blockly.Python.ORDER_NONE);
  var code = "get_bot().move(speed=" + speed + ", distance=" + distance + ")\n";
  return code;
};

Blockly.Blocks['coderbot_adv_stop'] = {
  // Block to stop the get_bot().
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Stop');
    this.setColour(40);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_MOVE_STOP);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_stopTooltip'));
  }
};

Blockly.Python['coderbot_adv_stop'] = function(block) {
  // Generate Python to stop the get_bot().
  return 'get_bot().stop()\n';
};


Blockly.Blocks['coderbot_camera_photoTake'] = {
  // Block for taking a picture.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Turn');
    this.setColour(120);
    var di = this.appendDummyInput()
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
        di.appendField(new Blockly.FieldImage('/images/blocks/photo_take.png', 32, 32, '*'));
    } else {
        di.appendField(Blockly.Msg.CODERBOT_PHOTO_TAKE)
    }
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_PhotoTooltip'));
  }
};

Blockly.Python['coderbot_camera_photoTake'] = function(block) {
  // Generate Python for turning left or right.
  return 'get_cam().photo_take()\n';
};

Blockly.Blocks['coderbot_camera_videoRec'] = {
  // Block for recording a video (start).
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Turn');
    this.setColour(120);

    var di = this.appendDummyInput()
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
        di.appendField(new Blockly.FieldImage('/images/blocks/video_rec.png', 32, 32, '*'));
    } else {
        di.appendField(Blockly.Msg.CODERBOT_VIDEO_REC)
    }
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_VideoTooltip'));
  }
};

Blockly.Python['coderbot_camera_videoRec'] = function(block) {
  // Generate Python for turning left or right.
  return 'get_cam().video_rec()\n';
};

Blockly.Blocks['coderbot_camera_videoStop'] = {
  // Block for recording a video (stop).
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Turn');
    this.setColour(120);

    var di = this.appendDummyInput()
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
        di.appendField(new Blockly.FieldImage('/images/blocks/video_stop.png', 32, 32, '*'));
    } else {
        di.appendField(Blockly.Msg.CODERBOT_VIDEO_STOP)
    }
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_VideoTooltip'));
  }
};

Blockly.Python['coderbot_camera_videoStop'] = function(block) {
  // Generate Python for turning left or right.
  return 'get_cam().video_stop()\n';
};

Blockly.Blocks['coderbot_adv_pathAhead'] = {
  /**
   * Block for pathAhead function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_PATHAHEAD);
    this.setOutput(true, 'Number');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_pathAhead'] = function(block) {
  // Boolean values true and false.
  var code = 'get_cam().path_ahead()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_findLine'] = {
  /**
   * Block for pathAhead function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDLINE);
    this.setOutput(true, 'Array');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_findLine'] = function(block) {
  // Boolean values true and false.
  var code = 'get_cam().find_line()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_findSignal'] = {
  /**
   * Block for findSignal function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDSIGNAL);
    this.setOutput(true, 'Number');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_findSignal'] = function(block) {
  // Boolean values true and false.
  var code = 'get_cam().find_signal()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_findFace'] = {
  /**
   * Block for findSignal function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDFACE)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_SENSOR_FINDFACE_X, 'X'], [Blockly.Msg.CODERBOT_SENSOR_FINDFACE_Y, 'Y'],[Blockly.Msg.CODERBOT_SENSOR_FINDFACE_SIZE, 'SIZE'],[Blockly.Msg.CODERBOT_SENSOR_FINDFACE_ALL,'ALL']]), 'RETVAL')
    this.setInputsInline(true);
    this.setOutput(true, ['Number', 'Array']);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_findFace'] = function(block) {
  // Boolean values true and false.
  var retval = block.getFieldValue('RETVAL');
  var ret_code = {'X': '[0]', 'Y': '[1]', 'SIZE': '[2]', 'ALL': ''}[retval];
  var code = 'get_cam().find_face()' + ret_code;
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_findColor'] = {
  /**
   * Block for findSignal function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_FIND)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_DIST, 'DIST'], [Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_ANGLE, 'ANGLE'],[Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_BOTH,'BOTH']]), 'RETVAL')
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDCOLOR_COLOR);
    this.appendValueInput('COLOR')
        .setCheck(['Colour','String']);
    this.setInputsInline(true);
    this.setOutput(true, ['Number', 'Array']);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_findColor'] = function(block) {
  // Boolean values true and false.
  var color = Blockly.Python.valueToCode(block, 'COLOR', Blockly.Python.ORDER_NONE);
  var retval = block.getFieldValue('RETVAL');
  var ret_code = {'DIST': '[0]', 'ANGLE': '[1]', 'BOTH': ''}[retval];
  var code = 'get_cam().find_color(' + color + ')' + ret_code;
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_cam_average'] = {
  /**
   * Block for image.get_average() function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_AVERAGE)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_SENSOR_AVERAGE_HUE, 'H'], 
                                                [Blockly.Msg.CODERBOT_SENSOR_AVERAGE_SATURATION, 'S'],
                                                [Blockly.Msg.CODERBOT_SENSOR_AVERAGE_VALUE, 'V'],
                                                [Blockly.Msg.CODERBOT_SENSOR_AVERAGE_ALL,'ALL']]), 'RETVAL')
    this.setInputsInline(true);
    this.setOutput(true, ['Number', 'Array']);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_cam_average'] = function(block) {
  // Boolean values true and false.
  var retval = block.getFieldValue('RETVAL');
  var ret_code = {'H': '[0]', 'S': '[1]', 'V': '[2]', 'ALL': ''}[retval];
  var code = 'get_cam().get_average()' + ret_code;
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_findText'] = {
  /**
   * Block for findText function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_FIND)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_ACCEPT_ALPHA, 'alpha'], 
                                                [Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_ACCEPT_NUM, 'num'],
                                                [Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_ACCEPT_ALPHANUM,'alphanum'],
                                                [Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_ACCEPT_UNSPEC,'unspec']]), 'ACCEPT')
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDTEXT_COLOR);
    this.appendValueInput('COLOR')
        .setCheck(['Colour','String']);
    this.setInputsInline(true);
    this.setOutput(true, ['Number', 'Array']);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_findText'] = function(block) {
  // Boolean values true and false.
  var accept = block.getFieldValue('ACCEPT');
  var color = Blockly.Python.valueToCode(block, 'COLOR', Blockly.Python.ORDER_NONE);
  var code = 'get_cam().find_text(accept="' + accept + '", back_color=' + color  + ')';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_findQRCode'] = {
  /**
   * Block for findText function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDQRCODE);
    this.setOutput(true, 'String');
    this.setInputsInline(true);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_findQRCode'] = function(block) {
  // Boolean values true and false.
  var code = 'get_cam().find_qr_code()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_findARCode'] = {
  /**
   * Block for findText function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDARCODE);
    this.setOutput(true, 'HashMap');
    this.setInputsInline(true);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_findARCode'] = function(block) {
  // Boolean values true and false.
  var code = 'get_cam().find_ar_code()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_findLogo'] = {
  /**
   * Block for findLogo function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDLOGO);
    this.setOutput(true, 'Number');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_findLogo'] = function(block) {
  // Boolean values true and false.
  var code = 'get_cam().find_logo()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_find_class'] = {
  /**
   * Block for find_class function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDCLASS);
    this.setOutput(true, 'String');
    this.setInputsInline(true);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_find_class'] = function(block) {
  // Boolean values true and false.
  var name = 'get_cam().find_class()';
  return [name, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_cnn_classify'] = {
  /**
   * Block for find_class function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDCLASS)
        .appendField(new Blockly.FieldDropdown(CODERBOT_CNN_MODEL_LIST), 'MODEL');
    this.setInputsInline(true);
    this.setOutput(true, ['Array']);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_cnn_classify'] = function(block) {
  var model = block.getFieldValue('MODEL');
  var class_scores = 'get_cam().cnn_classify("'+ model +'")';
  return [class_scores, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_adv_cnn_detect_objects'] = {
  /**
   * Block for find_class function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SENSOR_FINDOBJECTS)
        .appendField(new Blockly.FieldDropdown(CODERBOT_CNN_MODEL_LIST), 'MODEL');
    this.setInputsInline(true);
    this.setOutput(true, ['Array']);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_adv_cnn_detect_objects'] = function(block) {
  var model = block.getFieldValue('MODEL');
  var class_scores = 'get_cam().cnn_detect_objects("'+ model +'")';
  return [class_scores, Blockly.Python.ORDER_ATOMIC];
};


Blockly.Blocks['coderbot_event_generator'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_EVENT_GENERATOR);
    this.appendStatementInput("generator_statements")
        .setCheck(null);
    this.setColour(15);
 this.setTooltip("event generator");
 this.setHelpUrl("");
  }
};

var coderbot_generator_id = 1;
Blockly.Python['coderbot_event_generator'] = function(block) {
  Blockly.Generator.prototype.INDENT = '    ';
  var statements_event_generator = Blockly.Python.statementToCode(block, 'generator_statements');
  Blockly.Generator.prototype.INDENT = '  ';
  var code = 'def event_generator_' + coderbot_generator_id + '():\n' +
             '  while True:\n' +
             '    get_prog_eng().check_end()\n' +
             statements_event_generator + '\n' + 
             'get_event().register_event_generator(event_generator_' + coderbot_generator_id + ')'
  coderbot_generator_id++;
  return code;
};

Blockly.Blocks['coderbot_event_listener'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_EVENT_WHEN)
        .appendField(new Blockly.FieldTextInput("event_topic"), "event_topic")
        .appendField(Blockly.Msg.CODERBOT_EVENT_WITH + " event_data");
    this.appendStatementInput("event_statements")
        .setCheck(null);
    this.setInputsInline(true);
    this.setColour(15);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

var coderbot_listener_id = 1;
Blockly.Python['coderbot_event_listener'] = function(block) {
  var event_topic = block.getFieldValue('event_topic');
  var event_statements = Blockly.Python.statementToCode(block, 'event_statements');
  var code = 'def event_listener_' + coderbot_listener_id + '(message):\n' +
             Blockly.Generator.prototype.INDENT + 'event_data = json.loads(message)\n' +
             event_statements + '\n' +
             'get_event().register_event_listener(\'' + event_topic + '\', event_listener_' + coderbot_listener_id + ')'
  coderbot_listener_id++; 
  return code;
};

Blockly.Blocks['coderbot_event_publisher'] = {
  init: function() {
    this.appendValueInput("event_data")
        .appendField(Blockly.Msg.CODERBOT_EVENT_PUBLISH)
        .setCheck(null);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_EVENT_ON_TOPIC)
        .appendField(new Blockly.FieldTextInput("event_topic"), "event_topic");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(15);
 this.setTooltip("event publisher");
 this.setHelpUrl("");
  }
};

Blockly.Python['coderbot_event_publisher'] = function(block) {
  var event_topic = block.getFieldValue('event_topic');
  var event_data = Blockly.Python.valueToCode(block, 'event_data', Blockly.Python.ORDER_ATOMIC);
  var code = 'get_event().publish(\'' + event_topic + '\', json.dumps(' + event_data + '))\n';
  return code;
};

Blockly.Blocks['hashmap_get_value'] = {
  init: function() {
    this.appendValueInput("key")
        .setCheck("String")
        .appendField("get");
    this.appendValueInput("map")
        .setCheck("HashMap")
        .appendField("from ");
    this.setInputsInline(true);
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("get an item from an hashmap");
 this.setHelpUrl("");
  }
};

Blockly.Python['hashmap_get_value'] = function(block) {
  var value_key = Blockly.Python.valueToCode(block, 'key', Blockly.Python.ORDER_ATOMIC);
  var value_map = Blockly.Python.valueToCode(block, 'map', Blockly.Python.ORDER_ATOMIC);
  var code = value_map + '.get(' + value_key + ')';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Blocks['hashmap_get_keys'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("get keys");
    this.appendValueInput("map")
        .setCheck("HashMap")
        .appendField("from ");
    this.setInputsInline(true);
    this.setOutput(true, "Array");
    this.setColour(230);
 this.setTooltip("get keys from an hashmap");
 this.setHelpUrl("");
  }
};

Blockly.Python['hashmap_get_keys'] = function(block) {
  var value_map = Blockly.Python.valueToCode(block, 'map', Blockly.Python.ORDER_ATOMIC);
  var code = value_map + '.keys()';
  return [code, Blockly.Python.ORDER_NONE];
};


Blockly.Blocks['coderbot_conv_get_action'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_CONVERSATION_PARSE);
    this.appendValueInput("query")
        .setCheck("String");
    this.appendDummyInput()
        .appendField("in")
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_LOCALE_EN, 'en'],
                                                [Blockly.Msg.CODERBOT_LOCALE_IT, 'it'],
                                                [Blockly.Msg.CODERBOT_LOCALE_FR, 'fr'],
                                                [Blockly.Msg.CODERBOT_LOCALE_ES, 'es']]), "locale");
    this.setInputsInline(true);
    this.setOutput(true, "HashMap");
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.Python['coderbot_conv_get_action'] = function(block) {
  var value_query = Blockly.Python.valueToCode(block, 'query', Blockly.Python.ORDER_ATOMIC);
  var dropdown_locale = block.getFieldValue('locale');
  var code = 'get_conv().get_action(query=' + value_query + ', locale=\'' + dropdown_locale + '\')';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Blocks['coderbot_audio_record'] = {
  /**
   * Block for findLogo function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(220);
    this.appendValueInput('FILENAME')
        .setCheck('String')
        .appendField(Blockly.Msg.CODERBOT_AUDIO_RECORD_FILE_NAME);
    this.appendValueInput('ELAPSE')
        .setCheck('Number')
        .appendField(Blockly.Msg.CODERBOT_AUDIO_RECORD_FILE_ELAPSE);
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_audio_record_Tooltip'));
  }
};

Blockly.Python['coderbot_audio_record'] = function(block) {

  var filename = Blockly.Python.valueToCode(block, 'FILENAME',
      Blockly.Python.ORDER_NONE) || '\'\'';
  var elapse = Blockly.Python.valueToCode(block, 'ELAPSE',
      Blockly.Python.ORDER_NONE) || '\'\'';
  var code = 'get_audio().record_to_file(filename=' + filename + ', elapse=' + elapse + ')\n';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_audio_play'] = {
  // Block for text to speech.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Play');
    this.setColour(220);
    var vi = this.appendValueInput('FILENAME');
    vi.setCheck("String");
    if(CODERBOT_PROG_LEVEL.indexOf("basic")>=0) {
        vi.appendField(new Blockly.FieldImage('/images/blocks/play.png', 32, 32, '*'));
    } else {
        vi.appendField(Blockly.Msg.CODERBOT_AUDIO_PLAY_FILE);
    }
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_audio_play_Tooltip'));
  }
};

Blockly.Python['coderbot_audio_play'] = function(block) {
  // Generate Python for turning left or right.
  var filename = Blockly.Python.valueToCode(block, 'FILENAME',
      Blockly.Python.ORDER_NONE) || '\'\'';
  return 'get_audio().play(' + filename + ')\n';
};

Blockly.Blocks['coderbot_audio_hear'] = {
  /**
   * Block for audio hear function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(220);
    this.appendValueInput('LEVEL')
        .setCheck(["Number"])
        .appendField(Blockly.Msg.CODERBOT_AUDIO_HEAR + Blockly.Msg.CODERBOT_AUDIO_HEAR_LEVEL);
    this.appendValueInput('ELAPSE')
        .setCheck(["Number"])
        .appendField(Blockly.Msg.CODERBOT_AUDIO_HEAR_ELAPSE);
    this.setInputsInline(true);
    this.setOutput(true, ['Number']);
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_audio_hear'] = function(block) {
  // Boolean values true and false.
  var level = Blockly.Python.valueToCode(block, 'LEVEL', Blockly.Python.ORDER_NONE) || '\'\'';
  var elapse = Blockly.Python.valueToCode(block, 'ELAPSE', Blockly.Python.ORDER_NONE) || '\'\'';
  var code = 'get_audio().hear(level=' + level + ', elapse=' + elapse  + ')';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_audio_listen'] = {
  /**
   * Block for findText function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(220);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_AUDIO_LISTEN)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_LOCALE_EN, 'en-US'],
                                                [Blockly.Msg.CODERBOT_LOCALE_IT, 'it-IT'],
                                                [Blockly.Msg.CODERBOT_LOCALE_FR, 'fr-FR'],
                                                [Blockly.Msg.CODERBOT_LOCALE_ES, 'es-ES']]), 'MODEL');
    this.setInputsInline(true);
    this.setOutput(true, 'String');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_audio_listen'] = function(block) {
  // Boolean values true and false.
  var model = block.getFieldValue('MODEL');
  var code = 'get_audio().speech_recog_google(locale=\'' + model + '\')';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_sonar_get_distance'] = {
  /**
   * Block for get_distance function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(250);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_SONAR_GET_DISTANCE)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_SONAR_SENSOR_1, "0"],
                                                [Blockly.Msg.CODERBOT_SONAR_SENSOR_2, "1"],
                                                [Blockly.Msg.CODERBOT_SONAR_SENSOR_3, "2"],
                                                [Blockly.Msg.CODERBOT_SONAR_SENSOR_4, "3"]]), 'SONAR');
    this.setOutput(true, 'Number');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_sonar_get_distance'] = function(block) {
  // Boolean values true and false.
  var sonar = block.getFieldValue('SONAR');
  var code = 'get_bot().get_sonar_distance(' + sonar + ')';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_mpu_get_accel'] = {
  /**
   * Block for get_distance function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(240);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_MPU_GET_ACCEL)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_MPU_AXIS_X, "0"],
                                                [Blockly.Msg.CODERBOT_MPU_AXIS_Y, "1"],
                                                [Blockly.Msg.CODERBOT_MPU_AXIS_Z, "2"]]), 'AXIS');
    this.setOutput(true, 'Number');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_mpu_get_accel'] = function(block) {
  // Boolean values true and false.
  var axis = block.getFieldValue('AXIS');
  var code = 'get_bot().get_mpu_accel(' + axis + ')';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_mpu_get_gyro'] = {
  /**
   * Block for get_distance function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(240);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_MPU_GET_GYRO)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.CODERBOT_MPU_AXIS_X, "0"],
                                                [Blockly.Msg.CODERBOT_MPU_AXIS_Y, "1"],
                                                [Blockly.Msg.CODERBOT_MPU_AXIS_Z, "2"]]), 'AXIS');
    this.setOutput(true, 'Number');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_mpu_get_gyro'] = function(block) {
  // Boolean values true and false.
  var axis = block.getFieldValue('AXIS');
  var code = 'get_bot().get_mpu_gyro(' + axis + ')';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_mpu_get_heading'] = {
  /**
   * Block for get_distance function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(240);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_MPU_GET_HEADING);
    this.setOutput(true, 'Number');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_mpu_get_heading'] = function(block) {
  // Boolean values true and false.
  var code = 'get_bot().get_mpu_heading()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['coderbot_mpu_get_temp'] = {
  /**
   * Block for get_distance function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(240);
    this.appendDummyInput()
        .appendField(Blockly.Msg.CODERBOT_MPU_GET_TEMP);
    this.setOutput(true, 'Number');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.Python['coderbot_mpu_get_temp'] = function(block) {
  // Boolean values true and false.
  var code = 'get_bot().get_mpu_temp()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};
