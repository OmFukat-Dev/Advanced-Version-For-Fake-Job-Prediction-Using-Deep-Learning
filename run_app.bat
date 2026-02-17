@echo off
echo.
echo 🔍 Fake Job Detector Launcher
echo ==============================
echo.

:: Change to project directory
<<<<<<< HEAD
cd /d "C:\Users\fukat\OneDrive\Desktop\fake-job-detector"
=======
:: Change to project directory
cd /d "%~dp0"
>>>>>>> aeaa662 (Advanced Version)

:: Check if directory exists
if not exist "app.py" (
    echo ❌ ERROR: app.py not found!
    pause
    exit /b 1
)

:: Activate virtual environment
echo 📦 Activating Python environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
<<<<<<< HEAD
=======
    
    echo 📦 Checking dependencies...
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
>>>>>>> aeaa662 (Advanced Version)
) else (
    echo ❌ Virtual environment not found!
    pause
    exit /b 1
)

:: Check and create processed data if needed
if not exist "data\processed\train_data.csv" (
    echo ⚠️  Running data cleaning...
    python scripts\run_data_cleaning.py
    if errorlevel 1 (
        echo ❌ Data cleaning failed!
        pause
        exit /b 1
    )
)

:: Check and create tokenizer if needed
if not exist "models\tokenizer.pkl" (
    echo ⚠️  Creating tokenizer...
    python scripts\save_tokenizer.py
    if errorlevel 1 (
        echo ❌ Tokenizer creation failed!
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Starting Streamlit app...
echo 📋 Please wait 10-15 seconds for the app to start...
echo 📋 Then manually open: http://localhost:8501
echo.

:: Run Streamlit in the current window
streamlit run app.py

echo.
echo ⏹️  Application closed.
pause