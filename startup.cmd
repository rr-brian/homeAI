@echo off
echo Starting application with gunicorn...
cd %HOME%\site\wwwroot
set PYTHONPATH=%HOME%\site\wwwroot
%HOME%\Python\python.exe -m gunicorn --bind=0.0.0.0:%HTTP_PLATFORM_PORT% wsgi:application
