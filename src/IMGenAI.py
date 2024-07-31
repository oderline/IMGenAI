from PyQt6.QtWidgets import QFileDialog, QApplication, QMainWindow
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6 import QtCore

import threading, requests, base64, random, ujson, sys, os

from window import Ui_MainWindow


# TODO: config file (config.ini), import configparser

# For correct prompt saving
last_used_seed = "-1"


def openPrompt() -> None:
	filename = QFileDialog().getOpenFileName(
		caption="Open prompt file",
		filter="Text files (*.txt)"
	)

	with open(filename[0], "r") as f:
		data: dict = ujson.load(f)
		f.close()

	setValues(data)
	global last_used_seed
	last_used_seed = data["seed"]

def savePrompt() -> None:
	filename = QFileDialog().getSaveFileName(
		caption="Save prompt file",
		filter="Text files (*.txt)"
	)

	with open(filename[0], "w") as f:
		data: dict = getValues()
		data["seed"] = last_used_seed
		f.write(ujson.dumps(data, indent=4))
		f.close()

def toggleSidebar() -> None:
	if ui.toggle_sidebar.isChecked():
		MainWindow.setFixedSize(1000, MainWindow.height())
		ui.image.setGeometry(QtCore.QRect(270, 10, 720, 720))
		ui.widget1.show()
	else:
		MainWindow.setFixedSize(740, MainWindow.height())
		ui.image.setGeometry(QtCore.QRect(10, 10, 720, 720))
		ui.widget1.hide()

def getValues() -> dict:
	return {
		"prompt": ui.textEdit1.toPlainText(),
		"negative_prompt": ui.textEdit2.toPlainText(),
		"seed": ui.lineEdit1.text() if int(ui.lineEdit1.text()) != -1 else random.randint(0, 1000000000),
		"sampling_steps": ui.spinBox1.value(),
		"width": ui.spinBox2.value(),
		"height": ui.spinBox3.value(),
		"guidance_scale": ui.spinBox4.value(),
		"NSFW_content": int(ui.NSFW_content.isChecked())
	}

def setValues(data: dict) -> None:
	ui.textEdit1.setText(data["prompt"])
	ui.textEdit2.setText(data["negative_prompt"])
	ui.lineEdit1.setText(str(data["seed"]))
	ui.spinBox1.setValue(data["sampling_steps"])
	ui.spinBox2.setValue(data["width"])
	ui.spinBox3.setValue(data["height"])
	ui.spinBox4.setValue(data["guidance_scale"])
	ui.NSFW_content.setChecked(data["NSFW_content"])

def generate() -> None:
	# Get url and prompt data
	url: str = ui.lineEdit2.text()
	data: dict = getValues()

	# Update last used seed
	global last_used_seed
	last_used_seed = data["seed"]

	# Get response
	try:
		MainWindow.statusBar().showMessage("Generating image...")
		responce: requests.Response = requests.post(url, data)
		img: bytes = base64.b64decode(responce.content)
	except Exception as e:
		MainWindow.statusBar().showMessage(e)
		return

	# Get date and time
	date: str = QtCore.QDate.currentDate().toString("dd-MM-yyyy")
	time: str = QtCore.QTime.currentTime().toString("hh-mm-ss")

	# Save images
	if ui.save_images.isChecked():
		image_file: str = f"output/images/{date}/image_{time}.png"
		os.makedirs(os.path.dirname(image_file), exist_ok=True)
		with open(image_file, "wb") as f:
			f.write(img)
			f.close()

	# Save prompts
	if ui.save_prompts.isChecked():
		prompt_file: str = f"output/prompts/{date}/image_{time}.txt"
		os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
		with open(prompt_file, "w") as f:
			f.write(ujson.dumps(data, indent=4))
			f.close()

	# Create pixmap
	pixmap: QPixmap = QPixmap()
	pixmap.loadFromData(img)

	# Resize image
	if pixmap.width() > ui.image.width() or pixmap.height() > ui.image.height():
		pixmap = pixmap.scaled(720, 720, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)

	# Display image
	ui.image.setPixmap(pixmap)

	# Delete pixmap
	del pixmap


if __name__ == "__main__":
	app = QApplication(sys.argv)
	MainWindow = QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	ui.statusbar.hide()
	MainWindow.setFixedSize(MainWindow.size())
	MainWindow.show()

	# Set icons
	ui.open_prompt.setIcon(QIcon().fromTheme("document-open"))
	ui.save_prompt.setIcon(QIcon().fromTheme("document-save"))
	ui.configuration.setIcon(QIcon().fromTheme("document-properties"))
	ui.reset_prompt.setIcon(QIcon().fromTheme("view-restore"))

	# Configure "File" menu functions
	ui.open_prompt.triggered.connect(openPrompt)
	ui.save_prompt.triggered.connect(savePrompt)

	# Configure "Settings" menu functions
	ui.toggle_sidebar.triggered.connect(toggleSidebar)
	ui.reset_prompt.triggered.connect(lambda: setValues({
		"prompt": "",
		"negative_prompt": "",
		"seed": "-1",
		"sampling_steps": 20,
		"width": 512,
		"height": 512,
		"guidance_scale": 7
	}))

	# Configure "Help" menu functions
	# 

	# Change SpinBox values
	ui.horizontalSlider1.valueChanged.connect(lambda: ui.spinBox1.setValue(ui.horizontalSlider1.value()))
	ui.horizontalSlider2.valueChanged.connect(lambda: ui.spinBox2.setValue(ui.horizontalSlider2.value()))
	ui.horizontalSlider3.valueChanged.connect(lambda: ui.spinBox3.setValue(ui.horizontalSlider3.value()))
	ui.horizontalSlider4.valueChanged.connect(lambda: ui.spinBox4.setValue(ui.horizontalSlider4.value()))


	# Change HorizontalSlider values
	ui.spinBox1.valueChanged.connect(lambda: ui.horizontalSlider1.setValue(ui.spinBox1.value()))
	ui.spinBox2.valueChanged.connect(lambda: ui.horizontalSlider2.setValue(ui.spinBox2.value()))
	ui.spinBox3.valueChanged.connect(lambda: ui.horizontalSlider3.setValue(ui.spinBox3.value()))
	ui.spinBox4.valueChanged.connect(lambda: ui.horizontalSlider4.setValue(ui.spinBox4.value()))

	# Connect buttons
	# ui.pushButton1.clicked.connect()
	ui.pushButton2.clicked.connect(lambda: ui.lineEdit1.setText(str(random.randint(0, 9999_9999_9999_9999))))
	ui.pushButton3.clicked.connect(lambda: ui.lineEdit1.setText("-1"))
	ui.pushButton4.clicked.connect(lambda: threading.Thread(target=generate).start())

	sys.exit(app.exec())
