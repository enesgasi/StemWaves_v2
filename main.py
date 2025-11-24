import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys
import shutil


# ---------------- Utility Functions ---------------- #

def get_base_dir():
    """
    Return the absolute directory containing this script.
    Works even when frozen with tools like PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_ffmpeg_path():
    """
    Try to locate ffmpeg in a local 'ffmpeg' folder first.
    Fallback to whatever is in the system PATH.
    
    Returns:
        (ffmpeg_dir, ffmpeg_exe_path) or (None, None) if not found.
    """
    base = get_base_dir()
    local_dir = os.path.join(base, "ffmpeg")
    local_exe = os.path.join(local_dir, "ffmpeg.exe")

    # 1) Prefer bundled ffmpeg.exe
    if os.path.isfile(local_exe):
        return local_dir, local_exe

    # 2) Fallback to system ffmpeg
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return os.path.dirname(system_ffmpeg), system_ffmpeg

    # 3) Not found
    return None, None


def find_demucs_executable():
    """
    Prefer demucs from local .venv\Scripts, then fall back to system PATH.
    """
    base = get_base_dir()
    venv_demucs = os.path.join(base, ".venv", "Scripts", "demucs.exe")
    if os.path.isfile(venv_demucs):
        return venv_demucs

    # Fallback: system-wide demucs
    return shutil.which("demucs")


# ---------------- GUI Callbacks ---------------- #

def select_input():
    file_path = filedialog.askopenfilename(
        title="Select an audio file",
        filetypes=[
            ("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a"),
            ("All Files", "*.*")
        ]
    )
    if file_path:
        input_path.set(file_path)


def select_output():
    folder_path = filedialog.askdirectory(title="Select output folder")
    if folder_path:
        output_path.set(folder_path)


def run_separation():
    input_file = input_path.get()
    output_folder = output_path.get()

    if not input_file:
        messagebox.showerror("Error", "Please select an input file.")
        return
    if not output_folder:
        messagebox.showerror("Error", "Please select an output folder.")
        return

    # Check Demucs
    demucs_exe = find_demucs_executable()
    if demucs_exe is None:
        messagebox.showerror(
            "Demucs Not Found",
            "Could not find the 'demucs' command.\n\n"
            "Please install Demucs first:\n"
            "    pip install demucs\n\n"
            "Then make sure your terminal can run:\n"
            "    demucs --help"
        )
        return

    # Check FFmpeg
    ffmpeg_dir, ffmpeg_exe = get_ffmpeg_path()
    if ffmpeg_exe is None:
        messagebox.showerror(
            "FFmpeg Not Found",
            "FFmpeg could not be found.\n\n"
            "You can either:\n"
            "  • Place ffmpeg.exe in a folder named 'ffmpeg' next to main.py\n"
            "    (StemWaveLite/ffmpeg/ffmpeg.exe)\n"
            "  • Or install FFmpeg and add it to your system PATH."
        )
        return

    # Disable button and update status
    separate_btn.config(state="disabled")
    status_label.config(text="Separating... Please wait.")

    def worker():
        try:
            # Prepare environment: make sure ffmpeg dir is in PATH
            env = os.environ.copy()
            if ffmpeg_dir:
                env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")

            cmd = [
                demucs_exe,
                "-n", "htdemucs",       # model name
                "-o", output_folder,    # output directory
                input_file              # input file
            ]

            # Run Demucs; raise CalledProcessError on failure
            subprocess.run(cmd, check=True, env=env)

            status_label.config(text="Separation complete!")
            messagebox.showinfo(
                "Done",
                f"Stems saved in:\n{output_folder}"
            )

        except subprocess.CalledProcessError as e:
            status_label.config(text="Error during separation.")
            messagebox.showerror(
                "Error",
                "Demucs failed to process the file.\n\n"
                f"Details:\n{e}"
            )
        except Exception as e:
            status_label.config(text="Unexpected error.")
            messagebox.showerror(
                "Error",
                f"An unexpected error occurred:\n{e}"
            )
        finally:
            separate_btn.config(state="normal")

    # Run in background so GUI stays responsive
    threading.Thread(target=worker, daemon=True).start()


# ---------------- GUI Setup ---------------- #

root = tk.Tk()
root.title("StemWave Lite - Audio Stem Separator")
root.geometry("540x260")
root.resizable(False, False)

input_path = tk.StringVar()
output_path = tk.StringVar()

# Input file
tk.Label(root, text="Input Audio File:").pack(pady=(10, 2))
input_frame = tk.Frame(root)
input_frame.pack()
tk.Entry(input_frame, textvariable=input_path, width=52).pack(side=tk.LEFT, padx=(0, 5))
tk.Button(input_frame, text="Browse", command=select_input).pack(side=tk.LEFT)

# Output folder
tk.Label(root, text="Output Folder:").pack(pady=(10, 2))
output_frame = tk.Frame(root)
output_frame.pack()
tk.Entry(output_frame, textvariable=output_path, width=52).pack(side=tk.LEFT, padx=(0, 5))
tk.Button(output_frame, text="Select", command=select_output).pack(side=tk.LEFT)

# Separate button
separate_btn = tk.Button(root, text="Separate Stems", command=run_separation)
separate_btn.pack(pady=18)

# Status label
status_label = tk.Label(root, text="", fg="blue")
status_label.pack(pady=(0, 10))

root.mainloop()
