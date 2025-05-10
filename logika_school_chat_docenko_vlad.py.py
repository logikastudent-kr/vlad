import threading
from socket import *
from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.label = None
        # menu frame
        self.menu_frame = CTkFrame(self, width=30, height=300, fg_color="#95FA8C")
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -5
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30, fg_color="#41613E")
        self.btn.place(x=0, y=0)
        # main
        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disabled')
        self.chat_field.place(x=0, y=0)
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)
        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message, fg_color="#41613E")
        self.send_button.place(x=0, y=0)

        self.username = 'Невідомий'
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('26.37.53.140', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        self.adaptive_ui()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
            self.clear_menu_widgets()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()
            # setting menu widgets
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=10)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack(pady=5)
            self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name, fg_color="#41613E")
            self.save_button.pack(pady=5)

        
            self.theme_option = CTkOptionMenu(self.menu_frame, values=["Світла", "Темна"], command=self.change_theme, fg_color="#41613E")
            self.theme_option.pack(pady=20 )
            self.theme_option.set("Світла")  

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if (self.is_show_menu and self.menu_frame.winfo_width() < 200) or (not self.is_show_menu and self.menu_frame.winfo_width() > 30):
            self.after(10, self.show_menu)

    def clear_menu_widgets(self):
        if self.label:
            self.label.destroy()
            self.label = None
        if self.entry:
            self.entry.destroy()
            self.entry = None
        if self.save_button:
            self.save_button.destroy()
            self.save_button = None
        if self.theme_option:
            self.theme_option.destroy()
            self.theme_option = None

    def save_name(self):
        if self.entry:
            new_name = self.entry.get().strip()
            if new_name:
                self.username = new_name
                self.add_message(f"Ваш новий нік: {self.username}", my_message=True)

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        menu_width = self.menu_frame.winfo_width()

        self.chat_field.place(x=menu_width, y=0)
        self.chat_field.configure(width=self.winfo_width() - menu_width, height=self.winfo_height() - 40)

        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=menu_width, y=self.send_button.winfo_y())
        self.message_entry.configure(width=self.winfo_width() - menu_width - 50)

        self.after(50, self.adaptive_ui)

    def add_message(self, text, my_message=False):
        self.chat_field.configure(state='normal')
        if my_message:
            self.chat_field.insert(END, 'Я: ' + text + '\n')
        else:
            self.chat_field.insert(END, text + '\n')
        self.chat_field.configure(state='disabled')
        self.chat_field.see(END)  # автоскрол вниз

    def change_theme(self, value):
        if value == 'Темна':
            set_appearance_mode('dark')
            self.menu_frame.configure(fg_color='#2B2B2B')
        else:
            set_appearance_mode('light')
            self.menu_frame.configure(fg_color='#95FA8C')

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}", my_message=True)
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except Exception as e:
                self.add_message(f"Помилка надсилання: {e}")
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]
                self.add_message(f"{author} надіслав(ла) зображення: {filename}")
        else:
            self.add_message(line)


if __name__ == '__main__':
    win = MainWindow()
    win.mainloop()