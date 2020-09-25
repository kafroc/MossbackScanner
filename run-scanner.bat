start /b mitmdump -s mitmScript.py -p 8899 > nul 2>&1

::tasklist
::taskkill /im mitmdump.exe /t /f

start /b python  mossbackScaner.py
