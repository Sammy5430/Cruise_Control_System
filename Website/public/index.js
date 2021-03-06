const socket = io('http://ccet.ece.uprm.edu');

socket.connect();

socket.on('send_data', function (data) {
    updateCruiseStatus(data['Cruise State']);
    updateSpeed(set_speed_gauge, data['Set Speed']);
    updateSpeed(actual_speed_gauge, data['Actual Speed']);
    updateSpdGraph(data['Time'], data['Set Speed'], data['Actual Speed']);
    updateBattery(data['Battery']);
});


let secs = [];
let act_spds = [];
let set_spds = [];
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
let spd_graph = new Chart(graph_ctx,{
    type: 'line',
    data: {
        labels: secs,
        datasets: [{
            label: 'Actual Speed',
            data: act_spds,
            borderColor: 'rgb(2,255,237)',
            borderWidth: 1
        },{
            label: 'Set Speed',
            data: set_spds,
            borderColor: 'rgb(34,255,80)',
            borderWidth: 1
        }]
    },
    options: {
        legend:
            {
                display:true
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
                    labelString: 'Speed (mph)',
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
    gauge.update()
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
    else
    {
        bat_img.src = "Images/Battery/low_battery.png";
    }
 }

function updateSpdGraph(sec, set_spd, act_spd) {
    if (sec === 0) {
        while (secs.length > 0)
            secs.pop();
        while (set_spds.length > 0)
            set_spds.pop();
        while (act_spds.length > 0)
            act_spds.pop();
    }
    if (secs.length >= 15)
        secs.shift();
    if (set_spds.length >= 15)
        set_spds.shift();
    if (act_spds.length >= 15)
        act_spds.shift();
    if (secs.length > 1) {
        if (Math.floor(sec) > secs[secs.length-1]) {
            secs.push(Math.floor(sec));
        }
    }
    else{
        secs.push(Math.floor(sec));
    }
    set_spds.push(set_spd);
    act_spds.push(act_spd);
    spd_graph.update();
}