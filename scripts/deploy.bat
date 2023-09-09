@ECHO OFF
@REM Publishes the package to PyPI
@REM Install/upgrade twine using: python -m pip install twine --upgrade
@REM API access token must be present in %USERPROFILE%\.pypirc

@REM Upload to Test PyPI to verify everything is ok
@REM python -m twine upload --repository testpypi dist/*

@REM Manually execute the command below to upload to PyPI
@REM python -m twine upload dist/*

@REM Check history, commit, tag the release and push to remote
SET RELEASE_VERSION=0.5.0
FINDSTR %RELEASE_VERSION% "HISTORY.md"
IF %ERRORLEVEL% NEQ 0 (
    ECHO HISTORY.md does not contain the release version!
    EXIT /B 1
) ELSE (
    pre-commit run
    IF %ERRORLEVEL% NEQ 0 (
        ECHO pre-commit found errors and modified files!
        EXIT /B 1
    )
    git add .
    git commit -m "Prepare release %RELEASE_VERSION%"
    git tag v%RELEASE_VERSION%
    git push
    git push --tags
)
