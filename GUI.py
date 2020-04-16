from tkinter import *
import socket
import sys
import errno
import threading

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234


def headerencode(text):
    message = text.encode('utf-8')
    header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
    return header + message

#Use this as the client end.
class App(Frame):

    def __init__(self):
        self.root = Tk(className=' Chinese Checkers')
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))
        
        
        Frame.__init__(self, self.root)
        self.user_entry_label = Label(self.root, text="Enter a Username:")
        self.user_entry_label.pack(side = LEFT)
        self.user_entry = Entry(self.root)
        self.user_entry.pack(side=RIGHT)
        self.user_entry.bind('<Return>', self.get_username)

        self.root.update_idletasks()
        self.root.update()

    def exit(self):
        self.root.destroy()
        sys.exit()

    def get_username(self, x = None):
        get = self.user_entry.get()
        if len(get) > 0:
            self.username = get
        else:
            self.username = 'username'
        self.user_entry.destroy()
        self.user_entry_label.destroy()

        #TO DO: Send username to server
        self.client_socket.send(headerencode(self.username))

        
        self.create_widgets()
        self.start()

    def create_widgets(self):
        self.board = Canvas(width=400, height=400, bg = 'Gray')
        self.board.pack(side = LEFT)
        self.board.create_text(200,200,text='Board goes here.')

        self.chatframe = Frame(width=40, height=400)
        self.chatframe.pack(side = RIGHT)

        scroll = Scrollbar(self.chatframe)
        self.log = Text(self.chatframe, width=40, height=40, yscrollcommand=scroll.set)
        
        self.log.pack(side=TOP)
        self.log.config(state=DISABLED)

        self.button = Button(self.chatframe, text="Return", command=self.callback)
        self.button.pack(side=RIGHT)
        
        self.entry = Entry(self.chatframe)
        self.entry.pack(side=RIGHT)
        self.entry.bind('<Return>', self.callback)

        self.user_label = Label(self.chatframe, text=f'{self.username}:')
        self.user_label.pack(side=RIGHT)

    def callback(self, x = None):
        get = self.entry.get()
        self.entry.delete(0,END)
        #self.print_log(self.username, get)
        if len(get) > 0:
            #TO DO: Send text to server.
            self.client_socket.send(headerencode(get))
        

    def print_log(self, user, text):
        self.log.config(state=NORMAL)
        if user == 'Chatbot':
            self.log.insert(END, f'{text}\n')
        else:
            self.log.insert(END, f'{user}: {text}\n')
        self.log.config(state=DISABLED)
        
        
    
    def submit_move(self, move):
        
        #Update Board Position
        '''
        loc = move[0].split(',')
        dest = move[1].split(',')
        loc = [int(x) for x in loc]
        dest = [int(x) for x in dest]
        print(loc,dest)
        '''
        pass
        

    
        

    def print_board(self, position):
        #Draw the board position
        pass
    
    def headerdecode(self, header = HEADER_LENGTH):
        username_header = self.client_socket.recv(header)
        if not len(username_header):
            print('connection closed by the server')
            sys.exit()
        username_length = int(username_header.decode('utf-8').strip())
        username = self.client_socket.recv(username_length).decode('utf-8')
        message_header = self.client_socket.recv(header)
        message_length = int(message_header.decode('utf-8').strip())
        message = self.client_socket.recv(message_length).decode('utf-8')
        print(message)
        return username, message
        
    def start(self):
        threading.Thread(target = self.receive).start()
        self.root.mainloop()
        
    def receive(self):

        while True:
            
            try:
                username, message = self.headerdecode()
                

                if len(message) > 0:
                    self.print_log(username, message)
                
                
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error', str(e))
                    sys.exit()
                continue
    
            except Exception as e:
                print('General error', str(e))
                sys.exit() 

App()
