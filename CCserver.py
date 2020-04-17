import ChineseCheckers as CC
import socket
import select
import sys
import pickle


HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

def headerencode(text, mode = 'utf-8'):
    if mode == 'utf-8':
        message = text.encode('utf-8')
    elif mode == 'pickle':
        message = pickle.dumps(text)
    header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
    return header + message

class Server(CC.ChineseCheckers):
    def __init__(self):
        CC.ChineseCheckers.__init__(self)
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((IP, PORT))
        self.server_socket.listen(6)
        
        self.sockets_list = [self.server_socket]
        

        self.clients = {}
        self.start()

    def receive_message(self, client_socket):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)

            if not len(message_header):
                return False

            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}
        except:
            return False

    def send_all(self, encoding):
        for client_socket in self.clients:
            client_socket.send(encoding)

    def start(self):
        while True:
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()

                    user = self.receive_message(client_socket)
                    if user is False:
                        continue

                    self.sockets_list.append(client_socket)
                    self.clients[client_socket] = user

                    print('Accepted new connection from {} {} username:{}'.format(client_address[0],client_address[1],user['data'].decode("utf-8")))

                    self.send_all(headerencode('Chatbot'))
                    self.send_all(headerencode('{} joined.'.format(user['data'].decode('utf-8'))))
                    if self.playing:
                        client_socket.send(headerencode('\\board'))
                        client_socket.send(headerencode(self.to_plane(self.home['red']),'pickle'))
                        print('board sent.')
                    
                else:
                    message = self.receive_message(notified_socket)
                    
                    if message is False:
                        print('Closed connection from {}'.format(self.clients[notified_socket]['data'].decode('utf-8')))
                        self.send_all(headerencode('Chatbot'))
                        self.send_all(headerencode('{} left.'.format(self.clients[notified_socket]['data'].decode('utf-8'))))
                        
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue
                
                    user = self.clients[notified_socket]
                    print('Received message from {}: {}'.format(user['data'].decode('utf-8'), message['data'].decode('utf-8')))

                    msg = message['data'].decode('utf-8')
                    if msg[0] != '\\':
                        self.send_all(user['header'] + user['data'] + message['header'] + message['data']) #Send Chat message to all

                    if msg[0] == '\\':
                        notified_socket.send(user['header'] + user['data']) #Command only visible to user
                        notified_socket.send(headerencode(msg))
                        msg = msg.split(' ')
                        if msg[0] == '\\set_up':
                            try:
                                if int(msg[1]) in (2,3,4,6):
                                    self.set_up(int(msg[1]))
                                    self.send_all(user['header'] + user['data'])
                                    self.send_all(headerencode('started game for {} players.'.format(msg[1])))
                                    self.send_all(headerencode('\\board'))
                                    self.send_all(headerencode(self.to_plane(self.home['red']),'pickle'))
                                    print('board sent.')
                            except:
                                notified_socket.send(headerencode('Chatbot'))
                                notified_socket.send(headerencode('Set up failed!'))

                        elif msg[0] == '\\reset':
                            self.reset()
                            self.send_all(user['header'] + user['data'])
                            self.send_all(headerencode('reset the board.'))
                            self.send_all(headerencode('\\board'))
                            self.send_all(headerencode({}),'pickle')

                        elif msg[0] == '\\is_legal':
                            try:
                                loc = msg[1].split(',')
                                loc = CC.Tile(*[int(x) for x in loc])
                                dest = msg[2].split(',')
                                dest = CC.Tile(*[int(x) for x in dest])

                                test = self.is_legal(loc,dest)
                                if test[0]:
                                    notified_socket.send(headerencode('Chatbot'))
                                    notified_socket.send(headerencode(f'Legal {test[1]} move.'))

                                elif not test[0]:
                                    notified_socket.send(headerencode('Chatbot'))
                                    notified_socket.send(headerencode(f'Illegal move, {test[1]}.'))
                                    

                            except:
                                notified_socket.send(headerencode('Chatbot'))
                                notified_socket.send(headerencode('Move not recognized.'))

                        elif msg[0] == '\\move':
                            try:
                                loc = msg[1].split(',')
                                loc = CC.Tile(*[int(x) for x in loc])
                                dest = msg[2].split(',')
                                dest = CC.Tile(*[int(x) for x in dest])
                                
                                if self.is_legal(loc,dest)[0]:
                                    self.move(loc, dest)
                                    self.send_all(user['header'] + user['data'])
                                    self.send_all(headerencode('moved from {} to {}'.format(loc,dest)))
                                    self.send_all(headerencode('\\board'))
                                    self.send_all(headerencode(self.to_plane(self.home['red']),'pickle'))
                                    print('board sent.')

                                    for color in self.pieces:
                                        if self.has_won(color):
                                            self.send_all(headerencode('Chatbot'))
                                            self.send_all(headerencode('{} has won!'.format(color)))
                                            

                                            
                                    #UPDATE BOARD and SEND!

                            except:
                                notified_socket.send(headerencode('Chatbot'))
                                notified_socket.send(headerencode('Move not recognized.'))
                            
                        else:
                            notified_socket.send(headerencode('Chatbot'))
                            notified_socket.send(headerencode(f'Command {msg[0]} not recognized.'))
                            

                            
                
            for notified_socket in exception_sockets:
                sockets_list.remove(notified_socket)
                del self.clients[notified_socket]
        

    
    
Server()
