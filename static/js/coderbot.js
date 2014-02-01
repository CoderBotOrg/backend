function CoderBot() {
	this.url = "/bot";
}

CoderBot.prototype.command = function(cmd, param) {
	data =  {'cmd': cmd,
			 'param': param};
	$.ajax({url: this.url, data: data, type: "GET"});
}

CoderBot.prototype.forward = function(t) {
	this.command('forward', t);
}

CoderBot.prototype.left = function(t) {
	this.command('left', t);
}

CoderBot.prototype.right = function(t) {
	this.command('right', t);
}

CoderBot.prototype.backward = function(t) {
	this.command('backward', t);
}

var bot = new CoderBot();

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
