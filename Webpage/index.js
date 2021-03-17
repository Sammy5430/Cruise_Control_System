var gauge = new RadialGauge({
    renderTo: document.getElementById('battery'),
    width: 300,
    height: 300,
    units: "mph",
    minValue: 0,
    maxValue: 10,
    majorTicks: [1,2,3,4,5,6,7,8,9,10],
    minorTicks: 5,
    strokeTicks: true,
    highlights: {from:7, to:10, color:"red"},
    colorPlate: "white",
    borderShadowWidth: 0,
    borders: false,
    needleType: "arrow",
    needleWidth: 2,
    needleCircleSize: 7,
    needleCircleOuter: true,
    needleCircleInner: false,
    animationDuration: 1000,
    animationRule: "linear"
})

// document.body.appendChild(gauge.options.renderTo);

var canvas = document.getElementById('setspeed');
var ctx = canvas.getContext('2d');

ctx.fillStyle = 'green';
ctx.fillRect(10, 10, 100, 100);
