rd "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe" /S /Q

"C:\Users\���\PycharmProjects\GeraniumsPot\venv11\Scripts\pyinstaller" main.py -n "Geraniums Pot.exe" -i "Geraniums Pot.ico" --onedir --noconsole --splash "splashfile.gif" --upx-dir C:\Users\���\PycharmProjects\UPX

copy "C:\Users\���\PycharmProjects\GeraniumsPot\Geraniums Pot.ico" "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\"
copy "C:\Users\���\PycharmProjects\GeraniumsPot\Geraniums Pot.png" "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\"
copy "C:\Users\���\PycharmProjects\GeraniumsPot\README.txt" "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\"

md "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\Garden"
xcopy "C:\Users\���\PycharmProjects\GeraniumsPot\Garden\*.*" "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\Garden" /S /E /Y /Q
md "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\Photo"
xcopy "C:\Users\���\PycharmProjects\GeraniumsPot\Photo\*.*" "C:\Users\���\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\Photo" /S /E /Y /Q
