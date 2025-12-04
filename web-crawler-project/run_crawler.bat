@echo off
REM Web Crawler Project - Windows Batch Script
REM This script provides easy commands to run the web crawler on Windows

echo ========================================
echo      WEB CRAWLER PROJECT
echo ========================================
echo.

if "%1"=="help" goto :help
if "%1"=="install" goto :install
if "%1"=="test" goto :test
if "%1"=="demo" goto :demo
if "%1"=="crawl" goto :crawl
if "%1"=="simple" goto :simple

:menu
echo Choose an option:
echo 1. Install dependencies
echo 2. Run tests
echo 3. Run demo
echo 4. Run keyword crawler
echo 5. Run simple crawler
echo 6. Help
echo 7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto :install
if "%choice%"=="2" goto :test
if "%choice%"=="3" goto :demo
if "%choice%"=="4" goto :crawl
if "%choice%"=="5" goto :simple
if "%choice%"=="6" goto :help
if "%choice%"=="7" goto :exit
echo Invalid choice. Please try again.
goto :menu

:install
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    goto :menu
)
echo Dependencies installed successfully!
pause
goto :menu

:test
echo Running project tests...
python test_crawler.py
pause
goto :menu

:demo
echo Running demonstration...
python test_crawler.py --demo
pause
goto :menu

:crawl
echo Running keyword crawler...
if "%2"=="" (
    scrapy crawl keyword_html_crawler
) else (
    scrapy crawl keyword_html_crawler -a keywords="%2"
)
pause
goto :menu

:simple
echo Running simple crawler...
if "%2"=="" (
    scrapy crawl simple_html_crawler
) else (
    scrapy crawl simple_html_crawler -a urls="%2"
)
pause
goto :menu

:help
echo.
echo USAGE:
echo   run_crawler.bat                    - Show interactive menu
echo   run_crawler.bat install            - Install dependencies
echo   run_crawler.bat test               - Run project tests
echo   run_crawler.bat demo               - Run demonstration
echo   run_crawler.bat crawl [keywords]   - Run keyword crawler
echo   run_crawler.bat simple [urls]      - Run simple crawler
echo   run_crawler.bat help               - Show this help
echo.
echo EXAMPLES:
echo   run_crawler.bat crawl "python,web,data"
echo   run_crawler.bat simple "http://example.com"
echo.
echo For more advanced usage, use the Python scripts directly:
echo   python run_crawler.py --help
echo   python test_crawler.py --help
echo.
pause
goto :menu

:exit
echo Goodbye!
exit /b 0