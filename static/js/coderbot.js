function CoderBot() {
/*
  this.ws = new WebSocket("ws://" + document.domain + ":" + location.port + "/bot_ws");     
  this.ws.onopen=function(e) {console.log('open')};
  this.ws.onclose=function(e) {console.log('closed')};
  this.ws.onerror=function(e) {console.log(e.data)}
*/
};

CoderBot.prototype.command = function(cmd, param) {
/*
  if(!param) {
    this.ws.send(cmd);    
  } else { 
*/
	this.url = "/bot";
	var data =  {'cmd': cmd,
                     'param': param};
	$.ajax({url: this.url, data: data, async: false, type: "GET"});
  //}
}

CoderBot.prototype.forward = function(t) {
	this.command('forward', typeof t !== 'undefined' ? t : -1 );
}

CoderBot.prototype.left = function(t) {
	this.command('left', typeof t !== 'undefined' ? t : -1 );
}

CoderBot.prototype.right = function(t) {
	this.command('right', typeof t !== 'undefined' ? t : -1 );
}

CoderBot.prototype.backward = function(t) {
	this.command('backward', typeof t !== 'undefined' ? t : -1 );
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
