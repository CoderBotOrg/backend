var bot = new CoderBot()

$(document).on( "pagecreate", function( event ) {
	if(('ontouchstart' in window) ||
     	   (navigator.maxTouchPoints > 0) ||
     	   (navigator.msMaxTouchPoints > 0)) {
       	        /* browser with either Touch Events of Pointer Events running on touch-capable device */	
		$('#b_forward')
	  	.on("touchstart", function (){console.log("start"); bot.forward(100,-1);})
	  	.on("touchend", function (){console.log("end"); bot.stop();});
		$('#b_backward')
	  	.on("touchstart", function (){bot.backward(100,-1);})
	  	.on("touchend", function (){bot.stop();});
		$('#b_left')
	  	.on("touchstart", function (){bot.left(40,-1);})
	  	.on("touchend", function (){bot.stop();});
		$('#b_right')
	  	.on("touchstart", function (){bot.right(40,-1);})
	  	.on("touchend", function (){bot.stop();});
	} else {
		$('#b_forward')
          	.on("mousedown", function (){bot.forward(100, -1);})
	  	.on("mouseup", function (){bot.stop();})
		$('#b_backward')
          	.on("mousedown", function (){bot.backward(100, -1);})
	  	.on("mouseup", function (){bot.stop();})
		$('#b_left')
	  	.on("mousedown", function (){bot.left(40,-1);})
	  	.on("mouseup", function (){bot.stop();})
		$('#b_right')
          	.on("mousedown", function (){bot.right(40, -1);})
	  	.on("mouseup", function (){bot.stop();})
	}
	$('#b_say').on("click", function (){
		var text = $('#i_say').val();
                bot.say(text);
	});
	$('.b_camera').on("click", function (){
		var param = $(this).attr('data-param');
		bot.set_handler(param);
                $('#f_stream').attr('src', $('#f_stream').attr('src'));
	});
	$('#b_halt').on("click", function (){
		if(confirm("Shutdown CoderBot?")){
			bot.halt();
		}
	});
});
