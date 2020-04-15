from tkinter import *

#Use this as the client end.
class App(Frame):

    def __init__(self):
        self.root = Tk(className=' Chinese Checkers')

        Frame.__init__(self, self.root)
        self.user_entry_label = Label(self.root, text="Enter a Username:")
        self.user_entry_label.pack(side = LEFT)
        self.user_entry = Entry(self.root)
        self.user_entry.pack(side=RIGHT)
        self.user_entry.bind('<Return>', self.get_username)

    def get_username(self, x = None):
        get = self.user_entry.get()
        if len(get) > 0:
            self.username = get
        else:
            self.username = 'username'
        self.user_entry.destroy()
        self.user_entry_label.destroy()
        #TO DO: Send username to server

        self.create_widgets()

    def create_widgets(self):
        self.board = Canvas(width=400, height=400, bg = 'Gray')
        self.board.pack(side = LEFT)
        self.board.create_text(200,200,text='Board goes here.')

        self.chatframe = Frame(width=40, height=400)
        self.chatframe.pack(side = RIGHT)
        
        self.log = Text(self.chatframe, width=40)
        self.log.pack(side=TOP)
        self.log.config(state=DISABLED)

        self.button = Button(self.chatframe, text="Submit", command=self.callback)
        self.button.pack(side=RIGHT)
        
        self.entry = Entry(self.chatframe)
        self.entry.pack(side=RIGHT)
        self.entry.bind('<Return>', self.callback)

        self.user_label = Label(self.chatframe, text=f'{self.username}:')
        self.user_label.pack(side=RIGHT)

    def callback(self, x = None):
        get = self.entry.get()
        if len(get) > 0:
            if get[0] == '\\':
                cmd = get.split(' ')
                if cmd[0] == '\\move':
                    self.submit_move(cmd[1:])
                else:
                    self.print_log('Command {cmd[0]} not recognized.')
            
            else:
                self.print_log(get)
        


    def print_log(self, text):
        self.log.config(state=NORMAL)
        self.log.insert(END, f'{self.username}: {text}\n')
        self.log.config(state=DISABLED)
        self.entry.delete(0,END)
        #TO DO: Send chat text to server.
    
    def submit_move(self, move):
        '''
        loc = move[0].split(',')
        dest = move[1].split(',')
        loc = [int(x) for x in loc]
        dest = [int(x) for x in dest]
        print(loc,dest)
        '''
        pass
        #TO DO: Send move to the server.

    
        #TO DO: Receive opponent's moves or chat text from server.

    def print_board(self, position):
        #Draw the board position
        pass
    
    
    def start(self):
        self.root.mainloop()

App().start()
