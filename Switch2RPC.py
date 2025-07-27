import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import subprocess
import time
import os
import psutil
from pypresence import Presence
import threading
import sys
import pystray
from PIL import Image, ImageDraw

FAKE_GAME_EXE = os.path.abspath("rpc/Game.exe")

PROFILES = {
    "Nintendo Switch 2": {
        "game_title": "Nintendo Switch 2",
        "details": "Idle",
        "state": "HOME Menu",
        "large_image_key": "ns2",
        "large_image_text": "HOME Menu",
        "small_image_key": "NS2",
        "small_image_text": "Nintendo Switch 2",
        "client_id": "1398866630045470770"
    },
    "Splatoon 3": {
        "game_title": "Splatoon 3",
        "details": "In Game",
        "state": "Nintendo Switch 2",
        "large_image_key": "splatoon3",
        "large_image_text": "Splatoon 3",
        "small_image_key": "NS2",
        "small_image_text": "Nintendo Switch 2",
        "client_id": "1398872624922099833"
    },
    "Mario Kart World": {
        "game_title": "Mario Kart World",
        "details": "In Game",
        "state": "Nintendo Switch 2",
        "large_image_key": "mariokartworld",
        "large_image_text": "Mario Kart World",
        "small_image_key": "NS2",
        "small_image_text": "Nintendo Switch 2",
        "client_id": "1398880485253582939"
    }
}

class FakeGameManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Nintendo Switch 2 - Local Discord RPC")
        self.root.geometry("400x250")
        self.root.minsize(400, 250)

        self.rpc = None
        self.connected = False
        self.proc = None
        self.tray_icon = None

        mainframe = ttk.Frame(root, padding="10")
        mainframe.pack(fill="both", expand=True)

        ttk.Label(mainframe, text="Select Game:").pack(pady=(0, 5))

        self.profile_var = tk.StringVar()
        self.combobox = ttk.Combobox(mainframe, textvariable=self.profile_var, state="readonly")
        self.combobox['values'] = list(PROFILES.keys())
        self.combobox.current(0)
        self.combobox.pack(fill='x', pady=(0, 15))

        button_frame = ttk.Frame(mainframe)
        button_frame.pack(fill="x", expand=True)

        ttk.Button(button_frame, text="Launch Game RPC", command=self.launch_profile).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Button(button_frame, text="Minimize to Tray", command=self.minimize_to_tray).grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Button(button_frame, text="Disconnect RPC", command=self.disconnect_rpc).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        threading.Thread(target=self.setup_tray_icon, daemon=True).start()

    def setup_tray_icon(self):
        image = Image.new('RGB', (64, 64), color='black')
        dc = ImageDraw.Draw(image)
        dc.rectangle([16, 16, 48, 48], fill='white')

        menu = pystray.Menu(
            pystray.MenuItem('Open RPC Menu', self.show_window),
            pystray.MenuItem('Quit', self.quit_app)
        )

        self.tray_icon = pystray.Icon("DiscordRPC", image, "Switch2", menu)
        self.tray_icon.run()

    def show_window(self, icon=None, item=None):
        self.root.after(0, self.root.deiconify)

    def minimize_to_tray(self):
        self.root.withdraw()

    def quit_app(self, icon=None, item=None):
        self.close_game()
        self.disconnect_rpc()
        if self.tray_icon:
            self.tray_icon.stop()
        os._exit(0)

    def launch_profile(self):
        profile_name = self.profile_var.get()
        profile = PROFILES[profile_name]

        if not os.path.exists(FAKE_GAME_EXE):
            messagebox.showerror("Error", f"EXE not found at:\n{FAKE_GAME_EXE}")
            return

        self.close_game()

        self.proc = subprocess.Popen(
            [FAKE_GAME_EXE, profile["game_title"]],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )

        client_id = profile.get("client_id")
        if not client_id:
            messagebox.showerror("Error", "Client ID missing in profile.")
            return

        try:
            if self.connected:
                self.rpc.clear()
                self.rpc.close()
                self.connected = False

            self.rpc = Presence(client_id)
            self.rpc.connect()
            self.connected = True

            self.rpc.update(
                details=profile.get("details", ""),
                state=profile.get("state", ""),
                large_image=profile.get("large_image_key", ""),
                large_text=profile.get("large_image_text", ""),
                small_image=profile.get("small_image_key", ""),
                small_text=profile.get("small_image_text", ""),
                start=time.time()
            )
            messagebox.showinfo("Success", f"Launched profile '{profile_name}' and updated presence.")
        except Exception as e:
            messagebox.showerror("RPC Error", str(e))

    def minimize_game(self):
        pass

    def close_game(self):
        if self.proc and self.proc.poll() is None:
            try:
                proc = psutil.Process(self.proc.pid)
                proc.terminate()
                self.proc.wait(timeout=5)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to close game: {e}")
            finally:
                self.proc = None

    def clear_presence(self):
        if self.rpc and self.connected:
            try:
                self.rpc.clear()
                messagebox.showinfo("Presence Cleared", "Discord presence cleared.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showinfo("Info", "No active RPC connection.")

    def disconnect_rpc(self):
        if self.rpc and self.connected:
            try:
                self.rpc.clear()
                self.rpc.close()
                self.connected = False
                messagebox.showinfo("Disconnected", "Disconnected from Discord RPC.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showinfo("Info", "Ended Background RPC.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FakeGameManager(root)
    root.mainloop()
