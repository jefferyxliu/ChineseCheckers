import ChineseCheckers, {Tile, TileSet} from "./ChineseCheckers.js";
const PORT = 3000
const io = require('socket.io')(PORT)
let CC = ChineseCheckers()
//object to track clients
const users = {}

//When a socket connects to the server
io.on('connection', socket => {
    
    console.log(`new connection from ${socket.id}`)
    
    //when username is entered, track name in users, send user-connected message to all clients
    socket.on('new-user', name => {
        users[socket.id] = name
        console.log(`${name} joined.`)
        socket.emit('user-connected', name)
    })
    
    //when server receives message, send chat message to all clients
    socket.on('send-chat-message', message => {
        console.log(`message from ${users[socket.id]}: ${message}`)
        socket.emit('chat-message', {message: message, name: users[socket.id]})
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
        //command = {function: 'help', parameters: null}
        if (command.function === 'help') {
            //socket.broadcast.to(socket.id).emit('command',)
        }

        //command = {function: 'set_up', parameters: [gamemode, [colors0-5]]}
        if (command.function === 'set_up') {
            try {
                CC.set_up(...command.parameters)
                socket.emit('command', `${users[socket.id]} set up a game for ${command.parameters[0]} people.`)
                socket.emit('board', CC.to_rect())
            } catch (error) {
                socket.broadcast.to(socket.id).emit('command', 'Error: set up failed.')
            }
        }
        //command = {function: 'reset', parameters: null}
        if (command.function === 'reset') {
            CC.reset()
            socket.emit('command', `${users[socket.id]} reset the board.`)
            socket.emit('board', CC.to_rect())
        }
        //command = {function: 'is_legal', parameters: [[x1,y1,z1],[x2,y2,z2]]}
        if (command.function === 'is_legal') {
            try {
                const loc = new Tile(...command.parameters[0])
                const dest = new Tile(...command.parameters[1])
                const legal = CC.is_legal(loc, dest)
                if (legal[0]) {
                    socket.broadcast.to(socket.id).emit('command', `Legal ${legal[1]} move.`)
                } else {
                    socket.broadcast.to(socket.id).emit('command', `Illegal move, ${legal[1]}.`)
                }
                
            } catch (error) {
                socket.broadcast.to(socket.id).emit('command', 'Error, move could not be recognized.')
            }
        }
        //command = {function: 'move', parameters: [[x1,y1,z1],[x2,y2,z2]]}
        if (command.function === 'move') {
            try {
                const loc = new Tile(...command.parameters[0])
                const dest = new Tile(...command.parameters[1])
                const legal = CC.is_legal(loc, dest)
                if (legal[0]) {
                    CC.move(loc, dest)
                    socket.emit('command', `${users[socket.id]} moved ${loc.toString()} to ${dest.toString()}.`)
                    socket.emit('board', CC.to_rect())
                } else {
                    socket.broadcast.to(socket.id).emit('command', `Illegal move, ${legal[1]}.`)
                }
            } catch (error) {
                socket.broadcast.to(socket.id).emit('command', 'Error, move could not be recognized.')
            }
        }
    })
    
})
