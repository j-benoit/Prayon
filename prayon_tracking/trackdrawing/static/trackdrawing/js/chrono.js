var startTime = 0
var start = 0
var end = 0
var diff = 0
var timerID = 0
var startOff = 0
//window.onload = chronoStart;
function chrono(){
	end = new Date()
	diff = end - start
	diff = diff + startOff
	diff = new Date(diff)
	var msec = diff.getMilliseconds()
	var sec = diff.getSeconds()
	var min = diff.getMinutes()
	var hr = diff.getHours()-1
	if (min < 10){
		min = "0" + min
	}
	if (sec < 10){
		sec = "0" + sec
	}
	if(msec < 10){
		msec = "00" +msec
	}
	else if(msec < 100){
		msec = "0" +msec
	}
	document.getElementById("id_chronotime").value = hr + ":" + min + ":" + sec + "." + msec
	timerID = setTimeout("chrono()", 10)
}
function chronoStart(){
	//document.chronoForm.startstop.value = "stop!"
	$('#id_view').attr("onclick","");
	document.chronoForm.startstop.onclick = chronoStop
	//document.chronoForm.reset.onclick = chronoReset
	var startvalue = document.getElementById("id_chronotime").value
	start = new Date()
	var startvaluesplit = startvalue.split(":")
	var startsec = Number(startvaluesplit[2])
	var startmin = Number(startvaluesplit[1])
	var starthr = Number(startvaluesplit[0])
	startOff = startsec * 1000 + startmin * 60000 + starthr * 3600000
	chrono()
}
function chronoContinue(){
	//document.chronoForm.startstop.value = "stop!"
	document.chronoForm.startstop.onclick = chronoStop
	//document.chronoForm.reset.onclick = chronoReset
	startOff = 0
	start = new Date()-diff
	start = new Date(start)
	chrono()
}
function chronoReset(){
	document.getElementById("id_chronotime").value = "00:00:000"
	startOff = 0
	start = new Date()
}
function chronoStopReset(){
	document.getElementById("id_chronotime").value = "00:00:000"
	document.chronoForm.startstop.onclick = chronoStart
}
function chronoStop(){
	//document.chronoForm.startstop.value = "start!"
	document.chronoForm.startstop.onclick = chronoContinue
	//document.chronoForm.reset.onclick = chronoStopReset
	clearTimeout(timerID)
}