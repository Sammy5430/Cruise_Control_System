const socket = io('http://ccet.ece.uprm.edu');

socket.connect();

socket.on('send_data', function (data) {
    updateCruiseStatus(data['Cruise State']);
    updateSpeed(set_speed_gauge, data['Set Speed']);
    updateSpeed(actual_speed_gauge,data['Actual Speed']);
    updateGraph(data['Time'], data['Current']);
    updateBattery(data['Battery']);
});


let currs = [];
let secs = [];
let set_speed_gauge = newSpeedGauge('setspeed');
let actual_speed_gauge = newSpeedGauge('actualspeed');


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
        valueBox: false
        // colorValueText: "aqua",
        // colorValueBoxBackground: "#363636",
        // valueBoxStroke: false,
        // valueInt: 1,
        // valueDec: 2,
    })
}


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


actual_speed_gauge.update()
set_speed_gauge.update()


 function updateSpeed(gauge, spd) {
    gauge.value = spd;
 }


 function updateCruiseStatus(state) {
    let c = document.getElementById("cruise_state");
    if(state){
        c.checked = true;
    }
    else{
        c.checked = false;
    }
 }


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


/** TODO: Clear the graph on new pi connection*/
function updateGraph(sec, curr) {
    if (sec === 0)
        while (secs.length > 0)
            secs.pop();
        while (currs.length > 0)
            currs.pop();
        curr_graph.update();
    if (secs.length >= 15)
        secs.shift();
    if (currs.length >= 15)
        currs.shift();
    if (Math.floor(sec) === parseInt(sec)) {
        secs.push(sec);
        currs.push(curr);
        curr_graph.update();
    }
}
