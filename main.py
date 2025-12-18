import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
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
    Prefer demucs from local .venv/Scripts, then fall back to system PATH.
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


def the_most_important_function_ever():
    print("Ayhan Hocam selmlar")
    return "Nothing important"

the_most_important_function_ever()

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
    status_label.config(text="Separating... This may take a while.")
    progress_bar.start(10)

    # Decide which model to use based on UI selection
    mode = model_var.get()
    if mode == "5":
        # Experimental 6-sources model: vocals, drums, bass, other, guitar, piano
        model_name = "htdemucs_6s"
    else:
        # Standard 4-sources: vocals, drums, bass, other
        model_name = "htdemucs"

    def worker():
        try:
            # Prepare environment: make sure ffmpeg dir is in PATH
            env = os.environ.copy()
            if ffmpeg_dir:
                env["PATH"] = ffmpeg_dir + os.pathsep + env.get("PATH", "")

            cmd = [
                demucs_exe,
                "-n", model_name,    # model name
                "-o", output_folder, # output directory
                input_file           # input file
            ]

            subprocess.run(cmd, check=True, env=env)

            if mode == "5":
                status_label.config(
                    text="Separation complete! (Vocal, Drums, Bass, Other, Guitar + Piano)"
                )
            else:
                status_label.config(
                    text="Separation complete! (Vocal, Drums, Bass, Other)"
                )

            messagebox.showinfo(
                "Done",
                f"Stems saved in:\n{output_folder}\n\n"
                "Note: For the extended mode, Demucs also outputs a 'piano' stem."
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
            progress_bar.stop()

    # Run in background so GUI stays responsive
    threading.Thread(target=worker, daemon=True).start()


# ---------------- GUI Setup ---------------- #

root = tk.Tk()
root.title("StemWave v2.1 - Audio Stem Separator")

# Slightly larger, centered window
root.geometry("600x500")
root.resizable(False, False)

# Use ttk theme for a more modern look
style = ttk.Style()
try:
    style.theme_use("clam")
except tk.TclError:
    # Fallback if theme is not available
    pass

# Global font tweaks (optional, comment out if you don't like it)
default_font = ("Segoe UI", 9)
root.option_add("*Font", default_font)

main_frame = ttk.Frame(root, padding=15)
main_frame.pack(fill="both", expand=True)

# Header
header_frame = ttk.Frame(main_frame)
header_frame.pack(fill="x", pady=(0, 12))

title_label = ttk.Label(
    header_frame,
    text="StemWave v2.1",
    font=("Segoe UI", 14, "bold")
)
title_label.pack(anchor="w")

subtitle_label = ttk.Label(
    header_frame,
    text="Deep-learning powered audio stem separation (Demucs)",
    foreground="#555555"
)
subtitle_label.pack(anchor="w")

# Input section
io_frame = ttk.LabelFrame(main_frame, text="Input / Output", padding=10)
io_frame.pack(fill="x", pady=(0, 10))

input_path = tk.StringVar()
output_path = tk.StringVar()
model_var = tk.StringVar(value="4")  # "4" or "5"

# Input row
input_row = ttk.Frame(io_frame)
input_row.pack(fill="x", pady=5)

ttk.Label(input_row, text="Input audio file:").pack(side="left")
input_entry = ttk.Entry(input_row, textvariable=input_path)
input_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
ttk.Button(input_row, text="Browse...", command=select_input).pack(side="left")

# Output row
output_row = ttk.Frame(io_frame)
output_row.pack(fill="x", pady=5)

ttk.Label(output_row, text="Output folder:").pack(side="left")
output_entry = ttk.Entry(output_row, textvariable=output_path)
output_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
ttk.Button(output_row, text="Select...", command=select_output).pack(side="left")

# Model selection
model_frame = ttk.LabelFrame(main_frame, text="Separation Mode", padding=10)
model_frame.pack(fill="x", pady=(0, 10))

rb_4 = ttk.Radiobutton(
    model_frame,
    text="Standard (4 stems: Vocals, Drums, Bass, Other)",
    value="4",
    variable=model_var
)
rb_4.pack(anchor="w", pady=2)

rb_5 = ttk.Radiobutton(
    model_frame,
    text="Extended (5 stems: Vocals, Drums, Bass, Other, Guitar, Piano)",
    value="5",
    variable=model_var
)
rb_5.pack(anchor="w", pady=2)

model_hint = ttk.Label(
    model_frame,
    text="Note: Extended mode uses the experimental htdemucs_6s model.\n"
         "It outputs Vocals, Drums, Bass, Other, Guitar, and Piano.",
    foreground="#666666"
)
model_hint.pack(anchor="w", pady=(4, 0))

# Action + status
bottom_frame = ttk.Frame(main_frame)
bottom_frame.pack(fill="x", pady=(10, 0))

separate_btn = ttk.Button(
    bottom_frame,
    text="Separate Stems",
    command=run_separation
)
separate_btn.pack(side="left")

progress_bar = ttk.Progressbar(
    bottom_frame,
    mode="indeterminate",
    length=200
)
progress_bar.pack(side="left", padx=(10, 0))

status_label = ttk.Label(
    main_frame,
    text="",
    foreground="#0055aa"
)
status_label.pack(anchor="w", pady=(8, 0))

root.mainloop()
