const express = require('express');
const path = require('path');
const app = express();

//set port
app.set('port', process.env.PORT || 3000);

//static files
app.use(express.static(path.join(__dirname, 'public')));

//Start server
const server = app.listen(app.get('port'), () => {
    console.log('Server started on port', app.get('port'));
    });


const SocketIO = require('socket.io');

//Socket.io server config
const io = SocketIO(server);

//connection event
io.on('connection', (socket) => {
    console.log('A user connected');
    socket.on('data_update', (data) => {
        io.emit('send_data', data);
    });
});




