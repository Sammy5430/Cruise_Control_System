function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

var currs = [12, 19, 3, 5, 2, 3, 19, 3, 5, 2, 3, 19, 3, 5, 2, 3, 19, 3, 5, 2, 3, 2 ,3 , 4, 5, 6, 2 ,3 , 4, 5, 6];
var secs = new Array(30);

for(var i=0;i<secs.length;i++)
{
    secs[i] = i+1;
}

// To update array:
// arr.shift();  to remove first element
// arr.push(); to add new element at the end

let set_speed_gauge = new RadialGauge({
    renderTo: document.getElementById('setspeed'),
    title: "Set Speed",
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

let actual_speed_gauge = new RadialGauge({
    renderTo: document.getElementById('actualspeed'),
    title: "Actual Speed",
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
    valueDec: 2
})

// need to make curr_graph size responsive
let graph_ctx = document.getElementById('graph')
let curr_graph = new Chart(graph_ctx,{
    type: 'line',
    data: {
        labels: secs,
        datasets: [{
            label: 'Current',
            data: currs,
            backgroundColor: 'rgba(255, 99, 132, 0.4)'
            ,
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
    },
    options: {
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
                    labelString: 'Current (mA)',
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
// if value < 10, valueInt:2
actual_speed_gauge.update()
set_speed_gauge.update({value:8.5})

// for(var i=10;i<=60;i++)
// {
//     if(secs.length >= 30)
//         secs.shift();
//     secs.push(i);
//     curr_graph.update();
//     sleep(10000);
// }
/*
function updateGraph(sec, curr)
{
    if(secs.length >= 30)
        secs.shift();
    secs.push(sec);
    if(currs.length >= 30)
        currs.shift();
    currs.push(curr);
    curr_graph.update();

}
 */
