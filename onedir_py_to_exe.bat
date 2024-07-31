cls
pyinstaller --clean --optimize 2 --noconfirm --onedir -w src\IMGenAI.py
rmdir /s /q build
del IMGenAI.spec