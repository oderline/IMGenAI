from PyQt6 import QtCore, QtGui, QtWidgets

# from PIL.PngImagePlugin import PngInfo
from PIL import Image

import threading, requests, base64, random, ujson, sys, os
from time import sleep

from window import Ui_MainWindow
from config import Ui_Dialog


# TODO: config file (config.ini), import configparser


class IMGenAI():
	def __init__(self) -> None:
		# For correct prompt saving
		self.last_used_seed: int = -1

	def run(self) -> None:
		self.app = QtWidgets.QApplication(sys.argv)
		self.MainWindow = QtWidgets.QMainWindow()
		self.main_window = Ui_MainWindow()
		self.main_window.setupUi(self.MainWindow)
		self.main_window.statusbar.hide()
		self.MainWindow.setFixedSize(self.MainWindow.size())
		self.setupMainWindowUI()
		self.MainWindow.show()

		sys.exit(self.app.exec())

	def setupMainWindowUI(self) -> None:
		# Set icons
		self.main_window.open_file.setIcon(QtGui.QIcon().fromTheme("document-open"))
		self.main_window.open_image.setIcon(QtGui.QIcon().fromTheme("document-open"))
		self.main_window.save_prompt.setIcon(QtGui.QIcon().fromTheme("document-save"))
		self.main_window.configuration.setIcon(QtGui.QIcon().fromTheme("document-properties"))
		self.main_window.reset_prompt.setIcon(QtGui.QIcon().fromTheme("view-restore"))

		# Configure shorttcut keys
		self.main_window.pushButton4.setShortcut(QtGui.QKeySequence("Ctrl+Return"))

		# Configure "File" menu functions
		self.main_window.open_file.triggered.connect(self.openFile)
		# self.main_window.open_image.triggered.connect(self.openImage)
		self.main_window.save_prompt.triggered.connect(self.savePrompt)

		# Configure "Settings" menu functions
		self.main_window.toggle_sidebar.triggered.connect(self.toggleSidebar)
		self.main_window.configuration.triggered.connect(self.configuWindow)
		self.main_window.reset_prompt.triggered.connect(lambda: self.setValues({
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
		self.main_window.horizontalSlider1.valueChanged.connect(lambda: self.main_window.spinBox1.setValue(self.main_window.horizontalSlider1.value()))
		self.main_window.horizontalSlider2.valueChanged.connect(lambda: self.main_window.spinBox2.setValue(self.main_window.horizontalSlider2.value()))
		self.main_window.horizontalSlider3.valueChanged.connect(lambda: self.main_window.spinBox3.setValue(self.main_window.horizontalSlider3.value()))
		self.main_window.horizontalSlider4.valueChanged.connect(lambda: self.main_window.spinBox4.setValue(self.main_window.horizontalSlider4.value()))

		# Change HorizontalSlider values
		self.main_window.spinBox1.valueChanged.connect(lambda: self.main_window.horizontalSlider1.setValue(self.main_window.spinBox1.value()))
		self.main_window.spinBox2.valueChanged.connect(lambda: self.main_window.horizontalSlider2.setValue(self.main_window.spinBox2.value()))
		self.main_window.spinBox3.valueChanged.connect(lambda: self.main_window.horizontalSlider3.setValue(self.main_window.spinBox3.value()))
		self.main_window.spinBox4.valueChanged.connect(lambda: self.main_window.horizontalSlider4.setValue(self.main_window.spinBox4.value()))

		# Connect buttons
		self.main_window.pushButton2.clicked.connect(lambda: self.main_window.lineEdit1.setText(str(random.randint(0, 9999_9999_9999_9999))))
		self.main_window.pushButton3.clicked.connect(lambda: self.main_window.lineEdit1.setText("-1"))
		self.main_window.pushButton4.clicked.connect(lambda: threading.Thread(target=self.generate).start())

	def configuWindow(self) -> None:
		from PyQt6.QtWidgets import QDialog
		self.ConfigWindow = QDialog()
		self.config_window = Ui_Dialog()
		self.config_window.setupUi(self.ConfigWindow)
		self.setupConfigWindowUI()
		self.ConfigWindow.show()

	def setupConfigWindowUI(self) -> None:
		self.config_window.listView.setMovement(QtGui.QListView.Movement.Static)
		self.config_window.listView.setModel(QtGui.QStandardItemModel())

		# List of configuration menu items
		self.config_window.listView.model().appendRow(QtGui.QStandardItem("1"))
		self.config_window.listView.model().appendRow(QtGui.QStandardItem("2"))
		self.config_window.listView.model().appendRow(QtGui.QStandardItem("3"))

	# 	self.config_window.listView.clicked.connect(self.changeConfigTab)

	# def changeConfigTab(self):
	# 	y = self.config_window.listView.selectedIndexes()
	# 	z = self.config_window.listView.model().itemData(y[0])[0]
	# 	print(z)

	def openFile(self) -> None:
		try:
			filename = QtWidgets.QFileDialog().getOpenFileName(
				caption="Open image/prompt file",
				# filter="Image files (*.png);;Text files (*.txt)"
				filter="Image/Text files (*.png *.txt)"
			)

			with open(filename[0], "r") as f:
				data: dict = ujson.load(f)
				f.close()

			self.setValues(data)
			self.last_used_seed = int(data["seed"])
		except:
			...

	def savePrompt(self) -> None:
		try:
			filename = QtWidgets.QFileDialog().getSaveFileName(
				caption="Save prompt file",
				filter="Text files (*.txt)"
			)

			with open(filename[0], "w") as f:
				data: dict = self. getValues()
				# data["seed"] = str(self.last_used_seed)
				data["seed"] = self.last_used_seed
				f.write(ujson.dumps(data, indent=4))
				f.close()
		except:
			...

	def toggleSidebar(self) -> None:
		if self.main_window.toggle_sidebar.isChecked():
			self.MainWindow.setFixedSize(1000, self.MainWindow.height())
			self.main_window.image.setGeometry(QtCore.QRect(270, 10, 720, 720))
			self.main_window.widget1.show()
		else:
			self.MainWindow.setFixedSize(740, self.MainWindow.height())
			self.main_window.image.setGeometry(QtCore.QRect(10, 10, 720, 720))
			self.main_window.widget1.hide()

	def getValues(self) -> dict:
		return {
			"prompt": self.main_window.textEdit1.toPlainText(),
			"negative_prompt": self.main_window.textEdit2.toPlainText(),
			"seed": int(self.main_window.lineEdit1.text()) if int(self.main_window.lineEdit1.text()) != -1 else random.randint(0, 9999_9999_9999_9999),
			"sampling_steps": self.main_window.spinBox1.value(),
			"width": self.main_window.spinBox2.value(),
			"height": self.main_window.spinBox3.value(),
			"guidance_scale": self.main_window.spinBox4.value(),
			"NSFW_content": int(self.main_window.NSFW_content.isChecked())
		}

	def setValues(self, data: dict) -> None:
		self.main_window.textEdit1.setText(str(data["prompt"]))
		self.main_window.textEdit2.setText(str(data["negative_prompt"]))
		self.main_window.lineEdit1.setText(str(data["seed"]))
		self.main_window.spinBox1.setValue(int(data["sampling_steps"]))
		self.main_window.spinBox2.setValue(int(data["width"]))
		self.main_window.spinBox3.setValue(int(data["height"]))
		self.main_window.spinBox4.setValue(int(data["guidance_scale"]))

		# For compatibility with old prompt files
		try:
			self.main_window.NSFW_content.setChecked(data["NSFW_content"])
		except:
			self.main_window.NSFW_content.setChecked(False)

	def setStatusBarText(self, text: str, time: int = 5) -> None:
		self.main_window.statusbar.show()
		self.MainWindow.statusBar().showMessage(text)
		sleep(time)
		self.main_window.statusbar.hide() if time > 0 else ...

	def generate(self) -> None:
		# Get url and prompt data
		url: str = self.main_window.lineEdit2.text()
		data: dict = self.getValues()

		# Update last used seed
		global last_used_seed
		last_used_seed = int(data["seed"])

		# POST request and response
		try:
			threading.Thread(target=self.setStatusBarText, args=("Generating image...", 0)).start()
			responce: requests.Response = requests.post(url, data)
			img: bytes = base64.b64decode(responce.content)
		except Exception as e:
			threading.Thread(target=self.setStatusBarText, args=(f"{e}",)).start()
			return

		# Get date and time
		date: str = QtCore.QDate.currentDate().toString("dd-MM-yyyy")
		time: str = QtCore.QTime.currentTime().toString("hh-mm-ss")

		# Save images
		if self.main_window.save_images.isChecked():
			image_file: str = f"output/images/{date}/image_{time}.png"
			os.makedirs(os.path.dirname(image_file), exist_ok=True)
			with open(image_file, "wb") as f:
				f.write(img)
				f.close()

		# Save prompts
		if self.main_window.save_prompts.isChecked():
			prompt_file: str = f"output/prompts/{date}/image_{time}.txt"
			os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
			with open(prompt_file, "w") as f:
				f.write(ujson.dumps(data, indent=4))
				f.close()

		# Create pixmap
		pixmap: QtGui.QPixmap = QtGui.QPixmap()
		pixmap.loadFromData(img)

		# Resize image
		if pixmap.width() > self.main_window.image.width() or pixmap.height() > self.main_window.image.height():
			pixmap = pixmap.scaled(720, 720, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)

		# Display image
		self.main_window.image.setPixmap(pixmap)

		# Delete pixmap
		del pixmap

		# Update status bar
		self.main_window.statusbar.hide()
		# threading.Thread(target=self.main_window.statusbar.hide(), args=()).start()


if __name__ == "__main__":
	app = IMGenAI()
	app.run()
