    $(document).ready(function() {
      Blockly.inject(document.getElementById('blocklyDiv'),
          {path: '../../', toolbox: document.getElementById('toolbox')});
      $("#b_new_prog").on("click", newProg).on("touchend",newProg);
      $("#b_load_prog").on("click", loadProg).on("touchend",loadProg);
      $("#b_save_prog").on("click", saveProg).on("touchend",saveProg);
      $("#b_show_prog").on("click", showProg).on("touchend",showProg);
      $("#b_run_prog").on("click", runProg).on("touchend",runProg);
      $("#b_end_prog").on("click", endProg).on("touchend",endProg);
      $("#b_end_prog_d").on("click", endProg).on("touchend",endProg);
      $("#b_new_prog_post").on("click", newProgPost);
      $("#b_load_prog_post").on("click", loadProgPost);
      $("#b_control").on("click", goControl).on("touchend",goControl);
    });

    var prog = {};

    function newProg() {
      $("#dialogNewProg").popup("open", {transition: "pop"});
    }

    function newProgPost() {
      $("#dialogNewProg").popup("close");
      Blockly.mainWorkspace.clear();
      prog.name=$("#i_new_prog_name").val();
    }

    function loadProg() {
      try {
        $.ajax({url: '/program/list', dataType: "json", type: "GET", success:function(data) {
          $('#i_prog_list').empty();
          for(i in data) {
            var name = data[i];
            $('#i_prog_list').append('<li data-prog-name="' + name +'"><a href="#" class="c_load_prog"><h2>'+name+'</h2></a><a href="#" class="c_delete_prog">Delete program</a></li>');
          }
          $('#i_prog_list').listview('refresh'); 
          $('.c_load_prog').on('click', loadProgPost);
          $('.c_delete_prog').on('click', deleteProg);
          $("#dialogLoadProg").popup("open", {transition: "pop"});
	}});
      } catch (e) {
        alert(e);
      }      
    }

    function loadProgPost() {
      Blockly.mainWorkspace.clear();
      prog.name=$(this).parent('li').attr('data-prog-name');
      try {
        var data =  {'name': prog.name};
        $.ajax({url: '/program/load', data: data, type: "GET", success:function(data) {
	  Blockly.mainWorkspace.clear();
          var xml = Blockly.Xml.textToDom(data);
          Blockly.Xml.domToWorkspace(Blockly.mainWorkspace, xml);
          $("#dialogLoadProg").popup("close");
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

    function deleteProg() {
      var name=$(this).parent('li').attr('data-prog-name');
      if(confirm("Delete program " + name + "?")) {
        var data =  {'name': name};
        $.ajax({url: '/program/delete', data: data, type: "POST", success:function() {
          $(this).parent('li').remove();
          $('#i_prog_list').listview('refresh');
	  }});
       }
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
        $("#dialogRunning").popup("open", {transition: "pop"});
        setTimeout(statusProg, 1000);
      } catch (e) {
        alert(e);
      }
    }

    function endProg() {
      $.ajax({url: '/program/end', type: "POST"});
      $("#dialogRunning").popup("close");
    }

    function statusProg() {
      $.ajax({url: '/program/status', dataType: "json", type: "GET", success:function(data) {
        console.log(data.running);
        if(!data.running) {
          $('#b_end_prog_d').text('Close');
          $('#i_dialog_running_title').text('CoderBot stopped');
        } else {
          setTimeout(statusProg, 1000);
        }  
      }});
    }

    function goControl() {
      $.mobile.changePage("/");
    }
