/**
  * Copyright (C) 2014 Roberto Previtera
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

// Extensions to Blockly's language and JavaScript generator.

Blockly.Blocks['coderbot_moveForward'] = {
  // Block for moving forward.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Move');
    this.setColour(290);
    this.appendDummyInput()
        .appendField('moveForward');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('CoderBot_moveForwardTooltip');
  }
};

Blockly.JavaScript['coderbot_moveForward'] = function(block) {
  // Generate JavaScript for moving forward.
  return 'bot.forward(elapse=0.25);\n';
};

Blockly.Python['coderbot_moveForward'] = function(block) {
  // Generate Python for moving forward.
  return 'bot.forward(elapse=0.25)\n';
};

Blockly.Blocks['coderbot_moveBackward'] = {
  // Block for moving forward.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Move');
    this.setColour(290);
    this.appendDummyInput()
        .appendField('moveBackward');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('CoderBot_moveBackwardTooltip');
  }
};

Blockly.JavaScript['coderbot_moveBackward'] = function(block) {
  // Generate JavaScript for moving forward.
  return 'bot.backward(elapse=0.25);\n';
};

Blockly.Python['coderbot_moveBackward'] = function(block) {
  // Generate Python for moving forward.
  return 'bot.backward(elapse=0.25)\n';
};

Blockly.Blocks['coderbot_turnLeft'] = {
  // Block for turning left.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Turn');
    this.setColour(290);
    this.appendDummyInput()
        .appendField("turnLeft");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_turnTooltip'));
  }
};

Blockly.JavaScript['coderbot_turnLeft'] = function(block) {
  // Generate JavaScript for turning left.
  return 'bot.left(elapse=0.15);\n';
};

Blockly.Python['coderbot_turnLeft'] = function(block) {
  // Generate Python for turning left.
  return 'bot.left(elapse=0.15)\n';
};

Blockly.Blocks['coderbot_turnRight'] = {
  // Block for turning right.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Turn');
    this.setColour(290);
    this.appendDummyInput()
        .appendField("turnRight");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_turnTooltip'));
  }
};

Blockly.JavaScript['coderbot_turnRight'] = function(block) {
  // Generate JavaScript for turning left or right.
  return 'bot.right(elapse=0.15);\n';
};

Blockly.Python['coderbot_turnRight'] = function(block) {
  // Generate Python for turning left or right.
  return 'bot.right(elapse=0.15)\n';
};

Blockly.Blocks['coderbot_say'] = {
  // Block for text to speech.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Say');
    this.setColour(290);
    this.appendValueInput('TEXT')
        .setCheck(["String", "Number", "Date"])
        .appendField('say');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_sayTooltip'));
  }
};

Blockly.JavaScript['coderbot_say'] = function(block) {
  // Generate JavaScript for turning left or right.
  var text = Blockly.JavaScript.valueToCode(block, 'TEXT',
      Blockly.JavaScript.ORDER_NONE) || '\'\'';
  return 'bot.say(' + text + ');\n';
};

Blockly.Python['coderbot_say'] = function(block) {
  // Generate Python for turning left or right.
  var text = Blockly.Python.valueToCode(block, 'TEXT',
      Blockly.Python.ORDER_NONE) || '\'\'';
  return 'bot.say(' + text + ')\n';
};

Blockly.Blocks['coderbot_adv_move'] = {
  // Block for moving forward.
  init: function() {
    var ACTIONS =
        [['forward', 'FORWARD'],
        ['backward', 'BACKWARD'],
        ['left', 'LEFT'],
        ['right', 'RIGHT']]
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Move');
    this.setColour(290);
    this.interpolateMsg("move bot ",
                        ['TEXT', null, Blockly.ALIGN_RIGHT],
                        Blockly.ALIGN_RIGHT);
    
    this.appendDummyInput("ACTION")
       .appendField(new Blockly.FieldDropdown(ACTIONS), 'ACTION');
    this.appendValueInput('SPEED')
        .setCheck('Number')
        .appendField(" at speed: ");
    this.appendValueInput('ELAPSE')
        .setCheck('Number')
        .appendField(" for: ");
    this.setInputsInline(true);
    // Assign 'this' to a variable for use in the tooltip closure below.
    var thisBlock = this;
    this.setTooltip(function() {
      var mode = thisBlock.getFieldValue('ACTION');
      var TOOLTIPS = {
        FORWARD: "Move forward",
        BACKWARD: "Move backward",
        LEFT: "Turn left",
        RIGHT: "Turn right",
      };
      return TOOLTIPS[mode] + " at speed (0-100%) for time (seconds)";
    });
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }
};

Blockly.JavaScript['coderbot_adv_move'] = function(block) {
  // Generate JavaScript for moving forward.
  return 'bot.forward();\n';
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
  var code = "bot." + action + "(speed=" + speed + ", elapse="+elapse+")\n";
  return code;
};

Blockly.Blocks['coderbot_adv_stop'] = {
  // Block to stop the bot.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Stop');
    this.setColour(290);
    this.appendDummyInput()
        .appendField("stop");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(('CoderBot_stopTooltip'));
  }
};

Blockly.JavaScript['coderbot_adv_stop'] = function(block) {
  // Generate JavaScript to stop the bot.
  return 'bot.stop();\n';
};

Blockly.Python['coderbot_adv_stop'] = function(block) {
  // Generate Python to stop the bot.
  return 'bot.stop()\n';
};


Blockly.Blocks['coderbot_adv_pathAhead'] = {
  /**
   * Block for pathAhead function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.LOGIC_BOOLEAN_HELPURL);
    this.setColour(210);
    this.appendDummyInput()
        .appendField('pathAhead');
    this.setOutput(true, 'Boolean');
    this.setTooltip(Blockly.Msg.LOGIC_BOOLEAN_TOOLTIP);
  }
};

Blockly.JavaScript['coderbot_adv_pathAhead'] = function(block) {
  // Boolean values true and false.
  var code = 'cam.path_ahead()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Python['coderbot_adv_pathAhead'] = function(block) {
  // Boolean values true and false.
  var code = 'cam.path_ahead()';
  return [code, Blockly.Python.ORDER_ATOMIC];
};


Blockly.Blocks['coderbot_if'] = {
  // Block for 'if' conditional if there is a path.
  init: function() {
    var DIRECTIONS =
        [['CoderBot_pathAhead', 'isPathForward'],
         ['CoderBot_pathLeft', 'isPathLeft'],
         ['CoderBot_pathRight', 'isPathRight']];
    this.setColour(210);
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown(DIRECTIONS), 'DIR');
    this.appendStatementInput('DO')
        .appendField('CoderBot_doCode');
    this.setTooltip('CoderBot_ifTooltip');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }
};


Blockly.JavaScript['coderbot_if'] = function(block) {
  // Generate JavaScript for 'if' conditional if there is a path.
  var argument = 'CoderBot.' + block.getFieldValue('DIR') +
      '(\'block_id_' + block.id + '\')';
  var branch = Blockly.JavaScript.statementToCode(block, 'DO');
  var code = 'if (' + argument + ') {\n' + branch + '}\n';
  return code;
};

Blockly.Blocks['coderbot_ifElse'] = {
  // Block for 'if/else' conditional if there is a path.
  init: function() {
    var DIRECTIONS =
        [[('CoderBot_pathAhead'), 'isPathForward'],
         [('CoderBot_pathLeft'), 'isPathLeft'],
         [('CoderBot_pathRight'), 'isPathRight']];
    this.setColour(210);
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown(DIRECTIONS), 'DIR');
    this.appendStatementInput('DO')
        .appendField(('CoderBot_doCode'));
    this.appendStatementInput('ELSE')
        .appendField(('CoderBot_elseCode'));
    this.setTooltip(('CoderBot_ifelseTooltip'));
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }
};

Blockly.JavaScript['coderbot_ifElse'] = function(block) {
  // Generate JavaScript for 'if/else' conditional if there is a path.
  var argument = 'CoderBot.' + block.getFieldValue('DIR') +
      '(\'block_id_' + block.id + '\')';
  var branch0 = Blockly.JavaScript.statementToCode(block, 'DO');
  var branch1 = Blockly.JavaScript.statementToCode(block, 'ELSE');
  var code = 'if (' + argument + ') {\n' + branch0 +
             '} else {\n' + branch1 + '}\n';
  return code;
};

Blockly.Blocks['coderbot_forever'] = {
  // Do forever loop.
  init: function() {
    this.setHelpUrl('http://code.google.com/p/blockly/wiki/Repeat');
    this.setColour(120);
    this.appendDummyInput()
        .appendField(('CoderBot_repeatUntil'))
        .appendField(new Blockly.FieldImage(CoderBot.SKIN.marker, 12, 16));
    this.appendStatementInput('DO')
        .appendField(('CoderBot_doCode'));
    this.setPreviousStatement(true);
    this.setTooltip(('CoderBot_whileTooltip'));
  }
};

Blockly.JavaScript['coderbot_forever'] = function(block) {
  // Generate JavaScript for do forever loop.
  var branch = Blockly.JavaScript.statementToCode(block, 'DO');
  if (Blockly.JavaScript.INFINITE_LOOP_TRAP) {
    branch = Blockly.JavaScript.INFINITE_LOOP_TRAP.replace(/%1/g,
        '\'block_id_' + block.id + '\'') + branch;
  }
  return 'while (true) {\n' + branch + '}\n';
};
