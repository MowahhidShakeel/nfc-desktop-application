import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import json

# --- Assumed Imports ---
# These classes should be in their respective files in the same directory.
from nfc_handler import NFCHandler
from write_handler import MultiCardWriteHandler
from read_handler import MultiCardReadHandler

# A sample configuration to pre-fill the GUI for easy testing.
SAMPLE_CONFIG = {
            "wifi": {
                "ssid": "VeryLongSSIDThatExceedsNormalLimits1234567890",
                "enterpriseIdentity": "user@longdomain.com1234567890",
                "enterpriseUsername": "user1234567890",
                "password": "VerySecurePassword1234567890abcde",
                "enterpriseMode": "EAP-TTLS"
            },
            "mqtt": {
                "host": "mqttserver.very.long.domain.name1234567890",
                "username": "mqttuser1234567890",
                "password": "mqttpass1234567890"
            },
            "ip": {
                "dhcpEnabled": False,
                "ipAddress": "192.168.1.100",
                "netmask": "24",
                "gateway": "192.168.1.1",
                "dns1": "8.8.8.8",
                "dns2": "8.8.4.4",
                "dns3": "1.1.1.1"
            },
            "sntp": {
                "server1": {"value": "time1.very.long.domain.name123"},
                "server2": {"value": "time2.very.long.domain.name123"},
                "server3": {"value": "time3.very.long.domain.name123"}
            }
}



class App:
    """A GUI application to test multi-card NFC read and write operations."""
    def __init__(self, root):
        self.root = root
        self.root.title("NFC Configuration Tool")

        # --- State Management ---
        # Create a single, shared instance of the low-level NFC utility
        self.nfc_utility = NFCHandler()
        
        # Handlers for the high-level, multi-step processes
        self.write_handler = None
        self.read_handler = None

        # --- UI Setup ---
        self._create_widgets()
        # self.reset_state()

    def _create_widgets(self):
        """Sets up all the visual components of the application."""
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Write Section ---
        write_frame = tk.LabelFrame(main_frame, text="Write Configuration", padx=10, pady=10)
        write_frame.pack(fill=tk.X, expand=True, pady=5)
        
        self.write_text = scrolledtext.ScrolledText(write_frame, height=10, width=50)
        self.write_text.pack(fill=tk.BOTH, expand=True)
        # Pre-fill the text box with the sample data in a clean JSON format
        self.write_text.insert(tk.END, json.dumps(SAMPLE_CONFIG, indent=4))

        self.start_write_button = tk.Button(write_frame, text="Start Write", command=self.start_writing)
        self.start_write_button.pack(pady=5, fill=tk.X)

        # --- Read Section ---
        read_frame = tk.LabelFrame(main_frame, text="Read Configuration", padx=10, pady=10)
        read_frame.pack(fill=tk.X, expand=True, pady=5)

        self.start_read_button = tk.Button(read_frame, text="Start Read", command=self.start_reading)
        self.start_read_button.pack(pady=5, fill=tk.X)

        self.read_text = scrolledtext.ScrolledText(read_frame, height=20, width=50, state=tk.DISABLED)
        self.read_text.pack(fill=tk.BOTH, expand=True)

        # --- Status and Action Section ---
        status_frame = tk.Frame(main_frame, pady=10)
        status_frame.pack(fill=tk.X, expand=True)

        bold_font = font.Font(family="Helvetica", size=10, weight="bold")
        self.status_label = tk.Label(status_frame, text="Welcome! Ready to start.", wraplength=400, font=bold_font)
        self.status_label.pack(fill=tk.X)

        self.proceed_button = tk.Button(status_frame, text="Scan Card & Proceed", command=self.proceed_operation, height=2)
        self.proceed_button.pack(pady=10, fill=tk.X)

    def start_writing(self):
        """Initiates the multi-card write process."""
        self.reset_state()
        try:
            config_str = self.write_text.get("1.0", tk.END)
            config_dict = json.loads(config_str)
        except json.JSONDecodeError:
            messagebox.showerror("Invalid Format", "The configuration is not valid JSON. Please correct it.")
            return

        # Instantiate the write process manager
        self.write_handler = MultiCardWriteHandler(self.nfc_utility, config_dict)
        
        self.start_write_button.config(state=tk.DISABLED)
        self.start_read_button.config(state=tk.DISABLED)
        self.proceed_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Process started. {self.write_handler.num_cards} card(s) needed. Please insert card 1.")

    def start_reading(self):
        """Initiates the multi-card read process."""
        self.reset_state()
        
        # Instantiate the read process manager
        self.read_handler = MultiCardReadHandler(self.nfc_utility)
        
        self.start_write_button.config(state=tk.DISABLED)
        self.start_read_button.config(state=tk.DISABLED)
        self.proceed_button.config(state=tk.NORMAL)
        self.status_label.config(text="Read process started. Please insert the first card to read.")

    def proceed_operation(self):
        """Handles the 'Proceed' button click for either reading or writing."""
        result = None
        # Check which process is active (write or read)
        if self.write_handler:
            result = self.write_handler.process_next_card()
        elif self.read_handler:
            result = self.read_handler.process_next_card()
        else:
            messagebox.showwarning("No Operation", "Please start a Read or Write operation first.")
            return

        # Update the GUI based on the result from the handler
        if not result: return
        
        self.status_label.config(text=result.get("message", "An unknown error occurred."))

        if result["status"] == "finished":
            if self.read_handler and "config" in result:
                # If reading is done, display the result
                self.read_text.config(state=tk.NORMAL)
                self.read_text.delete("1.0", tk.END)
                self.read_text.insert(tk.END, json.dumps(result["config"], indent=4))
                self.read_text.config(state=tk.DISABLED)
            
            messagebox.showinfo("Success", result["message"])
            # self.reset_state()

        elif result["status"] == "error":
            messagebox.showerror("Operation Error", result["message"])
            self.reset_state()

    def reset_state(self):
        """Resets the GUI to its initial, idle state."""
        self.write_handler = None
        self.read_handler = None
        
        self.start_write_button.config(state=tk.NORMAL)
        self.start_read_button.config(state=tk.NORMAL)
        self.proceed_button.config(state=tk.DISABLED)
        
        self.status_label.config(text="Ready. Please start a new Read or Write operation.")
        self.read_text.config(state=tk.NORMAL)
        self.read_text.delete('1.0', tk.END)
        self.read_text.config(state=tk.DISABLED)


# --- Main Application Entry Point ---
if __name__ == "__main__":
    app_root = tk.Tk()
    app = App(app_root)
    app_root.mainloop()