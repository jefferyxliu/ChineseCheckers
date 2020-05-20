//const PORT = 3000
const socket = io(`http://localhost:3000`)

const name = prompt('Enter username: ')
socket.emit('new-user', name)

//receiving new connection message
socket.on('user-connected', name => {
    console.log(`${name} joined.`)
    //TO DO: print to HTML chatbox instead
})

//receiving a chat-message
socket.on('chat-message', data => {
    console.log(`${data.name}: ${data.message}`)
    //TO DO: print to HTML textbox instead
})

//sending a chat-message
//TO DO: get message from HTML text form
function send_message(message = 'sample message') {
    socket.emit('send-chat-message', message)
}

//receiving disconnection message
socket.on('user-disconnected', name => {
    console.log(`${name} left.`)
    //TO DO: print to HTML chatbox instead
})

//sending a game command
//TO DO: get command from HTML text form (commands with special character "/")
//send command as object {function: function, parameters: parameters}
//list of commands implemented:
//{function: 'set_up', parameters: [gamemode, [colors0-5](optional colors)]}
//{function: 'reset', parameters: null}
//{function: 'is_legal', parameters: [[x1,y1,z1],[x2,y2,z2]]}
//{function: 'move', parameters: [[x1,y1,z1],[x2,y2,z2]]}
function send_command(command) {
    socket.emit('send-command', command)
}

//receiving a result of command
socket.on('command', data => {
    console.log(`${data.message}`)
    //TO DO: print to HTML textbox instead
})

//receiving a board position of all pieces (a Map of {'color' => [[x1,y1],[x2,y2],...]})
socket.on('board', position => {
    console.log(position)
    //TO DO: display board position on HTML canvas. Remember to multiply y coordinate by sqrt(3) ~1.73
})