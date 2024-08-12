// ----------------------------- THINGS TO CHANGE -----------------------------

var accessToken = 'YOUR ACCESS TOKEN HERE';
const project_id = 'YOUR PROJECT ID HERE';
const device_id = 'YOUR DEVICE ID HERE';
const oauth2_client_id = 'YOUR CLIENT ID HERE';
const oauth2_client_secret = 'YOUR CLIENT SECRET HERE';
const refresh_token = 'YOUR REFRESH TOKEN HERE';

// ----------------------------- END OF THINGS TO CHANGE -----------------------------

var pc = null;

const localOfferOptions = {
    offerToReceiveVideo: 1,
    offerToReceiveAudio: 1,
  };

var mediaSessionId;
var answerSDP;

function negotiate() {
    localSendChannel = pc.createDataChannel('dataSendChannel', null);
    return pc.createOffer(localOfferOptions).then(function(offer) {
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        console.log(offer.sdp);
        return fetch(`https://smartdevicemanagement.googleapis.com/v1/enterprises/${project_id}/devices/${device_id}:executeCommand`, {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              command: 'sdm.devices.commands.CameraLiveStream.GenerateWebRtcStream',
              params: {
                offerSdp: offer.sdp
              }
            })
          }).then(function(response) {
            if (!response.ok) {
                throw new Error(`${response.status}`);
            }
            return response.json();
        }).then(function(answer) {
            answerSDP = answer["results"].answerSdp;
            mediaSessionId = answer["results"].mediaSessionId;
            console.log(answerSDP);
            if (answerSDP[answerSDP.length - 1] !== '\n') {
                answerSDP += '\n';
            }
            return pc.setRemoteDescription({ "type": "answer", "sdp": answerSDP });
        }).catch(function(error) {
            console.error('Error in generate WebRTC stream:', error);
            throw error; // re-throw to propagate the error
        });
    }).catch(function(e) {
        if(e == 'Error: 401') {
            console.log('Access token expired, refreshing token');
            return fetch(`https://www.googleapis.com/oauth2/v4/token?client_id=${oauth2_client_id}&client_secret=${oauth2_client_secret}&refresh_token=${refresh_token}&grant_type=refresh_token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(function(response) {
                return response.json();
            }).then(function(response) {
                accessToken = response['access_token'];
                console.log('Access token refreshed');
                return negotiate(); // return the promise of negotiate
            }).catch(function(error) {
                console.error('Error refreshing token:', error);
                throw error; // re-throw to propagate the error
            });
        }
    });
}

function start() {
    var config = {
        sdpSemantics: 'unified-plan'
    };
    pc = new RTCPeerConnection(config);

    // connect audio / video
    pc.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video') {
            document.getElementById('video').srcObject = evt.streams[0];
        }
    });

    negotiate();
}

function stop() {

    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);

    // Make the fetch request
    fetch(`https://smartdevicemanagement.googleapis.com/v1/enterprises/${project_id}/devices/${device_id}:executeCommand`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`
        },
        body: JSON.stringify({
            command: 'sdm.devices.commands.CameraLiveStream.StopWebRtcStream',
            params: {
                mediaSessionId: `${mediaSessionId}`
            }
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to stop the WebRTC stream');
        }
        console.log('WebRTC stream stopped successfully');
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

