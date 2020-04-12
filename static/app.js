URL = window.URL || window.webkitURL; //Checks which URL object to use depending on browser
var soundStream; //Stream from getUserMedia() aka microPhone
var encoder = new OggVorbisEncoder(44100, 2, 0.45);
var rec; //recorder.js library
var microPhone;
var synced_recording = false;

var AudioContext = window.AudioContext || window.webkitAudioContext; //I already hate JS
//The above code abstract the audiocontext from the browser
var audio_context;

var record_button;
var stop_button;
var pause_button;
var synced_record_button;
var recordings_list;
var sync_audio;
var play_playback_button;
var clicked_item;



$('.record-controls').click(function(event){
    event.stopPropagation();
});

$(".entry-container").click(function() {
    clicked_item = this;
    var req = new XMLHttpRequest();
    let id = $(this).data("id");
    let arrow = $(".show-song-arrow[data-id='"+ id + "']");
    record_button = $(".recordButton[data-id='"+ id +"']");
    synced_record_button = $(".syncedRecordButton[data-id='"+ id +"']");
    stop_button = $(".stopButton[data-id='" + id + "']");
    pause_button = $(".pauseButton[data-id='" + id + "']");
    play_playback_button = $(".playbackPlayButton[data-id='"+ id+"']");
    sync_audio = $(".sync_audio[data-id='"+id +"']");
    recordings_list = $(".record-list[data-id='"+ id +"']");

    record_button.click(startRecording);
    synced_record_button.click(startSyncedRecording);
    stop_button.click(stop);
    play_playback_button.click(playSyncFile);
    req.open("GET", "/static/sample_sync_21guns.ogg", true);
    req.addEventListener("progress", function (e) {
        var complete = (e.loaded / e.total) * 100;
        document.querySelector('.sync_progress').MaterialProgress.setProgress(complete);
    }, false);
    req.responseType = "blob";
    req.onreadystatechange = function () {
    if (req.readyState === 4 && req.status === 200) {
        $('.sync_progress').hide();
        synced_record_button.attr('disabled', false);
        synced_record_button.html("Aufnahme mit Playback");
        play_playback_button.attr('disabled', false);
        play_playback_button.html('Playback wiedergeben');
        var blob_URL =  URL.createObjectURL(req.response);
        sync_audio.attr("src", blob_URL);
    }
    };
    req.send();

    var $self = $(this).find(".record-controls");
    $self.toggle();
    if ($self.is(":visible")) {
        $(this).height(200);
        arrow.html("arrow_drop_down");
    } else {
        arrow.html("arrow_right");
        $(this).height(70);
    }
    $(".record-controls").not($self).hide();
    $(".entry-container").not(this).height(70);
});

function progress({loaded, total}) {
    console.log("loaded: " + loaded + "total: " + total);
}

function playSyncFile() {
    if(sync_audio[0].paused) {
        sync_audio[0].play();
        synced_record_button.attr("disabled", true);
        record_button.attr("disabled", true);
        pause_button.attr("disabled", false);
        pause_button.click(playSyncFile);
        pause_button.html('pause');
        stop_button.attr("disabled", false);
        play_playback_button.attr("disabled", true);
    } else {
        sync_audio[0].pause();
        pause_button.html('pause_circle_filled');
    }
}

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

    record_button.attr("disabled", true);
    synced_record_button.attr("disabled", true);
    stop_button.attr("disabled", false);
    play_playback_button.attr("disabled", true);
    pause_button.attr("disabled", false); //Pressing record activates pause & stop
    pause_button.click(pauseRecording);

    //.then is JS's weird version of a try/catch block
    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        //A wild function definition appears
        console.log("Microphone Access was allowed, going on...");
        soundStream = stream;
        audio_context = new AudioContext();
        microPhone = audio_context.createMediaStreamSource(stream);
        rec = new Recorder(microPhone, {
            numChannels: 2 //Sweet stereo
        });
        rec.record();
        rec.getBuffer(function (buffer) {
            console.log(buffer);
            encoder.encode(buffer);
        });
        console.log("Now recording");
    }).catch(function(err) {
        console.log("Failed to get microphone input, user may try again");
        record_button.attr("disabled", false);
        stop_button.attr("disabled", true);
        pause_button.attr("disabled", true);
    });
}

function pauseRecording() {
    console.log("pauseButton clicked rec.recording=", rec.recording);
    if(rec.recording) {
        if(synced_recording) {
            sync_audio[0].pause();
        }
        rec.stop();
        pause_button.html("pause_circle_filled");
    } else {
        if(synced_recording) {
            sync_audio[0].play();
        }
        rec.record();
        pause_button.html("pause");
    }
}

function stop() {
    if(synced_recording) {
        synced_recording = false;
    }
    sync_audio[0].pause();
    sync_audio[0].currentTime = 0; //Zurückspulen
    play_playback_button.attr("disabled", false);
    console.log("stopButton clicked");
    //disable the stop and pause, enabled both recording buttons
    stop_button.attr("disabled", true);
    record_button.attr("disabled", false);
    pause_button.attr("disabled", true);
    synced_record_button.attr("disabled", false);
    //reset button just in case the recording is stopped while paused
    pause_button[0].innerHTML = "pause";
    pause_button.unbind("click");
    if(rec.recording) {
        //tell the recorder to stop the recording
        rec.stop(); //stop microphone access
        soundStream.getAudioTracks()[0].stop(); //?
        //$(clicked_item).css("background-color", 'blue');
        //create the wav blob and pass it on to createDownloadLink
        rec.exportWAV(createDownloadLink);
    }
}

function createDownloadLink(blob) {
    var wav_url = URL.createObjectURL(blob); //Pretty nice API, creates a "URL" for any in-memory blob
    let ogg_url;
    var audio_element = document.createElement('audio');
    var list_element = document.createElement('li');
    var link_element = document.createElement('a');
    var upload_element = document.createElement("a");
    ogg_url = URL.createObjectURL(encoder.finish());
    link_element.href = ogg_url;
    audio_element.controls = true; //See https://www.w3schools.com/tags/tag_audio.asp
    audio_element.src = wav_url;
    link_element.download = new Date().toISOString() + '.ogg'; //Suggested filename for downloading
    $(link_element).addClass("material-icons");
    $(upload_element).addClass("material-icons");
    link_element.innerHTML = "cloud_download";
    upload_element.innerHTML = "cloud_done";
    $(upload_element).click(function () {
        if(window.confirm("Diese Aufnahme hochladen?")) {

        }
    });
    list_element.appendChild(audio_element);
    $(list_element).addClass('mdl-list__item');
    list_element.appendChild(link_element);
    list_element.appendChild(upload_element);
    recordings_list.append(list_element);
    //recordings_list.height(recordings_list.height() + 100);
    $(clicked_item).innerHeight($(clicked_item).innerHeight() + 100);
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
    };

    record_button.attr("disabled", true);
    synced_record_button.attr("disabled", true);
    stop_button.attr("disabled", false);
    play_playback_button.attr("disabled", true);
    pause_button.attr("disabled", false); //Pressing record activates pause & stop
    pause_button.click(pauseRecording);

    //.then is JS's weird version of a try/catch block
    navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
        //A wild function definition appears
        console.log("Microphone Access was allowed, going on...");
        soundStream = stream;
        audio_context = new AudioContext();
        sync_audio[0].currentTime = 0;
        microPhone = audio_context.createMediaStreamSource(stream);
        rec = new Recorder(microPhone, {
            numChannels: 2 //Sweet stereo
        });
        rec.record();
        sync_audio[0].play();
        console.log("Now recording");
    }).catch(function(err) {
        console.log("Failed to get microphone input, user may try again");
        record_button.disabled = false;
        stop_button.disabled = true;
        pause_button.disabled = true;
    });
}


