// ------------------ GLOBAL STUFF ------------------------------------------
const SERVER_ADDRESS = '127.0.0.1';
const SESSION_URL = 'http://' + SERVER_ADDRESS + '/api/session/';
const ROVER_URL = 'http://' + SERVER_ADDRESS + '/api/rover/';
let aux = window.location.href.split("/");
const ROVER_ID = aux[aux.length -2];
const MAX_RETRIES = 3;
const MAX_POINTS_PER_GRAPH = 100;

let BATTERY_CANVAS;

// Internal variables
let roverAddress = null;
let retryCounter;
let battery_degrees;


// Session information
let sessionID = null;
let start_timestamp;
let start_timestamp_millis;
let timestamp;
let timestamp_relative;
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

// Chart canvas
let temperatureChart;
let pressureChart;
let humidityChart;
let altitudeChart;
let batteryGauge;
let map_position;
let initial_coord =[43.53037718011077, -5.669762979443579];
let end_coord=[43.52940122542376, -5.661973088851047];
let coordenadas=[initial_coord,end_coord];

// -------------------------- MAIN LOGIC ----------------------------------------

window.onload = function(){
    BATTERY_CANVAS = document.getElementById("batteryCanvas");

    let temperature_canvas = document.getElementById("temperatureCanvas");
    let pressure_canvas = document.getElementById("pressureCanvas");
    let humidity_canvas = document.getElementById("humidityCanvas");
    let altitude_canvas = document.getElementById("altitudeCanvas");
    let map = document.getElementById("map");
    temperatureChart = initializeChart(temperature_canvas, 'Tiempo desde inicio de sesión (s)', 'Temperatura (ºC)');
    pressureChart = initializeChart(pressure_canvas, 'Tiempo desde inicio de sesión (s)', 'Presión (hPa)');
    humidityChart = initializeChart(humidity_canvas, 'Tiempo desde inicio de sesión (s)', 'Humedad (%)');
    altitudeChart = initializeChart(altitude_canvas, 'Tiempo desde inicio de sesión (s)', 'Altitud (m)', true);
    map_position=initializeMap(map,coordenadas);
    initializeSessionData();
    requestRoverData();
    setInterval(requestSessionData, 1100);
};





// ----------------------------------------------------------------------------


function initializeMap(map,coordenadas){
    console.log("inicializando mapa");
    console.log("deberia de init mapa");

    map_position=L.map(map, {
        center: coordenadas[0],
        zoom: 17,
        maxBounds: coordenadas[0],
        minZoom: 5,
        maxZoom: 24 });
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
                maxZoom: 40,
                maxNativeZoom: 19
            }).addTo(map_position);
    L.control.scale().addTo(map_position);


    return map_position

}


function initializeSessionData(){
    console.log("Initializing session data...");

    // Internal variables
    retryCounter = 0;

    // Session information
    start_timestamp = null;
    start_timestamp_millis = null;
    timestamp = null;
    timestamp_relative = null;
    session_state = null;
    session_substate = null;
    battery = null;
    battery_degrees = null;
    rssi = null;
    error_list = [];  // TODO: Error list

    // Sensor information
    temperature = 1;
    pressure = null;
    humidity = null;

    // Position information
    latitude = null;
    longitude = null;
    altitude = null;


    // Charts
    deleteChartData(temperatureChart);
    deleteChartData(pressureChart);
    deleteChartData(humidityChart);
    deleteChartData(altitudeChart);
    batteryGauge = redrawGauge(BATTERY_CANVAS, 0)
}




function initializeChart(canvas, xlabel=null, ylabel=null, fill=false){
    // data: [{ x: 10, y: 5 }]
    return new Chart(canvas, {
        type: 'scatter',
        data: {
            datasets: [{
                borderColor: 'rgba(0, 204, 219, 0.6)',
                showLine: true,
                fill: fill,
                data: [],
            }]
        },
        options: {
            responsive: true,
            legend: {
                display: false
            },
            scales: {
                xAxes: [ {
                    display: true,
                    scaleLabel: {
                        display: (xlabel !== null),
                        labelString: xlabel
                    }
                } ],
                yAxes: [ {
                    display: true,
                    scaleLabel: {
                        display: (ylabel !== null),
                        labelString: ylabel
                    }
                } ]
            }
        },
    });
}


function addChartData(chart, new_x, new_y){
    let num_points = chart.data.datasets[0].data.length;
    chart.data.datasets[0].data.push({x: new_x, y: new_y});
    if (num_points >= MAX_POINTS_PER_GRAPH)
        chart.data.datasets[0].data.shift();
    chart.update();
}


function deleteChartData(chart){
    chart.data.datasets[0].data = [];
    chart.update();
}


function redrawGauge(canvas, degrees){
    let ctx = canvas.getContext("2d");
    let width = canvas.width;
    let height = canvas.height;
    let bgcolor = "#222";
    let color = "#b2c831";
    ctx.clearRect(0, 0, width, height);

    //Background 360 degree arc
    ctx.beginPath();
    ctx.strokeStyle = bgcolor;
    ctx.lineWidth = 30;
    ctx.arc(width/2, height/2, 100, 0, Math.PI*2, false); //you can see the arc now
    ctx.stroke();

    //gauge will be a simple arc
    let radians = degrees * Math.PI / 180;
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 30;
    //The arc starts from the rightmost end. If we deduct 90 degrees from the angles
    //the arc will start from the topmost end
    ctx.arc(width/2, height/2, 100, 0 - 90*Math.PI/180, radians - 90*Math.PI/180, false);
    ctx.stroke();

    ctx.fillStyle = color;
    ctx.font = "50px open sans";
    let text = Math.round((battery !== null) ? battery : 0) + "%";
    let text_width = ctx.measureText(text).width;
    ctx.fillText(text, width/2 - text_width/2, height/2 + 15);
}


function loadInteractionSection(){  // TODO: Interaction section

}


function handleSessionJSON(new_json){
    if ((new_json.timestamp === undefined) || (new_json.timestamp === timestamp)){
        retryCounter++;
        if (retryCounter === MAX_RETRIES){
            retryCounter = 0;
            requestRoverData();
        }
        return;
    }
    retryCounter = 0;

    if (start_timestamp === null && (new_json.start_time !== undefined)){
        start_timestamp = new_json.start_time;
        start_timestamp_millis = Date.parse(start_timestamp);
    }
    timestamp = new_json.timestamp;
    if (start_timestamp !== null)
        timestamp_relative = (Date.parse(timestamp) - start_timestamp_millis)/1000;
    console.log(`timestamp: ${timestamp}`);
    session_state = (new_json.session_state !== undefined) ? new_json.session_state : null;
    session_substate = (new_json.session_substate !== undefined) ? new_json.session_substate : null;
    battery = (new_json.battery !== undefined) ? new_json.battery : null;
    rssi = (new_json.rssi !== undefined) ? new_json.rssi : null;
    temperature = (new_json.temperature !== undefined) ? new_json.temperature : null;
    pressure = (new_json.pressure !== undefined) ? new_json.pressure : null;
    humidity = (new_json.humidity !== undefined) ? new_json.humidity : null;
    latitude = (new_json.latitude !== undefined) ? new_json.latitude : null;
    longitude = (new_json.longitude !== undefined) ? new_json.longitude : null;
    altitude = (new_json.altitude !== undefined) ? new_json.altitude : null;

    populateSessionFields();
    updateCharts();
}


function populateSessionFields(){
    // Session Information
    document.getElementById("sessionIDField").innerHTML = (sessionID !== null) ? sessionID : '--';
    document.getElementById("sessionStateField").innerHTML = (session_state !== null) ? session_state : '--';
    document.getElementById("sessionSubStateField").innerHTML = (session_substate !== null) ? session_substate : '--';
    document.getElementById("batteryField").innerHTML = (battery !== null) ? battery.toFixed(1) + ' %' : '--';
    document.getElementById("rssiField").innerHTML = (rssi !== null) ? rssi.toFixed(2) + ' dB' : '--';
    let error_content = "";
    for (let n=0; n < error_list.length; n++){
        error_content += "<li>" + error_list[n] + "</li>";
    }
    document.getElementById("errorList").innerHTML = error_content;

    // Sensor information
    document.getElementById("temperatureField").innerHTML = (temperature !== null) ? temperature.toFixed(1) + ' ºC' : '--';
    document.getElementById("pressureField").innerHTML = (pressure !== null) ? pressure.toFixed(1) + ' hPa' : '--';
    document.getElementById("humidityField").innerHTML = (humidity !== null) ? humidity.toFixed(1) + ' %' : '--';

    // Position information
    document.getElementById("latitudeField").innerHTML = (latitude !== null) ? latitude.toFixed(6) + ' deg' : '--';
    document.getElementById("longitudeField").innerHTML = (longitude !== null) ? longitude.toFixed(6) + ' deg' : '--';
    document.getElementById("altitudeField").innerHTML = (altitude !== null) ? altitude.toFixed(2) + ' m' : '--';
}


function updateCharts(){
    addChartData(temperatureChart, timestamp_relative, temperature);
    addChartData(pressureChart, timestamp_relative, pressure);
    addChartData(humidityChart, timestamp_relative, humidity);
    addChartData(altitudeChart, timestamp_relative, altitude);
    redrawGauge(BATTERY_CANVAS, Math.round(battery*360/100));
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


function deleteRover(rover_id){
    if (confirm("¿Estás seguro de querer eliminar el rover " + rover_id + " y todos sus datos almacenados?")){
        fetch('/api/rover/' + rover_id + '/', {
            method: 'delete'
        }).then();
        window.location.href = "/";
    }
}



