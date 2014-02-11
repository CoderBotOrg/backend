$(document).ready(function() {
	
	$('#b_forward').on("click", function (){
		CoderBot.forward(1);
	});
	$('#b_left').on("click", function (){
		CoderBot.left(1);
	});
	$('#b_right').on("click", function (){
		CoderBot.right(1);
	});
	$('#b_backward').on("click", function (){
		CoderBot.backward(1);
	});
});
