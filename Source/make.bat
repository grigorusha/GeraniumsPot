rd "C:\Users\Дом\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe" /S /Q

"C:\Users\Дом\PycharmProjects\GeraniumsPot\venv11\Scripts\pyinstaller" main.py -n "Geraniums Pot.exe" -i "Geraniums Pot.ico" --onedir --noconsole --splash "splashfile.gif" --upx-dir C:\Users\Дом\PycharmProjects\UPX

copy "C:\Users\Дом\PycharmProjects\GeraniumsPot\Geraniums Pot.png" "C:\Users\Дом\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\"
copy "C:\Users\Дом\PycharmProjects\GeraniumsPot\README.txt" "C:\Users\Дом\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\"

md "C:\Users\Дом\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\Garden"
xcopy "C:\Users\Дом\PycharmProjects\GeraniumsPot\Garden\*.*" "C:\Users\Дом\PycharmProjects\GeraniumsPot\dist\Geraniums Pot.exe\Garden" /S /E /Y /Q

rem md "C:\Users\Дом\PycharmProjects\GeraniumsPot\dist\GeraniumsPot.exe\Samples"
rem xcopy "C:\Users\Дом\PycharmProjects\GeraniumsPot\Samples\*.*" "C:\Users\Дом\PycharmProjects\GeraniumsPot\dist\GeraniumsPot.exe\Samples" /S /E /Y /Q
