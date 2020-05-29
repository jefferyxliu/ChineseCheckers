// Three Classes for the game algorithm; Tile, Tileset, ChineseCheckers
class Tile {
    constructor(x, y, z) {
        //hexagonal coordinate system
        //lattice points of plane x + y + z = 0
        //project z to plane if not on plane
        if (x + y + z != 0) {
            z = - x - y;
        }
        this.x = x;
        this.y = y;
        this.z = z;
    }
    toString() {
        return `${this.x}, ${this.y}, ${this.z}`;
    }
    //vector operations
    equals(that) {
        return (this.x === that.x) && (this.y === that.y);
    }
    add(that) {
        return new Tile(this.x + that.x, this.y + that.y, this.z + that.z);
    }
    sub(that) {
        return new Tile(this.x - that.x, this.y - that.y, this.z - that.z);
    }
    neg() {
        return new Tile(-this.x, -this.y, -this.z);
    }
    //scalar multiplication
    mult(that) {
        return new Tile(this.x * that, this.y * that, -this.z * that);
    }
    //rectilinear distance (adjacent tiles have distance 1)
    dist(that) {
        return (Math.abs(this.x - that.x) + Math.abs(this.y - that.y) + Math.abs(this.z - that.z))/2;
    }
    //hexagonal coordinates to 2D rectangular for board display
    //side (0-5) for all 6 rotation viewpoints
    //yay for linear algebra!
    to_rect(side = 0) {
        const c = [2, 1, -1, -2, -1, 1][side];
        const s = [0, 1, 1, 0, -1, -1][side];
        const x = (c + 3 * s) * this.x + (-c + 3 * s) * this.y;
        const y = (s - c) * this.x + (-s - c) * this.y;
        return [x/2, y/2] //normalized to integers for easy server-client transmission, multiply y coordinate by sqrt(3) = ~1.73 before display.
    }
}

class TileSet {
    constructor(tiles = null) {
        if (tiles === null) {
            tiles = []
        }
        this.map = new Map()
        tiles.forEach(element => {
            this.map.set(element.toString(),element)
        });
    }
    add(tile) {
        this.map.set(tile.toString(), tile);
    }
    values() {
        return this.map.values();
    }
    delete(tile) {
        return this.map.delete(tile.toString());
    }
    update(other) {
        [...other.values()].forEach(element => {
            this.add(element)
        });
    }
    clear() {
        this.map.clear()
    }
    difference(other) {
        return new TileSet([...(this.map.values())].filter(tile => !other.map.has(tile.toString())))
    }
    copy() {
        return new TileSet([...this.map.values()])
    }
    includes(tile) {
        return this.map.has(tile.toString())
    }
}
class ChineseCheckers {
    constructor() {
        //Map of all pieces and tile locations, index 0-5 as key
        this.pieces = new Map()
        //Map of index 0-5 to color
        this.color = new Map()

        //six cardinal directions
        //for getting adjacent tiles
        this.directions = [new Tile(1,0,-1), new Tile(0,1,-1), new Tile(-1,0,1), new Tile(0,-1,1), new Tile(1,-1,0), new Tile(-1,1,0)]
        this.isPlaying = false

    }
    set_up(gamemode = 2, colors = ['red','yellow','green','cyan','blue','magenta']) {
        //gamemode number of players; 2, 3, 4 or 6 for symmetry
        //default color wheel colors
        this.reset()
        for (let index = 0; index < gamemode; index++) {
            const i = Math.floor(index*6/gamemode);
            const color = colors[i];
            let piecearray = [];
            const c = [1,0,0,-1,0,0][i % 6];
            const d = [1,0,0,-1,0,0][(i + 2) % 6];
            const e = [1,0,0,-1,0,0][(i + 4) % 6];
            for (let a = 1; a < 5; a++) {
                for (let b = 5 - a; b < 5; b++) {
                    const x = c * a + d * b + e * (-a - b);
                    const y = e * a + c * b + d * (-a - b);
                    piecearray.push(new Tile(x, y, -x-y));
                }
            }
            this.pieces.set(i, piecearray);
            this.color.set(i, color);
        this.isPlaying = true;
        }
    }
    //calculates home tile from index 0-5.
    home_tile(i) {
        const c = [1,0,0,-1,0,0][i % 6];
        const d = [1,0,0,-1,0,0][(i + 2) % 6];
        const e = [1,0,0,-1,0,0][(i + 4) % 6];
        const x = c * 4 + d * 4 + e * (-8);
        const y = e * 4 + c * 4 + d * (-8);
        return new Tile(x, y, -x-y);
    }
    reset() {
        this.pieces.clear();
        this.color.clear();
        this.isPlaying = false;
    }
    //boundary is intersection of two equilateral triangles
    in_bounds(tile) {
        return (tile.x <= 4 && tile.y <= 4 && tile.z <= 4) || (tile.x >= -4 && tile.y >= -4 && tile.z >= -4);
    }
    occupied_tiles() {
        let occupied = [];
        for (const sidepieces of [...this.pieces.values()]) {
            occupied.push(...sidepieces)
        }
        return occupied;
    }
    is_occupied(tile) {
        return !!this.occupied_tiles().find(element => element.equals(tile));
    }
    is_empty(tile) {
        return !(this.is_occupied(tile));
    }
    move(loc, dest) {
        for (const side of this.pieces.keys()) {
            let tiles = this.pieces.get(side);
            for (let i = 0; i < tiles.length; i++) {
                if (loc.equals(tiles[i])) {
                    tiles[i] = dest;
                    this.pieces.set(side, tiles);
                }
            }
        }
    }
    //find all tile connected by jump move
    connection(tile) {
        let aggr = new TileSet();
        let newtiles = new TileSet([tile]);
        while (newtiles.map.size > 0) {
            aggr.update(newtiles);
            for (const x of newtiles.copy().values()) {
                for (const direction of this.directions) {
                    let jump = x.add(direction.mult(2));
                    //console.log(jump.toString())
                    if (this.is_occupied(x.add(direction)) && this.in_bounds(jump) && this.is_empty(jump)) {
                        newtiles.add(jump);
                        //console.log('added')                      
                    }
                }
            }
            newtiles = newtiles.difference(aggr);
        }
        return aggr;
    }
    //determines if move is legal
    //move must be to adjacent tile, or connected by jump
    is_legal(loc, dest) {
        if (this.is_occupied(loc)) {
            if (this.is_empty(dest) && this.in_bounds(dest)) {
                if (loc.dist(dest) === 1) {
                    return [true, 'step']
                }
                else{
                    if (this.connection(loc).includes(dest) && !loc.equals(dest)) {
                        return [true, 'jump']
                    } else {
                        return [false, 'no path found']
                    }
                }
            } else {
                return [false, 'destination occupied or out of bounds']
            }
        } else {
            return [false, 'no piece to move']
        }
    }
    //win condition
    has_won(side) {
        const home = this.home_tile(side)
        return this.pieces.get(side).every(piece => piece.dist(home) > 12)
    }
    //all pieces mapped to rectangular coordinates
    to_rect(view = 0) {
        let pieces_rect = new Map()
        for (const side of this.pieces.keys()) {
            pieces_rect.set(this.color.get(side), this.pieces.get(side).map(tile => tile.to_rect(view)));
        }
        return Object.fromEntries(pieces_rect.entries())
    }
}

//Socket Server-side Programming
const PORT = 3001;
const io = require('socket.io')(PORT);
let CC = new ChineseCheckers();
//object to track clients
const users = {};

//When a socket connects to the server
io.on('connection', socket => {
    
    console.log(`new connection from ${socket.id}`);
    
    //when username is entered, track name in users, send user-connected message to all clients, update participants box
    socket.on('new-user', name => {
        users[socket.id] = name;
        console.log(`${name} joined.`);
        socket.broadcast.emit('user-connected', name);
        io.sockets.emit('board', CC.to_rect());
        io.sockets.emit('participants', Object.values(users))
    })
    
    //when server receives message, send chat message to all clients
    socket.on('send-chat-message', message => {
        console.log(`message from ${users[socket.id]}: ${message}`);
        socket.broadcast.emit('chat-message', {message: message, name: users[socket.id]});
    })
    
    //when client disconnects, send user-disconnect message to all clients, update participants box
    socket.on('disconnect', () => {
        socket.broadcast.emit('user-disconnected', users[socket.id]);
        console.log(`${users[socket.id]} left.`);
        delete users[socket.id];
        io.sockets.emit('participants', Object.values(users))
    })

    //when server receives command
    //command: 'set_up'
    //parameters: [gamemode, [colors0-5]]
    socket.on('set_up', parameters => {
        try {
            CC.set_up(...parameters);
            io.sockets.emit('command', `${users[socket.id]} set up a game for ${parameters[0]} people.`);
            io.sockets.emit('board', CC.to_rect());
            console.log(`${users[socket.id]} set up a game for ${parameters[0]} people.`);
        } catch (error) {
            socket.emit('command', 'Error: set up failed.');
            console.log('error1');
        }
    })

    //command: 'reset'
    socket.on('reset', () => {
        CC.reset();
        io.sockets.emit('command', `${users[socket.id]} reset the board.`);
        io.sockets.emit('board', CC.to_rect());
        console.log(`${users[socket.id]} reset the board.`);
    })

    //command: 'is_legal'
    //parameters: [[x1,y1,z1],[x2,y2,z2]]
    socket.on('is_legal', parameters => {
        try {
            const loc = new Tile(...parameters[0]);
            const dest = new Tile(...parameters[1]);
            const legal = CC.is_legal(loc, dest);
            if (legal[0]) {
                socket.emit('command', `Legal ${legal[1]} move.`);
                console.log(`Legal ${legal[1]} move.`)
            } else {
                socket.emit('command', `Illegal move, ${legal[1]}.`);
                console.log(`Illegal move, ${legal[1]}.`);
            }
            
        } catch (error) {
            socket.emit('command', 'Error, move could not be recognized.');
            console.log('error2');
        }
    })

    //command: 'move'
    //parameters: [[x1,y1,z1],[x2,y2,z2]]
    socket.on('move', parameters => {
        try {
            const loc = new Tile(...parameters[0]);
            const dest = new Tile(...parameters[1]);
            const legal = CC.is_legal(loc, dest);
            if (legal[0]) {
                CC.move(loc, dest);
                io.sockets.emit('command', `${users[socket.id]} moved ${loc.toString()} to ${dest.toString()}.`);
                io.sockets.emit('board', CC.to_rect());
                console.log(`${users[socket.id]} moved ${loc.toString()} to ${dest.toString()}.`)
            } else {
                socket.emit('command', `Illegal move, ${legal[1]}.`);
                console.log(`Illegal move, ${legal[1]}.`);
            }
        } catch (error) {
            socket.emit('command', 'Error, move could not be recognized.');
            console.log('error3');
        }
    })
})
