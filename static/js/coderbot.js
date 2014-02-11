var CoderBot {}

CoderBot.prototype.command = function(cmd, param) {
	var url = "/bot";
	var data =  {'cmd': cmd,
			 'param': param};
	$.ajax({url: this.url, data: data, type: "GET"});
}

CoderBot.prototype.forward = function(t) {
	CoderBot.command('forward', t);
}

CoderBot.prototype.left = function(t) {
	CoderBot.command('left', t);
}

CoderBot.prototype.right = function(t) {
	CoderBot.command('right', t);
}

CoderBot.prototype.backward = function(t) {
	CoderBot.command('backward', t);
}
