import customtkinter as ctk
from .theme import *
from .components import TextFrame, InputFrame, WorkFrame
from controller.logic import register_user

class UserApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        #Setting window
        self.title('Quickstamp')
        self.geometry('900x500')
        self.grid_rowconfigure(0, weight = 0)
        self.grid_columnconfigure(0, weight = 1)
        self.configure(fg_color = '#F9F7F7')

        #Components
        self.text_frame = TextFrame(self, "Welcome to QuickStamp!", "Please provide your last name, your first name and your weekly working load in hours to continue.")
        self.name = InputFrame(self)
        self.working_load = WorkFrame(self)

        #Error message
        self.error_label = ctk.CTkLabel(
            self, 
            text = '', 
            font = FONT_BOLD, 
            text_color = ERROR_COLOR,
            wraplength = 500
        )
        self.error_label.place(relx = 0.5, rely = 0.5, anchor = 'n', y = 120)
        self.error_label.configure(text_color = ERROR_COLOR)


        self.button = ctk.CTkButton(self, text = 'Continue', font = FONT_BOLD, fg_color = PRIMARY_COLOR, command = self.save_user_data)
        self.button.place(relx = 0.5, rely = 0.5, anchor = 'n', y = 100)

    def save_user_data(self):
        '''Save user data and pass to the stamp page'''
        first_name = self.name.entries[0].get().strip()
        last_name = self.name.entries[1].get().strip()
        weekly_hours = self.working_load.entry.get().strip()
        
        success, errors = register_user(first_name, last_name, weekly_hours)
        
        if success:
            self.destroy()
            from .stamp_page import Stamp_Interface
            stamp_app = Stamp_Interface()
            stamp_app.mainloop()

        else:
            # Afficher les erreurs
            error_text = "\n".join(errors)
            self.error_label.configure(text=error_text)
