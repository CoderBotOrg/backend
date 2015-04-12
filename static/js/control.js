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
	$( ".photopopup" ).on({
        	popupbeforeposition: function() {
            	var maxHeight = $( window ).height() - 60 + "px";
            	$( ".photopopup img" ).css( "max-height", maxHeight );
        	}
    	});
});
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
});

$(document).on( "pageshow", '#page-photos', function( event ) {
	var media_list = $('#media').empty();
	$.get(url='/photos', success=function(data){
                for( p in data) {
			var media = data[p];
			var media_name = media.substring(0, media.indexOf('.'));
			var media_thumb = media_name + '_thumb.jpg';
			var media_type = media.indexOf('jpg') > 0 ? 'photo' : 'video';
			media_list.append('<li class="ui-li-has-thumb"><a href="#popup-' + media_type + '" data-rel="popup" data-position-to="window" class="ui-btn ui-corner-all ui-shadow ui-btn-inline"><img class="ui-li-thumb" data-src="' + media + '" src="/photos/' + media_thumb + '"><div class="ui-content-hud" style="position:absolute;"></div><p class="p_photo_cmd" style="display:none;"><span>' + media_name + '</span><br/><button class="ui-btn ui-btn-inline ui-mini ui-icon-delete ui-btn-icon-left b_photo_delete">' + BotMessages.DeletePhoto + '</button></p></a></li>');
		}
$('li.ui-li-has-thumb').hover( function( event ) {
	$(this).find('.p_photo_cmd').show();
}, function( event ) {
        $(this).find('.p_photo_cmd').hide();
});
$('video').on('loadeddata', function( event, ui ) {
        $( '#popup-video' ).popup( 'reposition', 'positionTo: window' );
});
        }, dataType="json");       
});

$(document).on( "click", 'a[data-rel="popup"]', function( event ) {
	var src = "/photos/" + $(this).find('img').attr('data-src');
        $('#popup-photo').find('img').attr('src', src);
        $('#popup-video').find('video').attr('src', src);
});

$(document).on( "click", '.b_photo_delete', function( event ) {
        var ul = $(this).parents('ul');
        var li = $(this).parents('li');
	var src = "/photos/" + li.find('img').attr('data-src');
	if(confirm(BotMessages.DeletePhotoConfirm + src + " ?")) {
        	$.post(url=src, data={'cmd':'delete'}, success=function(data){
			li.remove();
                        ul.listview('refresh');
        	});
	}
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

function botStatus() {
  $.ajax({url:'/bot/status',dataType:'json'})
  .done(function (data) {
    if(data.status == 'ok') {
      $('.s_bot_status').text('Online').removeClass('ui-icon-alert ui-btn-b').addClass('ui-icon-check ui-btn-a');
    } else {
      $('.s_bot_status').text('Offline').removeClass('ui-icon-check ui-btn-a').addClass('ui-icon-alert ui-btn-b');
    }})
  .error(function() {
    $('.s_bot_status').text('Offline').removeClass('ui-icon-check ui-btn-a').addClass('ui-icon-alert ui-btn-b');
  });
  setTimeout(botStatus, 1000);
}
