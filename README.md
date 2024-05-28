CreamyKeys is a Python-based application for Windows that emulates the satisfying keyboard sound effects found in the Opera GX browser
<a href="https://github.com/MeepCastana/CreamyKeys/releases/download/v1/KeyboardSoundPlayer.exe">Download here the exe </a> <br><br>Once you open it you can find it in system tray where you can also adjust the volume for it <br><br>Or mess with the code and compile it with pyinstaller using this command ``pyinstaller --name=KeyboardSoundPlayer --onefile --windowed --add-data "ico.ico;." --add-data "sounds;./sounds" keyboard_sounds.py``

Currently when loading the exe file it has small delay 3-5 seconds to load up, im trying to find a way to make it load faster.
