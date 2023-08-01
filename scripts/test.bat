@ECHO OFF
black --check tests jacktrade
IF %ERRORLEVEL% NEQ 0 ( EXIT /B 1 )
coverage run --source=jacktrade -m unittest discover -s tests -b
coverage html
coverage report