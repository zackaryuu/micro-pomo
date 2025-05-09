import tkinter as tk
import random
import time
import winsound
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class ReminderWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Micro Pomo Reminder")
        
        # Initialize state variables
        self.is_paused = False
        self.is_muted = True  # Set muted to True by default
        self.original_volume = None
        
        # Set window size and position
        window_size = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_size) // 2
        y = (screen_height - window_size) // 2
        self.root.geometry(f"{window_size}x{window_size}+{x}+{y}")
        
        # Create label for question mark
        self.label = tk.Label(
            self.root,
            text="?",
            font=("Arial", 120, "bold"),
            bg="white"
        )
        self.label.pack(expand=True, fill="both")
        
        # Create context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Pause", command=self.toggle_pause)
        self.context_menu.add_command(label="Unmute Other Sounds", command=self.toggle_mute)  # Updated label to match initial state
        
        # Bind right-click to show context menu
        self.label.bind("<Button-3>", self.show_context_menu)
        
        # Schedule the first reminder
        self.schedule_next_reminder()
    
    def show_context_menu(self, event):
        """Show the context menu on right-click"""
        self.context_menu.post(event.x_root, event.y_root)
    
    def toggle_pause(self):
        """Toggle pause/resume state"""
        self.is_paused = not self.is_paused
        self.context_menu.entryconfig(0, label="Resume" if self.is_paused else "Pause")
    
    def toggle_mute(self):
        """Toggle mute state for other sounds"""
        self.is_muted = not self.is_muted
        self.context_menu.entryconfig(1, label="Unmute Other Sounds" if self.is_muted else "Mute Other Sounds")
    
    def set_system_volume(self, volume):
        """Set system volume (0.0 to 1.0)"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            volume_interface.SetMasterVolumeLevelScalar(volume, None)
        except Exception as e:
            print(f"Error setting volume: {e}")
    
    def get_system_volume(self):
        """Get current system volume"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            return volume_interface.GetMasterVolumeLevelScalar()
        except Exception as e:
            print(f"Error getting volume: {e}")
            return 1.0
    
    def flash_and_beep(self):
        """Flash the background and make beeping sounds for 10 seconds"""
        if self.is_paused:
            return
            
        if self.is_muted:
            self.original_volume = self.get_system_volume()
            # Set volume to 30% to make the reminder more noticeable
            self.set_system_volume(0.3)
        
        start_time = time.time()
        while time.time() - start_time < 10 and not self.is_paused:
            # Toggle background color
            current_color = self.label.cget("bg")
            new_color = "black" if current_color == "white" else "white"
            self.label.configure(bg=new_color)
            
            # Make beeping sound - increased frequency and duration for more noticeable sound
            winsound.Beep(1500, 200)  # 1500Hz for 200ms

            # change text to display time it took to delay
            self.label.configure(text=f"{self.delay}")
            
            # Update the window
            self.root.update()
            time.sleep(0.5)  # Half second delay between flashes
        
        # Reset to white background
        self.label.configure(bg="white")
        self.label.configure(text="?")
        self.root.update()
        
        # Restore original volume if muted
        if self.is_muted and self.original_volume is not None:
            self.set_system_volume(self.original_volume)
    
    def schedule_next_reminder(self):
        """Schedule the next reminder"""
        # Random delay between 5-8 minutes
        self.delay = random.randint(300, 480)  # 300-480 seconds
        self.root.after(self.delay * 1000, self.trigger_reminder)
    
    def trigger_reminder(self):
        """Trigger the reminder and schedule the next one"""
        if not self.is_paused:
            self.flash_and_beep()
        self.schedule_next_reminder()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = ReminderWindow()
    app.run()

if __name__ == "__main__":
    main()
