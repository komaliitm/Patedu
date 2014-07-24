@echo off
CALL C:\BitNami\djangostack-1.4.10-2\scripts\setenv.bat
START /MIN "BitNami DjangoStack Environment" CMD /C %*

SET DB_ENGINE=
SET DB_NAME=
SET DB_USER=
SET DB_PASSWORD=
