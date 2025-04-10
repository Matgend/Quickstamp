import customtkinter as ctk
from gui.user_page import UserApp
from gui.stamp_page import Stamp_Interface
from controller.logic import is_first_launch, init_app_state

if __name__ == '__main__':

    ctk.set_appearance_mode('light')
    ctk.set_default_color_theme('blue')

    init_app_state()

    if is_first_launch():
        app = UserApp()
            
    else:
        app = Stamp_Interface()

    app.mainloop()
    

