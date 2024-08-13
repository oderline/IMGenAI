all:
	pyuic6 -x -o src/window.py src/window.ui
	pyuic6 -x -o src/config.py src/config.ui
	pyuic6 -x -o src/about.py src/about.ui

ui:
	qt6-tools designer

onefile:


onedir:
	pyinstaller --clean --optimize 2 --noconfirm --onedir -w src/IMGenAI.py
