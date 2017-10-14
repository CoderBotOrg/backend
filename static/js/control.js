var bot = new CoderBot('#b_counter');

$(document).on( "pagecontainershow", function(){
    ScaleContentToDevice();
    
    $(window).on("resize orientationchange", function(){
        ScaleContentToDevice();
    })
});

function ScaleContentToDevice(){
    scroll(0, 0);
    var w = $( window ).width();
    var h = $( window ).height();
  
    var width =  w;
    var height = h - $(".ui-header").outerHeight() - $(".ui-footer").outerHeight();
    var contentHeight = height - $(".ui-content").outerHeight() + $(".ui-content").height();
    var contentWidth = (contentHeight * 4) / 3;

    if (width - contentWidth > 384) {
      $("#ui_control_left").width((width - contentWidth)/2);
      $("#ui_control_center").width(contentWidth);
      $("#ui_control_right").width((width - contentWidth)/2);      
    } else {
      $("#ui_control_left").width((width)/2);
      $("#ui_control_center").width(0);
      $("#ui_control_right").width((width)/2);      
    }

    $(".ui-content-stream").height(contentHeight);
}


if($("#page-control")) {
$(document).on( "pageshow", '#page-control', function( event, ui ) {
      $('[href="#page-control"]').addClass( "ui-btn-active" );
      $('[href="#page-program"]').removeClass( "ui-btn-active" );
});

$(document).on( "pagecreate", '#page-control', function( event ) {
	if(Modernizr.touch){
       	        /* browser with either Touch Events of Pointer Events running on touch-capable device */	
		$('#b_forward')
	  	.on("touchstart", function (){bot.move(CODERBOT_CTRL_FW_SPEED,CODERBOT_CTRL_FW_ELAPSE);})
	  	.on("touchend", function (){bot.stop();});
		$('#b_backward')
	  	.on("touchstart", function (){bot.move(0-CODERBOT_CTRL_FW_SPEED,CODERBOT_CTRL_FW_ELAPSE);})
	  	.on("touchend", function (){bot.stop();});
		$('#b_left')
	  	.on("touchstart", function (){bot.turn(0-CODERBOT_CTRL_TR_SPEED,CODERBOT_CTRL_TR_ELAPSE);})
	  	.on("touchend", function (){bot.stop();});
		$('#b_right')
	  	.on("touchstart", function (){bot.turn(CODERBOT_CTRL_TR_SPEED,CODERBOT_CTRL_TR_ELAPSE);})
	  	.on("touchend", function (){ bot.stop();});
                $('body').on("touchend", function (){bot.stop();});
                $('#b_counter').on("touchend", function (){if(confirm(BotMessages.CounterReset)) bot.counterReset();});
           } else {
		$('#b_forward')
          	.on("mousedown", function (){bot.move(CODERBOT_CTRL_FW_SPEED, CODERBOT_CTRL_FW_ELAPSE);})
	  	.on("mouseup", function (){bot.stop();});
		$('#b_backward')
          	.on("mousedown", function (){bot.move(0-CODERBOT_CTRL_FW_SPEED, CODERBOT_CTRL_FW_ELAPSE);})
	  	.on("mouseup", function (){bot.stop();});
		$('#b_left')
	  	.on("mousedown", function (){bot.turn(0-CODERBOT_CTRL_TR_SPEED,CODERBOT_CTRL_TR_ELAPSE);})
	  	.on("mouseup", function (){bot.stop();});
		$('#b_right')
          	.on("mousedown", function (){bot.turn(CODERBOT_CTRL_TR_SPEED, CODERBOT_CTRL_TR_ELAPSE);})
	  	.on("mouseup", function (){bot.stop();});
                $('body').on("mouseup", function (){bot.stop();});
                $('#b_counter').on("click", function (){if(confirm(BotMessages.CounterReset)) bot.counterReset();});
	}
	$('#b_say').on("click", function (){
		var text = window.prompt(BotMessages.Input);
                bot.say(text);
	});
	$('#b_camera').on("click", function (){
                bot.takePhoto();
	});
	$('#b_video_rec').on("click", function (){
                bot.videoRec();
	});
	$('#b_video_stop').on("click", function (){
                bot.videoStop();
	});
	$('#b_photos').on("click", function (){
        	$.mobile.pageContainer.pagecontainer('change', '#page-photos');
	});
	$('#photo_detail').on("click", function (e) {
                var pos = findPos(e.target);
                var x = e.pageX - pos.x;
                var y = e.pageY - pos.y;
                var img = $("#photo_detail_img");
                canvas = document.createElement("canvas");
                canvas.width = img.width();
                canvas.height = img.height();
                canvas.getContext('2d').drawImage(img.get(0), 0, 0, img.width(), img.height());
                var pixelData = canvas.getContext('2d').getImageData(x, y, 1, 1).data;
                var colorHex = "#" + paddedHexString(pixelData[0]) + paddedHexString(pixelData[1]) + paddedHexString(pixelData[2]);
		alert(BotMessages.ColorAtPoint + colorHex); 
        });
	$( ".photopopup" ).on({
        	popupbeforeposition: function() {
            	var maxHeight = $( window ).height() - 60 + "px";
            	$( ".photopopup img" ).css( "max-height", maxHeight );
        	}
    	});
});
}

function paddedHexString(n) {
        var ns = n.toString(16);
	return ("00" + ns).substring(ns.length); 
}


function findPos(obj) {
    var curleft = 0, curtop = 0;
    if (obj.offsetParent) {
        do {
            curleft += obj.offsetLeft;
            curtop += obj.offsetTop;
        } while (obj = obj.offsetParent);
        return { x: curleft, y: curtop };
    }
    return undefined;
}

$(document).on( "pagecreate", '#page-preferences', function( event ) {
	$('#f_config').on("submit", function (){	
		var form_data = $(this).serialize();
                $.post(url='/config', form_data, success=function(){
                  alert(BotMessages.Saved);
                  location.href="/";
                });
                return false;
	});
        $.get(url='/cnnmodels', success= function(data) {
        	$('#i_cnn_default_model').empty();
		$('#i_cnn_default_model').append('<option></option>');
		var def_model = $('#i_cnn_default_model').attr("value");
		for(m in data) {
			if(Math.trunc(parseInt(data[m].status))==1){
				$('#i_cnn_default_model').append('<option value="'+m+'">'+m+'</option>');
			}
		}
		$('#i_cnn_default_model').val(def_model).selectmenu("refresh");

	}, dataType="json");
	$( "#popup-cnn-models" ).bind({
   		popupbeforeposition: function(event, ui) {
			$.get(url='/cnnmodels', success= function(data) {
				$('#cnn-model-list').empty();
				for(m in data) {
					$('#cnn-model-list').append('<li data-icon="delete"><a href="#" data-name="'+m+'" class="b_cnn_model_delete">'+m+' [' + Math.trunc(parseFloat(data[m].status) * 100) +'%]</a></li>');
				}
				$('#cnn-model-list').listview('refresh');
                                $('.b_cnn_model_delete').on('click', function(event, ui) {
					var model_name = $(event.target).attr("data-name");
					if(confirm("Delete model " + model_name + "?")) {
						$.ajax({url:'/cnnmodels/'+model_name, method: "DELETE", success: function(data) {
							console.log("model_name: " + model_name);
							$('#cnn-model-list a[data-name="' + model_name + '"]').parent().remove();
 							$('#cnn-model-list').listview('refresh');
							}
						});
					}
				});
			}, dataType='json')
		}
	});
        $( "#f_cnn_train" ).submit(function (){
			var form = $(event.target);
                        var data = {architecture: form.find("#i_cnn_model_arch").val(),
				model_name: form.find("#i_cnn_model_name").val(),
				training_steps: parseInt(form.find("#i_cnn_train_steps").val()),
				learning_rate: parseFloat(form.find("#i_cnn_learn_rate").val()),
				image_tags: form.find("#i_cnn_image_tags").val().split(",")};
			console.log(data);
                        $.post(url='/cnnmodels', data=JSON.stringify(data), success=function(data) {
					alert(BotMessages.ModelTraining);
                                }, dataType='json');
			return false;
        });
        $('#b_wifi_apply').on("click", function (){
                var form_data = $(this).parents("form").serialize();
                $.post(url='/wifi', form_data);
                $('#popup-wifi').popup('close');
                if($("[name='wifi_mode']:checked").val()=="ap"){
			$('#popup-wifi-ap').popup('open');
                } else {
                        $('#popup-wifi-client').popup('open');
		}
                return false;
        });
        $('#b_halt').on("click", function (){
                if(confirm("Shutdown CoderBot?")){
                        bot.halt();
                }
        });
        $('#b_restart').on("click", function (){
                if(confirm("Restart CoderBot?")){
                        bot.restart();
                }
        });
        $('#b_reboot').on("click", function (){
                if(confirm("Reboot CoderBot?")){
                        bot.reboot();
                }
        });
        $('#b_update').on("click", function (){
                if(confirm(BotMessages.UpdateSystem)){
		        $('#popup-update-system').popup('open');	
                        $.get(url='/update', success=function (data) {
                                $('#i_update_system_log').text(data);
                                $('#b_update_system_close').removeClass('ui-disabled');
                        });
		}
        });
});
var tags = [];

$(document).on( "pageshow", '#page-photos', function( event ) {
	var media_list = $('#media').empty();
	$.get(url='/photos', success=function(data){
		tags = [];
		for(p in data) {
			var media = data[p];
			if(media.tag && tags.indexOf(media.tag)<0) {
				tags.push(media.tag);
			}
		}
                for(p in data) {
			var media = data[p];
			media.type = media.name.indexOf('jpg') > 0 ? 'photo' : 'video';
			media.thumb = media.name.replace(media.name.substring(media.name.length-4), '_thumb.jpg');
                        var tags_select = '<select class="s_media_tag" data-mini="true">';
			tags_select += '<option value=""' + (media.tag ? '' : ' selected') + '></option>';
                        for(t in tags) {
                          tags_select += ('<option value="' + tags[t] + '"'  + (media.tag == tags[t] ? " selected" : "") + '>'+tags[t]+'</option>');
			}
			tags_select += '<option value="new" class="o_new">new...</option></select>';
			media_list.append('<li class="ui-li-has-thumb"><a href="#popup-' + media.type + '" data-rel="popup" data-position-to="window" class="ui-btn ui-corner-all ui-shadow ui-btn-inline a_media_thumb"><img class="ui-li-thumb" data-src="' + media.name + '" src="/photos/' + media.thumb + '"></a><div class="ui-content-hud" style=""><p class="p_photo_cmd" style="display:none;"><span>' + media.name + '</span><br/><button class="ui-btn ui-btn-inline ui-mini ui-icon-delete ui-btn-icon-left ui-corner-all b_photo_delete">' + BotMessages.DeletePhoto + '</button>' + tags_select + '</p></div></li>');
		}

$('li.ui-li-has-thumb').hover( function( event ) {
	$(this).find('.p_photo_cmd').show();
}, function( event ) {
        $(this).find('.p_photo_cmd').hide();
});
$('video').on('loadeddata', function( event, ui ) {
        $( '#popup-video' ).popup( 'reposition', 'positionTo: window' );
});
$('select.s_media_tag').change(function (e) {
	var select = $(e.target);
	var image = select.parents('li').find('img').attr('data-src');
	var tag_name = select.find('option:selected').text();
        if(tag_name == "new...") {
		while(true) {
			tag_name = prompt("Enter a new tag:", "");
			if(tags.indexOf(tag_name)>=0) {
				alert(BotMessages.TagAlreadyExists);
			} else {
				$('<option value="' + tag_name + '">' + tag_name +'</option>').insertBefore('option.o_new');
				select.find('option').removeAttr('selected');
				select.find('option[value="'+tag_name+'"]').attr('selected', true);
				break;
			}
		}
	}
	var data = {tag: tag_name};
	$.ajax(url="/photos/"+image, {method:"PUT", data:JSON.stringify(data), dataType:'json'});
});
        }, dataType="json");       
});

$(document).on( "click", 'a.a_media_thumb[data-rel="popup"]', function( event ) {
	var src = "/photos/" + $(this).find('img').attr('data-src');
        $('#popup-photo').find('img').attr('src', src);
        $('#popup-video').find('video').attr('src', src);
});

$(document).on( "click", '.b_photo_delete', function( event ) {
        var ul = $(this).parents('ul');
        var li = $(this).parents('li');
	var src = "/photos/" + li.find('img').attr('data-src');
	if(confirm(BotMessages.DeletePhotoConfirm + src + " ?")) {
        	$.ajax({url:src, method:"DELETE", success:function(data){
			li.remove();
                        ul.listview('refresh');
        	}});
	}
        event.preventDefault();
});

$(document).on( "click", '.b_photo_prop', function( event ) {
        var li = $(this).parents('li');
        $('popup-picprop').popup("open");
        event.preventDefault();
});


Mousetrap.bind(['command+alt+s', 'ctrl+alt+k'], function(e) {
	$.mobile.pageContainer.pagecontainer('change', '#page-preferences');
        return false;
});

Mousetrap.bind(['command+alt+h', 'ctrl+alt+h'], function(e) {
        if(confirm("Shutdown CoderBot?")){
        	bot.halt();
	}
});
 
botStatus();
var bot_status = true;
function botStatus() {
  $.ajax({url:'/bot/status',dataType:'json'})
  .done(function (data) {
    if(data.status == 'ok') {
      $('.s_bot_status').text('Online').removeClass('ui-icon-alert ui-btn-b').addClass('ui-icon-check ui-btn-a');
      if( bot_status == false ) {
        window.location.reload(false);
      }
    } else {
      $('.s_bot_status').text('Offline').removeClass('ui-icon-check ui-btn-a').addClass('ui-icon-alert ui-btn-b');
      bot_status = false;
    }})
  .error(function() {
    $('.s_bot_status').text('Offline').removeClass('ui-icon-check ui-btn-a').addClass('ui-icon-alert ui-btn-b');
    bot_status = false;
  });
  setTimeout(botStatus, 1000);
}
