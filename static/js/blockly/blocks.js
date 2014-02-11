/**
 * Blockly Apps: CoderBot Blocks
 *
 * Copyright 2012 Google Inc.
 * https://blockly.googlecode.com/
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @fileoverview Blocks for Blockly's CoderBot application.
 * @author fraser@google.com (Neil Fraser)
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
  return 'bot.forward(2);\n';
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
  return 'bot.backward(2);\n';
};

Blockly.Blocks['coderbot_turnLeft'] = {
  // Block for turning left or right.
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
  // Generate JavaScript for turning left or right.
  var dir = block.getFieldValue('DIR');
  return 'bot.left(1.8);\n';
};

Blockly.Blocks['coderbot_turnRight'] = {
  // Block for turning left or right.
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
  var dir = block.getFieldValue('DIR');
  return 'bot.right(1.8);\n';
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
