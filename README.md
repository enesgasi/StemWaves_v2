# StemWave v2.0

StemWave v2.0 is a simple desktop application that separates audio tracks into individual stems (vocals, drums, bass, and others) using the Demucs machine learning model. It provides an easy interface for selecting an input audio file and exporting the separated stems to a chosen folder.

## Requirements and Dependencies

- Windows 10 or later  
- Python 3.10.9 (automatically installed by `install.bat` if missing)  
- Virtual environment created by `install.bat`  
- Demucs 4.0.0  
- FFmpeg (bundled locally or available in system PATH)  
- Other dependencies listed in `requirements.txt`

## Usage

1. Run `install.bat` to install Python 3.10.9 and all required packages.  
3. After installation, run `run.bat` to start the application.  
4. Select an input audio file.  
5. Choose an output folder.  
6. Click "Separate Stems" to begin processing.  
7. The separated stems will be saved inside the selected output folder.
