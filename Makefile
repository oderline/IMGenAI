all:
ifeq ($(OS), Windows_NT)
	venv\Scripts\python.exe src\IMGenAI.py
else
	venv/bin/python3 src/IMGenAI.py
endif


setup:
ifeq ($(OS), Windows_NT)
	echo W
else
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
endif


ui:
ifeq ($(OS), Windows_NT)
	echo W
else
	venv/bin/pyuic6 -x -o src/window.py src/ui/window.ui
	venv/bin/pyuic6 -x -o src/ui/config.py src/ui/config.ui
	venv/bin/pyuic6 -x -o src/ui/about.py src/ui/about.ui
endif


onefile:
ifeq ($(OS), Windows_NT)
	echo W
else
	venv/bin/pyinstaller --clean --optimize 2 --noconfirm --onefile -w src/IMGenAI.py
	rm -rf build
	rm *.spec
endif


onedir:
ifeq ($(OS), Windows_NT)
	echo W
else
	venv/bin/pyinstaller --clean --optimize 2 --noconfirm --onedir -w src/IMGenAI.py
	rm -rf build
	rm *.spec
endif
