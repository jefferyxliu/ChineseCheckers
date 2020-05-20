const PORT = 3000
const io = require('socket.io')(PORT)

//object to track clients
const users = {}

//When a socket connects to the server
io.on('connection', socket => {
    
    console.log(`new connection from ${socket.id}`)
    
    //when username is entered, track name in users, send user-connected message to all clients
    socket.on('new-user', name => {
        users[socket.id] = name
        console.log(`${name} joined.`)
        socket.broadcast.emit('user-connected', name)
    })
    
    //when server receives message, send chat message to all clients
    socket.on('send-chat-message', message => {
        console.log(`message from ${users[socket.id]}: ${message}`)
        socket.broadcast.emit('chat-message', {message: message, name: users[socket.id]})
    })
    
    //when client disconnects, send user-disconnect message to all clients
    socket.on('disconnect', () => {
        socket.broadcast.emit('user-disconnected', users[socket.id])
        console.log(`${users[socket.id]} joined.`)
        delete users[socket.id]
    })

    //when server receives command
    //TO DO figure out import ChineseCheckers.js, implement commands
    socket.on('send-command', command => {
        if (command.function === 'set_up') {
            
        }
        if (command.function === 'reset') {

        }
        if (command.function === 'is_legal') {

        }
        if (command.function === 'move') {

        }
    })
    
})