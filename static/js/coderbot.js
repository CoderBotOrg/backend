function CoderBot() {};

CoderBot.prototype.command = function(cmd, param) {
	this.url = "/bot";
	var data =  {'cmd': cmd,
                     'param': param};
	$.ajax({url: this.url, data: data, async: false, type: "GET"});
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

CoderBot.prototype.set_handler = function(h) {
	this.command('set_handler', h);
}

CoderBot.prototype.say = function(h) {
	this.command('say', h);
}
