Recorder.initialize({
	swfSrc: "ao/swf/recorder.swf"
});

var isRecord = false;

function timecode(ms) {
	var hms = {
			h: Math.floor(ms/(60*60*1000)),
			m: Math.floor((ms/60000) % 60),
			s: Math.floor((ms/1000) % 60)
	};
	var tc = []; // Timecode array to be joined with '.'

	if (hms.h > 0) {
		tc.push(hms.h);
	}

	tc.push((hms.m < 10 && hms.h > 0 ? "0" + hms.m : hms.m));
	tc.push((hms.s < 10  ? "0" + hms.s : hms.s));

	return tc.join(':');
}

function record(){
	isRecord = true;
	Recorder.record({
		start: function(){
			document.getElementById("status-lbl").innerHTML = "Started Recording Message..";
		},
		progress: function(milliseconds){
			document.getElementById("status-lbl").innerHTML = "Recording Message : " +  timecode(milliseconds);
		}
	});
}

function play(){
	isRecord = false;
	Recorder.stop();
	Recorder.play({
		progress: function(milliseconds){
			document.getElementById("status-lbl").innerHTML = "Playing Message : " + timecode(milliseconds);
		}
	});
}

function stop(){
	Recorder.stop();
	if(isRecord)
		document.getElementById("status-lbl").innerHTML = "Recording of message stopped..";
	else
		document.getElementById("status-lbl").innerHTML = "Playing of message stopped..";
}


function upload(uploadUrl, params){
	var dataParams =  {};
	for (var i = 0; i < params.length; i++) {
	    var entry = params[i];
	    dataParams[entry.name] = entry.value;
	}
	
	Recorder.upload({
		url:        uploadUrl,
		audioParam: "main", 
		params: dataParams,
		success: function(responseText){           
			window.onAudioSucessCallBack(responseText);
		},
		error: function(errorText){
			window.onAudioErrorCallBack(errorText);
		}
	});
}