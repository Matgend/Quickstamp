import customtkinter as ctk
from .components import TableFrame, EntryBarre, Message, Stamp, Outputs

class Stamp_Interface(ctk.CTk):
    def __init__(self, master = None):
        super().__init__()
        
        self.title('Quickstamp')
        self.geometry('900x1000')
        self.grid_columnconfigure(0, weight = 1)
        self.configure(fg_color = '#F9F7F7')

        #Components
        self.table = TableFrame(self)
        self.entry_barre = EntryBarre(self) 
        self.message = Message(self)
        self.stamp_button = Stamp(self)
        self.reports = Outputs(self)

        #Check stamps previous day
        self.check_daily_stamps()

    def check_daily_stamps(self):
        '''Check stamps previous day'''
        from controller.logic import daily_stamp_check
        complete, date = daily_stamp_check()

        if date and not complete:
            self.message.show_message(f'One timestamps is missing for the {date}', 'warning'
            )