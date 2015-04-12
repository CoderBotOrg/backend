function CoderBot(elemCounterId) {
    this.element = elemCounterId
    this.counter = 0;
};

CoderBot.prototype.command = function(cmd, param1, param2) {
	this.url = "/bot";
	var data =  {'cmd': cmd,
                     'param1': param1,
                     'param2': param2};
	$.ajax({url: this.url, data: data, async: true, type: "GET"});
}

CoderBot.prototype.counterInc = function() {
    this.counter++;
    $(this.element).html(this.counter);
}

CoderBot.prototype.counterDec = function() {
    this.counter--;
    $(this.element).html(this.counter);
}

CoderBot.prototype.counterReset = function() {
    this.counter = 0;
    $(this.element).html(this.counter);
}

CoderBot.prototype.move = function(speed, amount) {
    if(CODERBOT_CTRL_MOVE_MOTION) {
        this.command('move_motion', Math.abs(speed), Math.sign(speed) * amount );
    } else {
        this.command('move', speed, amount );
    }
    this.counterInc();
}

CoderBot.prototype.turn = function(speed, amount) {
    if(CODERBOT_CTRL_MOVE_MOTION) {
        this.command('turn_motion', Math.abs(speed), Math.sign(speed) * amount );
    } else {
        this.command('turn', speed, amount );
    }
    this.counterInc();
}


CoderBot.prototype.stop = function() {
	if(CODERBOT_CTRL_FW_ELAPSE < 0) {
		this.command('stop', 0);
        }
}

CoderBot.prototype.takePhoto = function() {
	this.command('take_photo', 0);
}

CoderBot.prototype.videoRec = function() {
	this.command('video_rec', 0);
}

CoderBot.prototype.videoStop = function() {
	this.command('video_stop', 0);
}

CoderBot.prototype.say = function(h) {
	this.command('say', h);
}

CoderBot.prototype.halt = function(h) {
	this.command('halt', h);
}

CoderBot.prototype.restart = function(h) {
        this.command('restart', h);
}

CoderBot.prototype.reboot = function(h) {
        this.command('reboot', h);
}
