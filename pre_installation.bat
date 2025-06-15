@echo off
REM Menentukan direktori kerja (sesuaikan dengan path folder Anda)
set "WORKDIR=C:\Code and Application\Data Science\Flood_RandomForest"
set "PYTHON_CMD=python"

REM Memeriksa apakah python tersedia
%PYTHON_CMD% --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python tidak ditemukan. Pastikan Python sudah terinstal dan ada di PATH.
    pause
    exit /b
)

REM Pindah ke direktori kerja
cd /d "%WORKDIR%"

REM Membuat virtual environment jika belum ada
if not exist "venv\" (
    echo Membuat virtual environment...
    %PYTHON_CMD% -m venv venv
)

REM Mengaktifkan virtual environment dan menginstal requirements
echo Mengaktifkan virtual environment dan menginstal requirements...
call venv\Scripts\activate && %PYTHON_CMD% -m pip install --upgrade pip && pip install -r requirements.txt

REM Menjalankan aplikasi Streamlit
echo Menjalankan aplikasi Streamlit...
start "" "cmd.exe" /k "cd /d "%WORKDIR%" && venv\Scripts\activate && streamlit run flood_prediction.py"