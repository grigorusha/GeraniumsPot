rd "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe" /S /Q

"C:\Users\���\PycharmProjects\GeraniumsPot\venv11\Scripts\pyinstaller" main.py -n "Geraniums Pot.exe" -i "Geraniums Pot.ico" --onedir --noconsole --splash "splashfile.gif" --upx-dir C:\Users\���\PycharmProjects\UPX

copy "C:\Users\���\PycharmProjects\GeraniumsPot\Geraniums Pot.png" "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\"
copy "C:\Users\���\PycharmProjects\GeraniumsPot\README.txt" "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\"

md "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\Garden"
xcopy "C:\Users\���\PycharmProjects\GeraniumsPot\Garden\*.*" "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\Garden" /S /E /Y /Q

rem md "C:\Users\���\PycharmProjects\GeraniumsPot\dist\GeraniumsPot.exe\Samples"
rem xcopy "C:\Users\���\PycharmProjects\GeraniumsPot\Samples\*.*" "C:\Users\���\PycharmProjects\GeraniumsPot\dist\GeraniumsPot.exe\Samples" /S /E /Y /Q
