// ------------------ GLOBAL STUFF ------------------------------------------
const SERVER_ADDRESS = '127.0.0.1';
const SESSION_URL = 'http://' + SERVER_ADDRESS + '/api/session/';
const ROVER_URL = 'http://' + SERVER_ADDRESS + '/api/rover/';
let aux = window.location.href.split("/");
const ROVER_ID = aux[aux.length -2];
const MAX_RETRIES = 3;

// Internal variables
let roverAddress = null;
let retryCounter;
// let roverUpdateIntervalID;
// let sessionUpdateIntervalID;

// Session information
let sessionID = null;
let timestamp;
let session_state;
let session_substate;
let battery;
let rssi;
let error_list;

// Sensor information
let temperature;
let pressure;
let humidity;

// Position information
let latitude;
let longitude;
let altitude;


// -------------------------- MAIN LOGIC ----------------------------------------

initializeSessionData();
requestRoverData();
setInterval(requestSessionData, 1100);




// ----------------------------------------------------------------------------

function deleteRover(rover_id){
    if (confirm("¿Estás seguro de querer eliminar el rover " + rover_id + " y todos sus datos almacenados?")){
        fetch('/api/rover/' + rover_id + '/', {
            method: 'delete'
        }).then();
        window.location.href = "/";
    }
}


function initializeSessionData(){
    // Internal variables
    retryCounter = 0;

    // Session information
    timestamp = null;
    session_state = null;
    session_substate = null;
    battery = null;
    rssi = null;
    error_list = [];  // TODO: Error list

    // Sensor information
    temperature = null;
    pressure = null;
    humidity = null;

    // Position information
    latitude = null;
    longitude = null;
    altitude = null;
}


function loadInteractionSection(){  // TODO: Interaction section

}


function handleSessionJSON(json){
    if ((json.timestamp === undefined) || (json.timestamp === timestamp)){
        retryCounter++;
        if (retryCounter === MAX_RETRIES){
            retryCounter = 0;
            requestRoverData();
        }
        return;
    }
    timestamp = (json.timestamp !== undefined) ? json.timestamp : null;
    session_state = (json.session_state !== undefined) ? json.session_state : null;
    session_substate = (json.session_substate !== undefined) ? json.session_substate : null;
    battery = (json.battery !== undefined) ? json.battery : null;
    rssi = (json.rssi !== undefined) ? json.rssi : null;
    temperature = (json.temperature !== undefined) ? json.temperature : null;
    pressure = (json.pressure !== undefined) ? json.pressure : null;
    humidity = (json.humidity !== undefined) ? json.humidity : null;
    latitude = (json.latitude !== undefined) ? json.latitude : null;
    altitude = (json.altitude !== undefined) ? json.altitude : null;

    populateSessionFields();
}


function populateSessionFields(){
    // Session Information
    document.getElementById("sessionIDField").innerHTML = (sessionID !== null) ? sessionID : '--';
    document.getElementById("sessionStateField").innerHTML = (session_state !== null) ? session_state : '--';
    document.getElementById("sessionSubStateField").innerHTML = (session_substate !== null) ? session_substate : '--';
    document.getElementById("batteryField").innerHTML = (battery !== null) ? battery : '--';
    document.getElementById("rssiField").innerHTML = (rssi !== null) ? rssi : '--';
    let error_content = "";
    for (let n=0; n < error_list.length; n++){
        error_content += "<li>" + error_list[n] + "</li>";
    }
    document.getElementById("errorList").innerHTML = error_content;

    // Sensor information
    document.getElementById("temperatureField").innerHTML = (temperature !== null) ? temperature + ' ºC' : '--';
    document.getElementById("pressureField").innerHTML = (pressure !== null) ? pressure + ' hPa' : '--';
    document.getElementById("humidityField").innerHTML = (humidity !== null) ? humidity + ' ???' : '--';

    // Position information
    document.getElementById("latitudeField").innerHTML = (latitude !== null) ? latitude + ' ºC' : '--';
    document.getElementById("longitudeField").innerHTML = (longitude !== null) ? longitude + ' hPa' : '--';
    document.getElementById("altitudeField").innerHTML = (altitude !== null) ? altitude + ' ???' : '--';
}


function requestSessionData(){
    if (sessionID === null)
        return;
    const url = SESSION_URL + sessionID + '/';
    const http = new XMLHttpRequest();
    http.open("GET", url, true);
    http.responseType='text';
    http.send();
    http.onreadystatechange = function () {
        if(this.readyState === 4 && this.status === 200) {
            const response = JSON.parse(http.responseText);
            handleSessionJSON(response);
            console.log("Session request: ", response);
        }
    }
}


function requestRoverData(){
    const url = ROVER_URL + ROVER_ID + '/';
    const http = new XMLHttpRequest();
    http.open("GET", url, true);
    http.responseType='text';
    http.send();
    http.onreadystatechange = function () {
        if(this.readyState === 4 && this.status === 200) {
            const response = JSON.parse(http.responseText);
            if ((roverAddress !== response.address) && (response.address !== undefined)){
                roverAddress = response.address;
                loadInteractionSection();
            }
            if ((sessionID !== response.last_session) && (response.last_session !== undefined)){
                sessionID = response.last_session;
                initializeSessionData();
            }
            console.log("Rover request: ", response);
        }

    }
}



