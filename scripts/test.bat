@ECHO OFF
black --check tests jacktrade
IF %ERRORLEVEL% NEQ 0 ( EXIT 1 )
isort --check tests jacktrade
IF %ERRORLEVEL% NEQ 0 ( EXIT 1 )
coverage run --source=jacktrade -m unittest discover -s tests -b
coverage html
coverage report
