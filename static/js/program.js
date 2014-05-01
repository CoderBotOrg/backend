    $(document).ready(function() {
      Blockly.inject(document.getElementById('blocklyDiv'),
          {path: '../../', toolbox: document.getElementById('toolbox')});
      $("#b_new_prog").on("click", newProg).on("touchend",newProg);
      $("#b_load_prog").on("click", loadProg).on("touchend",loadProg);
      $("#b_save_prog").on("click", saveProg).on("touchend",saveProg);
      $("#b_show_prog").on("click", showProg).on("touchend",showProg);
      $("#b_run_prog").on("click", runProg).on("touchend",runProg);
      $("#b_end_prog").on("click", endProg).on("touchend",endProg);
      $("#b_new_prog_post").on("click", newProgPost);
      $("#b_load_prog_post").on("click", loadProgPost);
      $("#b_control").on("click", goControl).on("touchend",goControl);
    });

    var prog = {};

    function newProg() {
      $("#dialogNewProgLnk").click();
    }

    function newProgPost() {
      $("#dialogNewProg").popup("close");
      Blockly.mainWorkspace.clear();
      prog.name=$("#i_new_prog_name").val();
    }

    function loadProg() {
      $("#dialogLoadProgLnk").click();
    }

    function loadProgPost() {
      $("#dialogLoadProg").popup("close");
      Blockly.mainWorkspace.clear();
      prog.name=$("#i_load_prog_name").val();
      try {
        var data =  {'name': prog.name};
        $.ajax({url: '/program/load', data: data, type: "GET", success:function(data) {
	  Blockly.mainWorkspace.clear();
          var xml = Blockly.Xml.textToDom(data);
          Blockly.Xml.domToWorkspace(Blockly.mainWorkspace, xml);
	}});
      } catch (e) {
        alert(e);
      }
    }

    function saveProg() {
      // Generate Dom code and display it.
      Blockly.JavaScript.INFINITE_LOOP_TRAP = null;
      var xml_code = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
      var code = Blockly.Xml.domToText(xml_code);
      var data =  {'name': prog.name, 'dom_code': code};
      $.ajax({url: '/program/save', data: data, type: "POST", success:function() {
	  alert('saved ok');
	}});
    }

    function showProg() {
      // Generate JavaScript code and display it.
      Blockly.JavaScript.INFINITE_LOOP_TRAP = null;
      var code = Blockly.Python.workspaceToCode();
      alert(code);
    }

    function runProg() {
      var bot = new CoderBot();
      // Generate JavaScript code and run it.
      window.LoopTrap = 1000;
      Blockly.Python.INFINITE_LOOP_TRAP = '  program.check_end()\n';
      var code = Blockly.Python.workspaceToCode();
      Blockly.Python.INFINITE_LOOP_TRAP = null;
      try {
        var data =  {'name': 'one',
                     'code': code};
        $.ajax({url: '/program/exec', data: data, type: "POST"});
        $('#popupRunningLnk').click();
      } catch (e) {
        alert(e);
      }
    }
    function endProg() {
        $.ajax({url: '/program/end', type: "POST"});
    }
    function goControl() {
      $.mobile.changePage("/");
    }
