function CoderBot() {
};

CoderBot.prototype.command = function(cmd, param1, param2) {
	this.url = "/bot";
	var data =  {'cmd': cmd,
                     'param1': param1,
                     'param2': param2};
	$.ajax({url: this.url, data: data, async: true, type: "GET"});
}

CoderBot.prototype.forward = function(speed, elapse) {
	this.command('forward', speed, elapse );
}

CoderBot.prototype.left = function(speed, elapse) {
	this.command('left', speed, elapse );
}

CoderBot.prototype.right = function(speed, elapse) {
	this.command('right', speed, elapse );
}

CoderBot.prototype.backward = function(speed, elapse) {
	this.command('backward', speed, elapse );
}

CoderBot.prototype.stop = function() {
	this.command('stop', 0);
}

CoderBot.prototype.set_handler = function(h) {
	this.command('set_handler', h);
}

CoderBot.prototype.say = function(h) {
	this.command('say', h);
}

CoderBot.prototype.halt = function(h) {
	this.command('halt', h);
}
