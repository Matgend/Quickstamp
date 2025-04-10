#gui/components.py
from tkinter import *
import customtkinter as ctk
from CTkTable import *
from .theme import *
from PIL import Image, ImageTk
from datetime import date, datetime
from controller.logic import delete_timestamp, fetch_companies, last_status, last_id, get_last_10_entries

class DropdownButton(ctk.CTkComboBox):
    def __init__(self, master, values):
        self.all_values = values
        self.current_input = ctk.StringVar()
        self.current_input.trace_add('write', self.filter_values)

        super().__init__(master, 
                        values = values,
                        width = 100,
                        state = 'normal',
                        button_hover_color	= SECONDARY_COLOR,
                        button_color = SECONDARY_COLOR, 
                        variable = self.current_input)
        
        # Bind event to open dropdown when typing
        self.bind("<KeyRelease>", self.on_key_release)

    def filter_values(self, *args):
        '''Filter dropdown values dynamically'''
        input_text = self.current_input.get().lower()

        # Filter values
        filtered_values = [item for item in self.all_values if item.lower().startswith(input_text)] if input_text else self.all_values

        # Update the dropdown list
        self.configure(values = filtered_values)

        # Manually reopen dropdown if matches exist
        if filtered_values:
            self.after(100, lambda: self.event_generate("<Down>"))

    def on_key_release(self, event):
        '''Reopen dropdown when typing.'''
        self.event_generate("<Down>")

class TableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master,
                        fg_color = 'transparent')
        self.grid(row = 0, column = 0, pady = 20) 

        # Add sample data
        self.data = get_last_10_entries()

        len_entries = len(self.data)
        self.title = f'The stamps list'

        # Create a table with CTkTable
        self.header = ['ID', 'Status', 'Time', 'Date', 'Company']

        if len_entries > 0:
            self.title = f'The last {len_entries} stamps'
            self.data.insert(0, self.header)

        # Title Label
        ctk.CTkLabel(self, text = self.title, font = FONT_TITLE, text_color = PRIMARY_COLOR).grid(row = 0, pady = 20, sticky = 'ns')

        #Table 
        CTkTable(self, values = self.data, header_color = SECONDARY_COLOR, text_color = PRIMARY_COLOR).grid(row = 2, sticky = 'ns')


    def refresh_data(self):
        '''Refresh the data in the table'''

        self.destroy_all_widgets()
        
        # Title Label
        ctk.CTkLabel(self, text = self.title, font = FONT_TITLE, text_color = PRIMARY_COLOR).grid(row = 0, pady = 20, sticky = 'ns')

        # Updated data
        self.data = get_last_10_entries()

        if len(self.data) > 0:
            self.data.insert(0, self.header)
            CTkTable(self, values = self.data, header_color = SECONDARY_COLOR, text_color = PRIMARY_COLOR).grid(row = 2, sticky = 'ns')
            
        self.master.entry_barre.update_entries()

        # Refresh button
        add_refresh_image = ImageTk.PhotoImage(Image.open('images/refresh.png').resize((40, 30), Image.Resampling.LANCZOS))

        ctk.CTkButton(self,
                      text = '',
                      image = add_refresh_image,
                      command = self.refresh_data,
                      fg_color = 'transparent',
                      hover = False).grid(row = 1, sticky = 'e')

    def destroy_all_widgets(self):
        '''Delete all the widgets'''
        for widget in self.winfo_children():
            widget.destroy()

class EntryBarre(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, 
                         fg_color = 'transparent')
        self.grid(row = 1, column = 0, pady = 20) 
        self.entries = []

        companies = fetch_companies()
        fields = ['ID', 'Status', 'Time', 'Date', 'Company']

        for i, field in enumerate(fields):
            ctk.CTkLabel(self, text = field, font = FONT_BOLD, text_color = PRIMARY_COLOR).grid(row = 0, column = i, padx = 20, sticky = 'w')

            if field == 'ID':
                entry = ctk.CTkEntry(self, width = 100, placeholder_text = last_id()[0], placeholder_text_color = PRIMARY_COLOR)

            elif field == 'Status':
                val = ['in', 'out']
                entry = DropdownButton(self, values = val)
                last_val = last_status()
                val_index = 1 - val.index(last_val)
                entry.set(val[val_index])

            elif field == 'Company':
                entry = DropdownButton(self, values = companies)
                
                if companies:
                    entry.set(companies[0])


            elif field == 'Time':
                entry = ctk.CTkEntry(self, width = 100, placeholder_text = datetime.now().strftime("%H:%M:%S"), placeholder_text_color = PRIMARY_COLOR)
            
            else:
                entry = ctk.CTkEntry(self, width = 100, placeholder_text = date.today().strftime("%d/%m/%Y"), placeholder_text_color = PRIMARY_COLOR)

            entry.grid(row = 1, column = i, padx = 20)
            self.entries.append(entry)


        #Delete Button
        self.Delete = ctk.CTkButton(self,
                                    width = 100, 
                                    text = 'Delete', 
                                    font = FONT_BOLD, 
                                    fg_color = '#FF0000', 
                                    hover_color = '#f94449',
                                    command = self.delete_timestamp_GUI).grid(row = 1, column = 5, padx = 20)
        
        
    def delete_timestamp_GUI(self):
        '''Delete a timestamp in the db according to the ID'''
        try:
            timestamps_id = self.entries[0].get().strip()
            if not timestamps_id:
                self.master.message.show_message('Insert a valid ID', 'error')
                return
            
            success, message = delete_timestamp(timestamps_id)

            if success:
                self.master.message.show_message(message, 'success')
                #refresh table
                self.master.table.refresh_data()
            else:
                self.master.message.show_message(message, "error")
                
        except Exception as e:
            self.master.message.show_message(f"Erreur: {str(e)}", "error")

    def update_entries(self):
        '''Update entries with latest values'''
        #update ID
        self.entries[0].configure(placeholder_text = last_id()[0])

        #update status
        val = ['in','out']
        last_val = last_status()
        val_index = 1 - val.index(last_val)
        self.entries[1].set(val[val_index])

        #update time
        self.entries[2].configure(placeholder_text = datetime.now().strftime('%H:%M:%S'))

        #update date
        self.entries[3].configure(placeholder_text = date.today().strftime('%d/%m/%Y'))

        #update company
        self.entries[4].set(fetch_companies()[0])


        

class Message(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, 
                         fg_color = 'transparent')
        self.grid(row = 2, sticky = 'ns') 

        # Message Textbox
        self.message_box = ctk.CTkTextbox(self, height = 50, width = 700, fg_color = "transparent", text_color = PRIMARY_COLOR)
        self.message_box.grid(row = 0, sticky = 'ns')
        self.message_box._textbox.tag_configure('text', justify = 'center')
        self.message_box._textbox.tag_configure('success', foreground = SUCCESS_COLOR, justify = 'center')
        self.message_box._textbox.tag_configure('error', foreground = ERROR_COLOR, justify = 'center')
        self.message_box._textbox.tag_configure('warning', foreground = WARNING_COLOR, justify = 'center')

    def show_message(self, message, message_type = 'text'):
        '''Display text in the message zone'''
        self.message_box.delete('0.0', 'end')
        self.message_box.insert('0.0', message)
        self.message_box._textbox.tag_add(message_type, '0.0', 'end')


class Stamp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, 
                         fg_color = 'transparent')
        self.grid(row = 3, sticky = 'ns') 
        self.stamp = ctk.CTkButton(self, width = 150, text = 'Stamp', fg_color = PRIMARY_COLOR, hover_color = '#1b487d', text_color = TEXT_COLOR, font = FONT_BOLD, command = self.stamp_time)
        self.stamp.grid(row = 0, sticky = 'ns')

    def stamp_time(self):
        '''Save a new timestamp'''
        from controller.logic import create_timestamps

        try:
            status = self.master.entry_barre.entries[1].get() or None
            time = self.master.entry_barre.entries[2].get() or None
            date = self.master.entry_barre.entries[3].get() or None
            company = self.master.entry_barre.entries[4].get() or None

            success, message = create_timestamps(status, company, time, date)

            if success:
                self.master.message.show_message(message, 'success')
                self.master.table.refresh_data()
            else:
                self.master.message.show_message(message, 'error')
                
        except Exception as e:
            self.master.message.show_message(f'Error: {str(e)}', 'error')


class Outputs(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, 
                         fg_color = 'transparent')
        self.grid(row = 4, sticky = 'ns', pady = 20)
        
        buttons = ['Weekly report', 'Monthly report', 'Dashboard']

        for i, field in enumerate(buttons):
            ctk.CTkButton(self,
            text = field, 
            fg_color = TEXT_COLOR, 
            font = FONT_BOLD, 
            border_width = 2, 
            border_color = SECONDARY_COLOR, 
            text_color = PRIMARY_COLOR, 
            hover_color = SECONDARY_COLOR,
            command = lambda f = field: self.open_report(f)).grid(row = 0, column = i, sticky = 'ns', padx = 20)

    def open_report(self, report_type):
        '''Open the window of the corresponding report'''
        # Pour l'instant, on affiche juste un message
        self.master.message.show_message(f'The {report_type} is loading', 'warning')



#USER PAGE
class InputFrame(ctk.CTkFrame):
    '''Frame with two entry fields for user input.'''
    def __init__(self, master):
        super().__init__(master, 
                         fg_color = 'transparent')
        self.place(relx = 0.5, rely = 0.5, anchor = 'center')

        text = ['First name', 'Last name']
        text_help = ['Enter your first name', 'Enter your last name']

        self.entries = []
        for i, field in enumerate(text):
            ctk.CTkLabel(self, text = field, font = FONT_BOLD, text_color = PRIMARY_COLOR).grid(row = 0, column = i, padx = 10, pady = 0, sticky = 'w')
            entry = ctk.CTkEntry(self, placeholder_text = text_help[i])
            entry.grid(row = 1, column = i, padx = 10, pady = 0)
            self.entries.append(entry)


class TextFrame(ctk.CTkFrame):
    '''Frame containing a centered title and paragraph'''
    def __init__(self, master, title, paragraph):
        super().__init__(master, 
                         fg_color = 'transparent')
        self.place(relx = 0.5, rely = 0.5, anchor = 's', y = -40)

        # Title Label
        ctk.CTkLabel(self, text = title, font = FONT_TITLE, text_color = PRIMARY_COLOR).grid(row = 0, column = 0, sticky = "n")

        # Paragraph Label
        ctk.CTkLabel(self, text = paragraph, font = FONT_BOLD, text_color = PRIMARY_COLOR, wraplength = 600).grid(row = 1, column = 0, sticky = "n")


class WorkFrame(ctk.CTkFrame):
    '''Frame with the working load entry fields'''
    def __init__(self, master):
        super().__init__(master, 
                         fg_color = 'transparent')
        self.place(relx = 0.5, rely = 0.5, anchor = 'center', y = 60)

        text = 'Weekly working load [hours]'
        text_help = '41.5'

        ctk.CTkLabel(self, text = text, font = FONT_BOLD, text_color = PRIMARY_COLOR).grid(row = 0, column = 0, padx = 10, pady = 0, sticky = 'w')
        self.entry = ctk.CTkEntry(self, placeholder_text = text_help)
        self.entry.grid(row = 1, column = 0, padx = 10, pady = 0)

