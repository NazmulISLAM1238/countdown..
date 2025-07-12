import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
import time
import threading
from datetime import datetime, timedelta

class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("COUNTDOWN TIMER")
        self.root.geometry("450x450")
        self.root.resizable(False, False)
        self.root.configure(bg="white")

        self.total_seconds = 0
        self.is_running = False
        self.stop_flag = False
        self.mode = "time"  # "time" or "day"

        self.time_left = tk.StringVar(value="00:00:00")
        self.timer_name = tk.StringVar(value="COUNTDOWN TIMER")
        self.user_timer_name = tk.StringVar(value="")
        self.status_message = tk.StringVar(value="")

        # Heading Label (constant)
        self.name_label = tk.Label(root, textvariable=self.timer_name, font=("Arima koshi", 40, "bold"), fg="black", bg="white")
        self.name_label.pack(pady=(10, 0))

        # Timer name below heading
        self.user_name_label = tk.Label(root, textvariable=self.user_timer_name, font=("Arial", 26, "italic"), fg="gray20", bg="white")
        self.user_name_label.pack(pady=(0, 10))

        # Time Display Label
        self.time_label = tk.Label(root, textvariable=self.time_left, font=("Arial", 20), fg="orange", bg="white")
        self.time_label.pack(pady=10)

        # Status message label
        self.status_label = tk.Label(root, textvariable=self.status_message, font=("Arial", 14), fg="green", bg="white")
        self.status_label.pack(pady=(0, 10))

        # Timer Name Entry
        self.name_entry = tk.Entry(root, font=("Arial", 17), justify="center", fg="white", bd=0, bg="#00AAFF")
        self.name_entry.insert(0, "Input timer name")
        self.name_entry.pack(pady=5)
        self.name_entry.bind("<FocusIn>", self.clear_name_placeholder)
        self.name_entry.bind("<FocusOut>", self.restore_name_placeholder)

        # Time Entry (only for time mode)
        self.time_entry = tk.Entry(root, font=("Arial", 17), justify="center", fg="white", bd=0, bg="#00AAFF")
        self.time_entry.insert(0, "HH:MM:SS")
        self.time_entry.pack(pady=5)
        self.time_entry.bind("<FocusIn>", self.clear_time_placeholder)
        self.time_entry.bind("<FocusOut>", self.restore_time_placeholder)

        # Buttons Frame
        btn_frame = tk.Frame(root, bg="white", bd=0)
        btn_frame.pack(pady=10)

        # Start/Stop Button
        self.start_stop_button = tk.Button(btn_frame, text="Start", font=("Arial", 14), command=self.start_stop_timer, bd=0, bg="#00AAFF", width=10)
        self.start_stop_button.grid(row=0, column=0, padx=5)

        # Reset Button
        self.reset_button = tk.Button(btn_frame, text="Reset", font=("Arial", 14), command=self.reset_timer, bd=0, bg="#00AAFF", width=10)
        self.reset_button.grid(row=0, column=1, padx=5)

        # Day Mode Button
        self.day_button = tk.Button(btn_frame, text="Day", font=("Arial", 14), command=self.open_calendar, bd=0, bg="#00AAFF", width=10)
        self.day_button.grid(row=0, column=2, padx=5)

        # Calendar popup window (initialized None)
        self.cal_window = None
        self.selected_date = None

    # Placeholder handlers
    def clear_name_placeholder(self, event):
        if self.name_entry.get() == "Input timer name":
            self.name_entry.delete(0, tk.END)
            self.name_entry.config(fg="white")

    def restore_name_placeholder(self, event):
        if not self.name_entry.get():
            self.name_entry.insert(0, "Input timer name")
            self.name_entry.config(fg="white")

    def clear_time_placeholder(self, event):
        if self.time_entry.get() == "HH:MM:SS":
            self.time_entry.delete(0, tk.END)
            self.time_entry.config(fg="white")

    def restore_time_placeholder(self, event):
        if not self.time_entry.get():
            self.time_entry.insert(0, "HH:MM:SS")
            self.time_entry.config(fg="white")

    # Set time countdown mode
    def set_time(self):
        time_input = self.time_entry.get().strip()
        name_input = self.name_entry.get().strip()

        try:
            h, m, s = map(int, time_input.split(':'))
            if h < 0 or m < 0 or s < 0 or m >= 60 or s >= 60:
                raise ValueError
            self.total_seconds = h * 3600 + m * 60 + s
            if self.total_seconds == 0:
                raise ValueError
            self.update_display(self.total_seconds)
            self.status_message.set("")
            self.is_running = False
            self.stop_flag = False
        except Exception:
            messagebox.showerror("Input Error", "Please enter a valid time in HH:MM:SS format (e.g., 01:30:00)")
            return False

        # Set timer name below heading
        if name_input and name_input != "Input timer name":
            self.user_timer_name.set(name_input)
        else:
            self.user_timer_name.set("")

        return True

    # Set day countdown mode
    def set_day(self, target_date):
        now = datetime.now()
        if target_date <= now:
            messagebox.showerror("Date Error", "Please select a future date.")
            return False

        delta = target_date - now
        self.total_seconds = int(delta.total_seconds())
        self.status_message.set("")
        self.is_running = False
        self.stop_flag = False

        # Set timer name below heading
        name_input = self.name_entry.get().strip()
        if name_input and name_input != "Input timer name":
            self.user_timer_name.set(name_input)
        else:
            self.user_timer_name.set("")

        self.update_display_day(self.total_seconds)
        return True

    # Update display for time mode (HH:MM:SS)
    def update_display(self, seconds):
        hrs, rem = divmod(seconds, 3600)
        mins, secs = divmod(rem, 60)
        self.time_left.set(f"{hrs:02d}:{mins:02d}:{secs:02d}")

    # Update display for day mode (human readable)
    def update_display_day(self, seconds):
        days, rem = divmod(seconds, 86400)
        hrs, rem = divmod(rem, 3600)
        mins, secs = divmod(rem, 60)
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hrs > 0:
            parts.append(f"{hrs} hour{'s' if hrs != 1 else ''}")
        if mins > 0:
            parts.append(f"{mins} minute{'s' if mins != 1 else ''}")
        parts.append(f"{secs} second{'s' if secs != 1 else ''}")
        self.time_left.set(", ".join(parts))

    # Countdown thread for time mode
    def countdown_time(self):
        while self.total_seconds > 0 and self.is_running:
            self.update_display(self.total_seconds)
            self.root.update()
            time.sleep(1)
            if not self.is_running:
                break
            self.total_seconds -= 1

        if self.total_seconds == 0 and self.is_running:
            self.time_left.set("00:00:00")
            self.status_message.set("Successfully completed")
            messagebox.showinfo("Timer Finished", "Successfully completed")
            self.is_running = False
            self.stop_flag = False
            self.start_stop_button.config(text="Start", state="normal")

    # Countdown thread for day mode
    def countdown_day(self):
        while self.total_seconds > 0 and self.is_running:
            self.update_display_day(self.total_seconds)
            self.root.update()
            time.sleep(1)
            if not self.is_running:
                break
            self.total_seconds -= 1

        if self.total_seconds == 0 and self.is_running:
            self.update_display_day(0)
            self.status_message.set("Successfully completed")
            messagebox.showinfo("Timer Finished", "Successfully completed")
            self.is_running = False
            self.stop_flag = False
            self.start_stop_button.config(text="Start", state="normal")

    # Start/Stop toggle
    def start_stop_timer(self):
        if not self.is_running:
            # Start timer
            if not self.stop_flag:  # fresh start or after reset
                if self.mode == "time":
                    if not self.set_time():
                        return
                else:
                    # day mode requires selected_date set
                    if not self.selected_date:
                        messagebox.showerror("Error", "Please select a date first by clicking 'Day' button.")
                        return
                    if not self.set_day(self.selected_date):
                        return

            self.is_running = True
            self.stop_flag = True
            self.start_stop_button.config(text="Stop")

            if self.mode == "time":
                threading.Thread(target=self.countdown_time, daemon=True).start()
            else:
                threading.Thread(target=self.countdown_day, daemon=True).start()
        else:
            # Stop timer
            self.is_running = False
            self.start_stop_button.config(text="Start")

    # Reset timer
    def reset_timer(self):
        self.is_running = False
        self.stop_flag = False
        self.start_stop_button.config(text="Start", state="normal")
        self.status_message.set("")
        self.total_seconds = 0
        self.user_timer_name.set("")
        self.selected_date = None

        if self.mode == "time":
            self.update_display(0)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, "Input timer name")
            self.name_entry.config(fg="white")
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, "HH:MM:SS")
            self.time_entry.config(fg="white")
            self.time_entry.pack(pady=5)
        else:
            self.update_display_day(0)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, "Input timer name")
            self.name_entry.config(fg="white")
            self.time_entry.pack_forget()

    # Open calendar popup for day selection
    def open_calendar(self):
        if self.cal_window and tk.Toplevel.winfo_exists(self.cal_window):
            self.cal_window.lift()
            return

        self.mode = "day"
        self.time_entry.pack_forget()  # hide time entry in day mode

        self.cal_window = tk.Toplevel(self.root)
        self.cal_window.title("Select Date")
        self.cal_window.geometry("300x300")
        self.cal_window.resizable(False, False)

        cal = Calendar(self.cal_window, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=20)

        def on_date_select():
            date_str = cal.get_date()
            try:
                selected = datetime.strptime(date_str, "%Y-%m-%d")
                self.selected_date = selected.replace(hour=0, minute=0, second=0,) + timedelta(days=1)  # midnight next day
                if self.selected_date <= datetime.now():
                    messagebox.showerror("Date Error", "Please select a future date.")
                    return
                self.set_day(self.selected_date)
                self.cal_window.destroy()
            except Exception as e:
                messagebox.showerror("Date Error", f"Invalid date selected: {e}")

        select_btn = tk.Button(self.cal_window, text="Select", command=on_date_select, bg="white", fg="black", font=("Arial", 12), bd=0)
        select_btn.pack(pady=10)

    def switch_to_time_mode(self, event=None):
        if self.mode != "time":
            self.mode = "time"
            self.selected_date = None
            self.time_entry.pack(pady=5)
            self.update_display(0)
            self.user_timer_name.set("")
            self.status_message.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownTimer(root)
    root.mainloop()