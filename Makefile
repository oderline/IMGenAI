all:
ifeq ($(OS), Windows_NT)
	venv\Scripts\python.exe src\IMGenAI.py
else
	venv/bin/python3 src/IMGenAI.py
endif


setup:
ifeq ($(OS), Windows_NT)
	python -m venv venv
	venv\Scripts\pip install -r requirements.txt
else
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
endif


ui:
ifeq ($(OS), Windows_NT)
	venv\Scripts\pyuic6 -x -o src/window.py src/ui/window.ui
	venv\Scripts\pyuic6 -x -o src/ui/config.py src/ui/config.ui
	venv\Scripts\pyuic6 -x -o src/ui/about.py src/ui/about.ui
else
	venv/bin/pyuic6 -x -o src/window.py src/ui/window.ui
	venv/bin/pyuic6 -x -o src/ui/config.py src/ui/config.ui
	venv/bin/pyuic6 -x -o src/ui/about.py src/ui/about.ui
endif


onefile:
ifeq ($(OS), Windows_NT)
	venv\Scripts\pyinstaller --clean --optimize 2 --noconfirm --onefile -w src/IMGenAI.py
	rmdir /q /s build
	del *.spec
else
	venv/bin/pyinstaller --clean --optimize 2 --noconfirm --onefile -w src/IMGenAI.py
	rm -rf build
	rm *.spec
endif


onedir:
ifeq ($(OS), Windows_NT)
	venv\Scripts\pyinstaller --clean --optimize 2 --noconfirm --onedir -w src/IMGenAI.py
	rmdir /q /s build
	del *.spec
else
	venv/bin/pyinstaller --clean --optimize 2 --noconfirm --onedir -w src/IMGenAI.py
	rm -rf build
	rm *.spec
endif
