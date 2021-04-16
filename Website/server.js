const express = require('express');
const path = require('path');
const app = express();

//set port
app.set('port', 3000);

//static file
app.use(express.static(path.join(__dirname, 'public')));

//Start server
const server = app.listen(app.get('port'), () => {
    console.log('Server listening at http://localhost:3000')
    });


const SocketIO = require('socket.io');

//Socket.io server config
const io = SocketIO(server);

//connection event
io.on('connection', (socket) => {
    console.log('a user connected');
    socket.on('data_update', (data) => {
        console.log('recibi alguito', data);
        io.emit('send_data', data);
        console.log('envie alguito');
    });
});




