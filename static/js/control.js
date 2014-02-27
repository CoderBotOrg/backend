var bot = new CoderBot()

$(document).ready(function() {
	
	$('#b_forward').on("click", function (){
		bot.forward(1);
	});
	$('#b_left').on("click", function (){
		bot.left(1);
	});
	$('#b_right').on("click", function (){
		bot.right(1);
	});
	$('#b_backward').on("click", function (){
		bot.backward(1);
	});
	$('.b_camera').on("click", function (){
		var param = $(this).attr('data-param');
		bot.set_handler(param);
                $('#f_stream').attr('src', $('#f_stream').attr('src'));
	});
});
