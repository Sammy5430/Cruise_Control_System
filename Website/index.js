function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

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

let currs = [];
let secs = new Array();
for(let i=0;i<secs.length;i++)
{
    secs[i] = i+1;
}

let set_speed_gauge = new RadialGauge({
    renderTo: document.getElementById('setspeed'),
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

let actual_speed_gauge = new RadialGauge({
    renderTo: document.getElementById('actualspeed'),
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


// for(var i=10;i<=60;i++)
// {
//     if(secs.length >= 30)
//         secs.shift();
//     secs.push(i);
//     curr_graph.update();
//     sleep(10000);
// }

/** TODO: Implement the following function for speed gauges updates*/
 function updateSpeed(gauge, spd)
 {
    gauge.value = spd;
 }


/** TODO: Implement the following function for cruise state updates*/
 function updateCruiseStatus(state)
 {
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


//to change battery, verify received measurement and change image source
/** TODO: Implement the following function for battery updates*/
function updateBattery(volt)
 {
    let bat_img = document.getElementById("bat_lvl")
    if ((volt/25) *100 > 80)
    {
        bat_img.src = "Images/Battery/battery5.png";
    }
    else if ((volt/25) *100 > 60)
    {
        bat_img.src = "Images/Battery/battery4.png";
    }
    else if ((volt/25) *100 > 40)
    {
        bat_img.src = "Images/Battery/battery3.png";
    }
    else if ((volt/25) *100 > 20)
    {
        bat_img.src = "Images/Battery/battery2.png";
    }
    else if ((volt/25) *100 > 10)
    {
        bat_img.src = "Images/Battery/battery1.png";
    }
    else if ((volt/25) *100 > 0)
    {
        bat_img.src = "Images/Battery/battery0.png";
    }
 }


/** TODO: Implement the following function for graph updates*/
function updateGraph(sec, curr)
{
    if(secs.length >= 15)
        secs.shift();
    secs.push(sec);
    if(currs.length >= 15)
        currs.shift();
    currs.push(curr);
    curr_graph.update();

}

//for testing:
async function fileTester(data)
{
    // let reader = new FileReader();
    // let file_blob = new Blob()
    // let file_string = reader.readAsText(document.getElementById('testfile').files[0]);
    // let file_array = file_string.split(',')
    for(let i=0;i<data.length;i++)
    {
        updateCruiseStatus(Boolean(parseInt(data[i][0])));
        updateBattery(parseFloat(data[i][1]));
        updateSpeed(actual_speed_gauge, parseFloat(data[i][2]));
        updateSpeed(set_speed_gauge, parseFloat(data[i][3]));
        updateGraph(parseInt(data[i][5]), parseFloat(data[i][4]));
        await sleep(800);
    }
}

fileTester(input_data);


