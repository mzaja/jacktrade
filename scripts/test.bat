@ECHO OFF
black --check tests jacktrade
IF %ERRORLEVEL% NEQ 0 ( EXIT 1 )
isort --check tests jacktrade
IF %ERRORLEVEL% NEQ 0 ( EXIT 1 )
coverage run
coverage html
coverage report
