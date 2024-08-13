cls
pyinstaller --clean --optimize 2 --noconfirm --onefile -w src/IMGenAI.py
rmdir /s /q build
del IMGenAI.spec