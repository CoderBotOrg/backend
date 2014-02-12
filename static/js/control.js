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
});
