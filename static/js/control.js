var bot = new CoderBot()

$(document).ready(function() {	
	$('#b_forward')
          .on("mousedown", function (){bot.forward();})
	  //.on("touchstart", function (){bot.forward();})
	  .on("mouseup", function (){bot.stop();})
	  //.on("touchend", function (){bot.stop();});
	$('#b_backward')
          .on("mousedown", function (){bot.backward();})
	  //.on("touchstart", function (){bot.backward();})
	  .on("mouseup", function (){bot.stop();})
	  //.on("touchend", function (){bot.stop();});
	$('#b_left')
	  .on("mousedown", function (){bot.left();})
	  //.on("touchstart", function (){bot.left();})
	  .on("mouseup", function (){bot.stop();})
	  //.on("touchend", function (){bot.stop();});
	$('#b_right')
          .on("mousedown", function (){bot.right();})
	  //.on("touchstart", function (){bot.right();})
	  .on("mouseup", function (){bot.stop();})
	  //.on("touchend", function (){bot.stop();});

	$('#b_say').on("click", function (){
		var text = $('#i_say').val();
                bot.say(text);
	});
	$('.b_camera').on("click", function (){
		var param = $(this).attr('data-param');
		bot.set_handler(param);
                $('#f_stream').attr('src', $('#f_stream').attr('src'));
	});
});
