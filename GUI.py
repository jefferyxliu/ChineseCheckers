from tkinter import *



class App(Frame):

    def __init__(self):
        self.root = Tk()

        Frame.__init__(self, self.root)
        self.create_widgets()

    def create_widgets(self):
        frame = Frame(width=32, height=576)
        frame.pack()
        
        self.log = Text(frame, width=32)
        self.log.pack(side=TOP)
        self.log.config(state=DISABLED)
        
        
        self.button = Button(frame, text="Submit", command=self.callback)
        self.button.pack(side=RIGHT)
        
        self.entry = Entry(frame)
        self.entry.pack(side=RIGHT)
        self.entry.bind('<Return>', self.callback)

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
        self.log.insert(END, f'{text}\n')
        self.log.config(state=DISABLED)
        self.entry.delete(0,END)
    
    def submit_move(self, move):
        '''
        loc = move[0].split(',')
        dest = move[1].split(',')
        loc = [int(x) for x in loc]
        dest = [int(x) for x in dest]
        print(loc,dest)
        '''
        pass
        
    def start(self):
        self.root.mainloop()

App().start()
