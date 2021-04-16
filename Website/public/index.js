// const gauge = require('canvas-gauges');
// const chart = require('chart.js');
// var app = require('./server');
// import { io } from "socket.io-client";

const socket = io('http://localhost:3000');

socket.connect();

socket.on('send_data', function (data) {
    updateCruiseStatus(data['Cruise State']);
    // console.log('Cruise State: ' + data['Cruise State']);
    updateSpeed(set_speed_gauge, data['Set Speed']);
    // console.log('Set Speed: ' + data['Set Speed']);
    updateSpeed(actual_speed_gauge,data['Actual Speed']);
    // console.log('Actual Speed: ' + data['Actual Speed']);
    updateGraph(data['Time'], data['Current']);
    // console.log('Current: ' + data['Current']);
    updateBattery(data['Battery']);
    // console.log('Battery: ' + data['Battery']);
});



let currs = [];
let secs = [];

let set_speed_gauge = newSpeedGauge('setspeed');
let actual_speed_gauge = newSpeedGauge('actualspeed');
let input_data = [
    ["1", "24.56", "4.0", "4.5", "15.75", "0"],
    ["1", "24.50", "4.5", "4.5", "10.01", "1"],
    ["0", "24.48", "5.1", "4.5", "20.89", "2"],
    ["0", "24.40", "5.0", "4.8", "20.01", "3"],
    ["1", "23.17", "4.8", "4.8", "5.35", "4"],
    ["1", "23.15", "5.0", "8.0", "28.75", "5"],
    ["1", "12.00", "10.8", "10.8", "0.00", "6"],
    ["1", "24.56", "4.0", "4.5", "15.75", "7"],
    ["1", "24.50", "4.5", "4.5", "10.01", "8"],
    ["0", "24.48", "5.1", "4.5", "20.89", "9"],
    ["0", "24.40", "5.0", "4.8", "20.01", "10"],
    ["1", "23.17", "4.8", "4.8", "5.35", "11"],
    ["1", "23.15", "5.0", "8.0", "28.75", "12"],
    ["0", "12.00", "10.8", "10.8", "0.00", "13"],
    ["1", "24.50", "4.5", "4.5", "10.01", "14"],
    ["0", "24.48", "5.1", "4.5", "20.89", "15"],
    ["0", "24.40", "5.0", "4.8", "20.01", "16"],
    ["1", "23.17", "4.8", "4.8", "5.35", "17"],
    ["1", "23.15", "5.0", "8.0", "28.75", "18"],
    ["1", "12.00", "10.8", "10.8", "0.00", "19"],
    ["1", "24.56", "4.0", "4.5", "15.75", "20"],
    ["1", "24.50", "4.5", "4.5", "10.01", "21"],
    ["0", "24.48", "5.1", "4.5", "20.89", "22"],
    ["0", "24.40", "5.0", "4.8", "20.01", "23"],
    ["1", "23.17", "4.8", "4.8", "5.35", "24"],
    ["1", "23.15", "5.0", "8.0", "28.75", "25"],
    ["0", "12.00", "10.8", "10.8", "0.00", "26"],
    ["1", "24.50", "4.5", "4.5", "10.01", "27"],
    ["0", "24.48", "5.1", "4.5", "20.89", "28"],
    ["0", "24.40", "5.0", "4.8", "20.01", "29"],
    ["1", "23.17", "4.8", "4.8", "5.35", "30"],
    ["1", "23.15", "5.0", "8.0", "28.75", "31"],
    ["1", "12.00", "10.8", "10.8", "0.00", "32"],
    ["1", "24.56", "4.0", "4.5", "15.75", "33"],
    ["1", "24.50", "4.5", "4.5", "10.01", "34"],
    ["0", "24.48", "5.1", "4.5", "20.89", "35"],
    ["0", "24.40", "5.0", "4.8", "20.01", "36"],
    ["1", "23.17", "4.8", "4.8", "5.35", "37"],
    ["1", "23.15", "5.0", "8.0", "28.75", "38"],
    ["0", "12.00", "10.8", "10.8", "0.00", "39"]
];


for(let i=0;i<secs.length;i++)
{
    secs[i] = i+1;
}

function newSpeedGauge(renderLocation){
    return new RadialGauge({
        renderTo: document.getElementById(renderLocation),
        title: "Speed",
        width: 300,
        height: 300,
        units: "MPH",
        colorUnits: "white",
        minValue: 0,
        maxValue: 10,
        majorTicks: [0,1,2,3,4,5,6,7,8,9,10],
        colorMajorTicks: "white",
        minorTicks: 3,
        colorMinorTicks: "white",
        strokeTicks: true,
        colorNumbers: "white",
        highlights: {from:7, to:10, color:"red"},
        colorPlate: "#262626",
        colorPlateEnd: "#363636",
        colorBorderOuter: "white",
        colorBorderOuterEnd: "white",
        borderOuterWidth: 5,
        borderMiddleWidth: 0,
        borderInnerWidth: 0,
        borderShadowWidth: 0,
        borders: true,
        needleType: "arrow",
        needleWidth: 2,
        needleCircleSize: 7,
        needleCircleOuter: true,
        needleCircleInner: false,
        colorNeedle: "red",
        colorNeedleEnd: "red",
        animationDuration: 1000,
        animationRule: "linear",
        colorValueText: "aqua",
        colorValueBoxBackground: "#363636",
        valueBoxStroke: false,
        valueInt: 1,
        valueDec: 2,
    })
}


// TODO: need to make curr_graph size responsive
let graph_ctx = document.getElementById('graph')
let curr_graph = new Chart(graph_ctx,{
    type: 'line',
    data: {
        labels: secs,
        datasets: [{
            label: 'Current',
            data: currs,
            backgroundColor: 'rgba(255, 99, 132, 0.4)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
    },
    options: {
        legend:
            {
                display:false
            },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    fontColor: 'rgba(255, 255, 255, 1)',
                    fontSize: 14
                },
                gridLines: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Current (A)',
                    fontColor: 'rgba(255, 255, 255, 1)',
                    fontSize: 20
                }
            }],
            xAxes: [{
                ticks: {
                    beginAtZero: true,
                    fontColor: 'rgba(255, 255, 255, 1)',
                    fontSize: 14
                },
                gridLines: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Time (s)',
                    fontColor: 'rgba(255, 255, 255, 1)',
                    fontSize: 20
                }
            }]

        },

    }
})

// if value >= 10, valueInt:2
actual_speed_gauge.update()
set_speed_gauge.update()


/** TODO: Implement the following function for speed gauges updates*/
 function updateSpeed(gauge, spd) {
    gauge.value = spd;
 }


/** TODO: Implement the following function for cruise state updates*/
 function updateCruiseStatus(state) {
    let c = document.getElementById("cruise_state");
    if(state)
    {
        c.checked = true;
    }
    else
    {
        c.checked = false;
    }
 }


/** TODO: Implement the following function for battery updates*/
function updateBattery(bat_pct) {
    let bat_img = document.getElementById("bat_lvl")
    if (bat_pct > 80)
    {
        bat_img.src = "Images/Battery/battery5.png";
    }
    else if (bat_pct > 60)
    {
        bat_img.src = "Images/Battery/battery4.png";
    }
    else if (bat_pct > 40)
    {
        bat_img.src = "Images/Battery/battery3.png";
    }
    else if (bat_pct > 20)
    {
        bat_img.src = "Images/Battery/battery2.png";
    }
    else if (bat_pct > 10)
    {
        bat_img.src = "Images/Battery/battery1.png";
    }
    else if (bat_pct > 0)
    {
        bat_img.src = "Images/Battery/battery0.png";
    }
 }


/** TODO: Implement the following function for graph updates*/
function updateGraph(sec, curr) {
    if(secs.length >= 15)
        secs.shift();
    secs.push(sec);
    if(currs.length >= 15)
        currs.shift();
    currs.push(curr);
    curr_graph.update();

}


// function sleep(ms) {
//     return new Promise(resolve => setTimeout(resolve, ms));
// }
//
// // for testing:
// async function fileTester(data)
// {
//     for(let i=0;i<data.length;i++)
//     {
//         updateCruiseStatus(Boolean(parseInt(data[i][0])));
//         updateBattery(parseFloat(data[i][1]));
//         updateSpeed(actual_speed_gauge, parseFloat(data[i][2]));
//         updateSpeed(set_speed_gauge, parseFloat(data[i][3]));
//         updateGraph(parseInt(data[i][5]), parseFloat(data[i][4]));
//         await sleep(800);
//     }
// }

// fileTester(input_data);
