@ECHO OFF
black --check tests jacktrade
coverage run --source=jacktrade -m unittest discover -s tests -b
coverage html
coverage report