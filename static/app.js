URL = window.URL || window.webkitURL; //Checks which URL object to use depending on browser
var soundStream; //Stream from getUserMedia() aka microPhone
var rec; //recorder.js library
var microPhone;
var synced_recording = false;

var AudioContext = window.AudioContext || window.webkitAudioContext; //I already hate JS
//The above code abstract the audiocontext from the browser
var audio_context;

var record_button = document.getElementById("recordButton");
var stop_button = document.getElementById("stopButton");
var pause_button = document.getElementById("pauseButton");
var synced_record_button = document.getElementById("syncedRecordButton");
var recordings_list = document.getElementById("recordingsList");
var sync_audio = document.getElementById("sync_audio")

record_button.addEventListener("click", startRecording);
sync_audio.addEventListener("canplaythrough", function() {
    synced_record_button.disabled = false;
});
synced_record_button.addEventListener("click", startSyncedRecording)
stop_button.addEventListener("click", stopRecording);
pause_button.addEventListener("click", pauseRecording);

function startRecording() {
    console.log("Trying to start recording");

    // Constraints for getUserMedia, see https://blog.addpipe.com/audio-constraints-getusermedia/
    // or https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
    var constraints = {
        audio: {
            latency: 0.02,
            echoCancellation: false,
            mozNoiseSuppression: false,
            mozAutoGainControl: false
          },
        video: false
    };

    record_button.disabled = true;
    stop_button.disabled = false;
    pause_button.disabled = false; //Pressing record activates pause & stop

    //.then is JS's weird version of a try/catch block
    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        //A wild function definition appears
        console.log("Microphone Access was allowed, going on...");
        soundStream = stream;
        audio_context = new AudioContext();
        microPhone = audio_context.createMediaStreamSource(stream);
        rec = new Recorder(microPhone, {
            numChannels: 1 //Sweet stereo
        })
        rec.record();
        console.log("Now recording");
    }).catch(function(err) {
        console.log("Failed to get microphone input, user may try again")
        record_button.disabled = false;
        stop_button.disabled = true;
        pause_button.disabled = true;
    });
}

function pauseRecording() {
    console.log("pauseButton clicked rec.recording=", rec.recording);
    if(rec.recording) {
        if(synced_recording) {
            sync_audio.pause();
        }
        rec.stop();
        pause_button.innerHTML = "Resume";
    } else {
        if(synced_recording) {
            sync_audio.play();
        }
        rec.record();
        pause_button.innerHTML = "Pause";
    }
}

function stopRecording() {
    if(synced_recording) {
        sync_audio.pause();
        sync_audio.currentTime = 0; //Zurückspulen
        synced_recording = false;
        synced_record_button.disabled = false;
    }
    console.log("stopButton clicked");
    //disable the stop button, enable the record too allow for new recordings
    stop_button.disabled = true;
    record_button.disabled = false;
    pause_button.disabled = true;
    //reset button just in case the recording is stopped while paused
    pause_button.innerHTML = "Pause";
    //tell the recorder to stop the recording
    rec.stop(); //stop microphone access
    soundStream.getAudioTracks()[0].stop(); //?
    //create the wav blob and pass it on to createDownloadLink
    rec.exportWAV(createDownloadLink);
}

function createDownloadLink(blob) {
    var url = URL.createObjectURL(blob); //Pretty nice API, creates a "URL" for any in-memory blob
    var audio_element = document.createElement('audio');
    var list_element = document.createElement('li');
    var link_element = document.createElement('a');
    audio_element.controls = true; //See https://www.w3schools.com/tags/tag_audio.asp
    audio_element.src = url;
    link_element.href = url;
    link_element.download = new Date().toISOString() + '.wav'; //Suggested filename for downloading
    link_element.innerHTML = "Download Recording: " + link_element.download;
    list_element.appendChild(audio_element)
    list_element.appendChild(link_element)
    recordings_list.appendChild(list_element)
}

function startSyncedRecording() {
    console.log("Trying to start synced recording");
    synced_recording = true;
    // Constraints for getUserMedia, see https://blog.addpipe.com/audio-constraints-getusermedia/
    // or https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
    var constraints = {
         audio: {
            latency: 0.01,
            echoCancellation: false,
            mozNoiseSuppression: false,
            mozAutoGainControl: false
          },
        video: false
    }

    synced_record_button.disabled = true;
    record_button.disabled = true;
    stop_button.disabled = false;
    pause_button.disabled = false; //Pressing record activates pause & stop

    //.then is JS's weird version of a try/catch block
    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        //A wild function definition appears
        console.log("Microphone Access was allowed, going on...");
        soundStream = stream;
        audio_context = new AudioContext();
        microPhone = audio_context.createMediaStreamSource(stream);
        rec = new Recorder(microPhone, {
            numChannels: 2 //Sweet stereo
        })
        rec.record();
        sync_audio.play();
        console.log("Now recording");
    }).catch(function(err) {
        console.log("Failed to get microphone input, user may try again")
        record_button.disabled = false;
        stop_button.disabled = true;
        pause_button.disabled = true;
    });
}


