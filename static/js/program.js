var inject_once = true;
var editor = null;
if($('#page-program')) {
    $(document).on( "pageshow", '#page-program', function( event, ui ) {
        $('[href="#page-program"]').addClass( "ui-btn-active" );
        $('[href="#page-control"]').removeClass( "ui-btn-active" );
         if(inject_once) {
            inject_once=false;
            var editorDOMElement = document.getElementById("editorDiv");
            if(CODERBOT_PROG_LEVEL != "py") {
                editor = new ProgramEditorBlockly(editorDOMElement);
            } else {
                editor = new ProgramEditorPython(editorDOMElement);
            }
        $("#b_new_prog").on("click", function() {editor.newProgramDlg()});
        $("#b_load_prog").on("click", function() {editor.loadProgramDlg()});
        $("#b_save_prog").on("click", function() {editor.saveProgram()});
        $("#b_save_prog_as").on("click", function() {editor.saveProgramAsDlg()});
        $("#b_save_prog_as_post").on("click", function() {editor.saveProgramAs()});
        $("#b_show_prog").on("click", function() {editor.showProgramCode()});
        $("#b_run_prog").on("click", function() {editor.runProgram()});
        $("#b_end_prog").on("click", function() {editor.stopProgram()});
        $("#b_end_prog_d").on("click", function() {editor.stopProgram()});
        $("#b_new_prog_post").on("click", function() {editor.newProgram()});
        editor.loadProgramList();
        $('#popup-video').popup();
        $('video').on('loadeddata', function( event, ui ) {
            $( '#popup-video' ).popup( 'reposition', 'positionTo: window' );}
        );
        $("#b_show_last").on("click", function( event ) {
            var src = "/photos/" + "VID" + editor.program.name + ".mp4" + "?t=" + (new Date()).getTime();
            $('#popup-video').find('video').attr('src', src);
            $('#popup-video').popup("open");
        });
        }

  });

    $(document).on( "pagecreate", '#page-program', function( event ) {
   });
}

class ProgramEditor {
    constructor(editorDOMElement) {
        this.program = {}
        this.programList = {}
        this.program.name = "no_name";
    }

    loadProgramList() {
        try {
            $.ajax({url: '/program/list', dataType: "json", type: "GET", success:function(data) {
               editor.programList = data;
            }});
        } catch (e) {
            alert(e);
        }
    }

    newProgramDlg() {
        $("#dialogNewProg").popup("open", {transition: "pop"});
    }

    newProgram() {
        $("#dialogNewProg").popup("close");
        var program_name = $("#i_new_prog_name").val();
        if($.inArray(name, this.programList)>=0) {
            if(!confirm(BotMessages.ProgramExists)) {
                throw "ProgramAlreadyExixts";
            }
        }
        this.program.name = program_name;
        $('#id_prog_name').text("[ " + this.program.name + " ]");
    }

    loadProgramDlg() {
        $('#i_prog_list').empty();
        for(var i in this.programList) {
            var name = this.programList[i].name;
            $('#i_prog_list').append('<li data-prog-name="' + name +'"><a href="#" class="c_load_prog"><h2>'+name+'</h2></a><a href="#" class="c_delete_prog">Delete program</a></li>');
        }
        $('#i_prog_list').listview('refresh'); 
        $('.c_load_prog').on('click', function(){editor.loadProgram($(this).parent('li').attr('data-prog-name'))});
        $('.c_delete_prog').on('click', function(){editor.deleteProgram($(this).parent('li').attr('data-prog-name'))});
        $("#dialogLoadProg").popup("open", {transition: "pop"});
    }

    loadProgram(name) {
        $("#dialogLoadProg").popup("close");
        $.mobile.loading("show");
        this.program.name = name;
        try {
            var data =  {'name': this.program.name};
            $.ajax({url: '/program/load', data: data, type: "GET", dataType: "json", success:function(data){editor.loadProgramCallback(data)}});
        } catch (e) {
            alert(e);
        }
    }

    loadProgramCallback(data) {
        $.mobile.loading("hide");
        $('#id_prog_name').text("[ " + this.program.name + " ]");
    }

    getProgramData() {
        return {name: this.program.name, dom_code: null, code: null};
    }

    saveProgram() {
        var data = this.getProgramData(); 
        $.ajax({url: '/program/save', data: data, type: "POST", success:function() {editor.saveProgramCallback()}});
    }

    saveProgramCallback() {
        alert(BotMessages.ProgramSaved);
        this.loadProgramList();
    }

    saveProgramAsDlg() {
        $("#dialogSaveProgAs").popup("open", {transition: "pop"});
    }

    saveProgramAs() {
        $("#dialogSaveProgAs").popup("close");
        var name = $("#i_save_prog_as_name").val();
        if($.inArray(name, this.programList)>=0) {
            if(!confirm(BotMessages.ProgramExists)) {
                return;
            }
        }
        this.program.name = name;
        $('#id_prog_name').text("[ " + this.program.name + " ]");
        this.saveProgram();
    }

    deleteProgram() {
        var prog_element = $(this).parent('li'); 
        var name=prog_element.attr('data-prog-name');
        if(confirm("Delete program " + name + "?")) {
            var data =  {'name': name};
            $.ajax({url: '/program/delete', data: data, type: "POST", success:function() {
                prog_element.remove();
                $('#i_prog_list').listview('refresh');
                this.loadProgramList();
	    }});
        }
    }

    runProgram() {
        var program_data = this.getProgramData()

        if(CODERBOT_PROG_SAVEONRUN) {
            try {
                $.ajax({url: '/program/save', data: program_data, type: "POST", success:function(){
                    editor.loadProgramlist();
                }});
            } catch (e) {
                alert(e);
            }
        }
        try {
            $.ajax({url: '/program/exec', data: program_data, type: "POST"});
            $("#dialogRunning").popup("open", {transition: "pop"});
            setTimeout(function() {editor.statusProgram()}, 1000);
        } catch (e) {
            alert(e);
        }
    }

    stopProgram() {
        $.ajax({url: '/program/end', type: "POST"});
        $("#dialogRunning").popup("close");
    }

    statusProgram() {
        $.ajax({url: '/program/status', dataType: "json", type: "GET", success:function(data) {
            $('#t_logging').val(data.log);
            if(!data.running) {
                $('#b_end_prog_d').text(BotMessages.ProgramDialogClose);
                $('#i_dialog_running_title').text('CoderBot ' + BotMessages.ProgramStatusStop);
            } else {
                $('#b_end_prog_d').text(BotMessages.ProgramDialogStop);
                $('#i_dialog_running_title').text('CoderBot ' + BotMessages.ProgramStatusRunning);
                setTimeout(statusProgram, 1000);
            }  
        }});
    }
}

class ProgramEditorBlockly extends ProgramEditor {
    constructor(editorDOMElement) {
        super(editorDOMElement);
        this.workspace = Blockly.inject(editorDOMElement,
                {path: '../../', toolbox: document.getElementById('toolbox'),
                 scrollbars:CODERBOT_PROG_SCROLLBARS, maxBlocks:CODERBOT_PROG_MAXBLOCKS,
                 zoom:
                 {controls: true,
                  wheel: false,
                  startScale: 1.0, //you can change this accorting to your needs.
                  maxScale: 1.5,
                  minScale: 0.2
                }});
    }

    newProgram() {
        try {
            super.newProgram()
            Blockly.mainWorkspace.clear();
        } catch(e) {
            console.log(e);
        }
    }

    loadProgramCallback(data) {
        editor.workspace.clear();
        var xml = Blockly.Xml.textToDom(data.dom_code);
        Blockly.Xml.domToWorkspace(xml, editor.workspace);
        super.loadProgramCallback(data)
    }

    getProgramData() {
        var xml_code = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
        var dom_code = Blockly.Xml.domToText(xml_code);

        window.LoopTrap = 1000;
        Blockly.Python.INFINITE_LOOP_TRAP = '  get_prog_eng().check_end()\n';
        var code = Blockly.Python.workspaceToCode();
        Blockly.Python.INFINITE_LOOP_TRAP = null;

        return {name: this.program.name, dom_code: dom_code, code: code};
    }

    showProgramCode() {
        // Generate Python code and display it.
        Blockly.Python.INFINITE_LOOP_TRAP = null;
        var code = Blockly.Python.workspaceToCode();
        alert(code);
    }
}

class ProgramEditorPython extends ProgramEditor {
    constructor(editorDOMElement) {
        super(editorDOMElement);
        this.editor = CodeMirror(editorDOMElement, {
        	mode: {name: "python", 
                       version: 2, 
                       singleLineStringErrors: false},
            	foldGutter: true,
                theme: "default",
                lineNumbers: true,
                matchBrackets: true});
    }

    newProgram() {
        try {
            super.newProgram();
            this.editor.clear();
        } catch(e) {
            console.log(e);
        }
    }

    loadProgramCallback(data) {
        this.editor.setValue(data.code);
        super.loadProgramCallback(data)
    }

    getProgramData() {
        var dom_code = "";
        var code = this.editor.getValue();
        return {name: this.program.name, dom_code: dom_code, code: code};
    }
}
