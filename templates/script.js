var recognition = new webkitSpeechRecognition();
recognition.interimResults = false;
recognition.maxAlternatives = 1;
recognition.continuous = true;
recognition.lang = "en-US"

var listening = false;  // continue listening flag
var previousText = '';
let wakeLock = null;
let devilMode = false;

// Toggle chess mode 
$("#devil").click(function() {
  devilMode = !devilMode;
});





recognition.onresult = function(event) {
    var transcribedText = event.results[event.results.length-1][0].transcript;

    
    document.getElementById('transcribed-text').innerText = transcribedText;
    console.log(transcribedText)

    
    var wordCount = transcribedText.split(' ').length;
    if (wordCount < 2) {

        previousText += ' ' + transcribedText;
    } else {

        
        var finalText = previousText + ' ' + transcribedText;
        finalText += '. ';
        console.log("sending post:"+ finalText)
        $.post("/start_listening", { 'transcribed-text': finalText,
                                     'devilMode': devilMode}, function(data) {
            speak(data);
        });
        previousText = '';  // reset previous texct
    }
  if (listening) {
      recognition.start();
  }
    
};

recognition.onerror = function(event) {
    console.error('Speech recognition error:', event.error);
};

recognition.onend = function() {
    console.log('Speech recognition ended');
    if (listening) {
        recognition.start();
    }
};


function speak(text) {
    var msg = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(msg);
}

$(document).ready(function(){
    $("#start").click(function(){
        listening = true;
        console.log("Start button clicked");
        recognition.start();
        navigator.wakeLock.request('screen').then(function(lock) {
            console.log('wake lock acquired');
            wakeLock = lock;
        });
    });

    $("#stop").click(function(){
        listening = false;
        console.log("Stop button clicked");
        recognition.stop();
        if (wakeLock !== null) {
            wakeLock.release().then(function() {
                console.log('wake lock released');
                wakeLock = null;
            });
        }
    });

    $("#clear").click(function(){
        $.post("/clear_session")
        console.log("clear session clicked");
    });
});
