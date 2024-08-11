import threading, requests, base64, random, sys, os
from PyQt6 import QtCore, QtGui, QtWidgets
from PIL import Image, ImageFilter
from time import sleep
import ujson as json

from window import Ui_MainWindow
from config import Ui_Config_Dialog
from about import Ui_About_Dialog

import license

import configparser

# TODO: config file (config.ini), import configparser


class IMGenAI:
	def __init__(self) -> None:
		self.last_used_seed: int = -1
		self.in_generation_process: bool = False
		self.config_parser = configparser.ConfigParser()
		self.config_parser.read("config.ini")

	def run(self) -> None:
		self.app = QtWidgets.QApplication(sys.argv)
		self.MainWindow = QtWidgets.QMainWindow()
		self.main_window = Ui_MainWindow()
		self.main_window.setupUi(self.MainWindow)
		self.MainWindow.setFixedSize(self.MainWindow.size())
		self.setupMainWindowUI()
		self.MainWindow.show()

		sys.exit(self.app.exec())

	def setupMainWindowUI(self) -> None:
		self.main_window.statusbar.hide()

		# Set icons
		self.main_window.open_file.setIcon(QtGui.QIcon().fromTheme("document-open"))
		self.main_window.save_prompt.setIcon(QtGui.QIcon().fromTheme("document-save"))
		self.main_window.configuration.setIcon(QtGui.QIcon().fromTheme("document-properties"))
		self.main_window.reset_prompt.setIcon(QtGui.QIcon().fromTheme("view-restore"))
		self.main_window.about.setIcon(QtGui.QIcon().fromTheme("help-about"))

		# Configure shortcut keys
		self.main_window.pushButton3.setShortcut(QtGui.QKeySequence("Ctrl+Return"))

		# Configure "File" menu functions
		self.main_window.open_file.triggered.connect(self.openFile)
		self.main_window.save_prompt.triggered.connect(self.savePrompt)

		# Configure "Settings" menu functions
		self.main_window.prompt_sidebar.triggered.connect(self.togglePromptSettingsSidebar)
		self.main_window.image_view_sidebar.triggered.connect(self.toggleImageViewSidebar)
		self.main_window.show_status_bar.triggered.connect(
			lambda: (
				self.main_window.statusbar.show()
				if self.main_window.show_status_bar.isChecked()
				else self.main_window.statusbar.hide()
			)
		)
		self.main_window.configuration.triggered.connect(self.configureWindow)
		self.main_window.reset_prompt.triggered.connect(
			lambda: self.setValues(
				{
					"prompt": "",
					"negative_prompt": "",
					"seed": "-1",
					"sampling_steps": 20,
					"width": 512,
					"height": 512,
					"guidance_scale": 7,
					"num_images": 1,
					"NSFW_content": 0,
				}
			)
		)

		# Configure "Help" menu functions
		self.main_window.about.triggered.connect(self.aboutWindow)

		# Change SpinBox values
		self.main_window.horizontalSlider1.valueChanged.connect(lambda: self.main_window.spinBox1.setValue(self.main_window.horizontalSlider1.value()))
		self.main_window.horizontalSlider2.valueChanged.connect(lambda: self.main_window.spinBox2.setValue(self.main_window.horizontalSlider2.value()))
		self.main_window.horizontalSlider3.valueChanged.connect(lambda: self.main_window.spinBox3.setValue(self.main_window.horizontalSlider3.value()))
		self.main_window.horizontalSlider4.valueChanged.connect(lambda: self.main_window.spinBox4.setValue(self.main_window.horizontalSlider4.value()))
		self.main_window.horizontalSlider5.valueChanged.connect(lambda: self.main_window.spinBox5.setValue(self.main_window.horizontalSlider5.value()))
		self.main_window.horizontalSlider6.valueChanged.connect(lambda: self.main_window.spinBox6.setValue(self.main_window.horizontalSlider6.value()))

		# Change HorizontalSlider values
		self.main_window.spinBox1.valueChanged.connect(lambda: self.main_window.horizontalSlider1.setValue(self.main_window.spinBox1.value()))
		self.main_window.spinBox2.valueChanged.connect(lambda: self.main_window.horizontalSlider2.setValue(self.main_window.spinBox2.value()))
		self.main_window.spinBox3.valueChanged.connect(lambda: self.main_window.horizontalSlider3.setValue(self.main_window.spinBox3.value()))
		self.main_window.spinBox4.valueChanged.connect(lambda: self.main_window.horizontalSlider4.setValue(self.main_window.spinBox4.value()))
		self.main_window.spinBox5.valueChanged.connect(lambda: self.main_window.horizontalSlider5.setValue(self.main_window.spinBox5.value()))
		self.main_window.spinBox6.valueChanged.connect(lambda: self.main_window.horizontalSlider6.setValue(self.main_window.spinBox6.value()))

		# Connect buttons/actions
		self.main_window.pushButton1.clicked.connect(lambda: self.main_window.lineEdit1.setText(str(random.randint(0, 9999_9999_9999_9999))))
		self.main_window.pushButton2.clicked.connect(lambda: self.main_window.lineEdit1.setText("-1"))
		self.main_window.pushButton3.clicked.connect(lambda: threading.Thread(target=self.generate, args=(self.main_window.spinBox6.value(),)).start())
		self.main_window.listWidget1.clicked.connect(lambda: self.imageSelected())

	def imageSelected(self) -> None:
		image_path: str = self.main_window.listWidget1.model().itemData(self.main_window.listWidget1.selectedIndexes()[0])[0]
		self.openImage(image_path)

		try:
			self.setValues(self.getMetadataFromImage(image_path))
		except:
			threading.Thread(target=self.setMainWindowStatusBarText, args=("No prompt data found!", 3, "#FF3333")).start()
			return

	def configureWindow(self) -> None:
		self.ConfigWindow = QtWidgets.QDialog()
		self.config_window = Ui_Config_Dialog()
		self.config_window.setupUi(self.ConfigWindow)
		self.ConfigWindow.setFixedSize(self.ConfigWindow.size())
		self.setupConfigWindowUI()
		self.ConfigWindow.show()

	def setupConfigWindowUI(self) -> None:
		self.hideAndDisableWidgets()

		self.config_window.listView1.setMovement(QtWidgets.QListView.Movement.Static)
		self.config_window.listView1.setModel(QtGui.QStandardItemModel())

		# List of configuration menu items
		self.config_window.listView1.model().appendRow(QtGui.QStandardItem("General"))
		self.config_window.listView1.model().appendRow(QtGui.QStandardItem("Image generation"))
		self.config_window.listView1.model().appendRow(QtGui.QStandardItem("Images and prompts"))
		self.config_window.listView1.model().appendRow(QtGui.QStandardItem("Additional"))

		self.config_window.listView1.clicked.connect(self.changeConfigTab)

	def hideAndDisableWidgets(self) -> None:
		self.config_window.widget1.hide()
		self.config_window.widget1.setEnabled(False)

		self.config_window.widget2.hide()
		self.config_window.widget2.setEnabled(False)

		self.config_window.widget3.hide()
		self.config_window.widget3.setEnabled(False)

		self.config_window.widget4.hide()
		self.config_window.widget4.setEnabled(False)



		# self.createConfigFile()



	def createConfigFile(self):
		...
		config = configparser.ConfigParser()

		# config["General"] = {
		# 	"image_output_dir": "output/images/<date>",
		# 	"prompt_output_dir": "output/prompts/<date>",
		# 	"image_prompt_filename": "image_<time>_<index>",
		# 	"date_format": "dd-MM-yyyy",
		# 	"time_format": "hh-mm-ss",
		# 	"show_status_bar": True,
		# 	"reset_settings": True
		# }

		# config["Image generation"] = {
		# 	"use_custom_model": False,
		# 	"model_id": "",
		# 	"custom_model_id": ""
		# }

		# config["Images and prompts"] = {
		# 	"save_images": True,
		# 	"save_prompts": True,
		# 	"show_prompt_image": True,
		# 	"nsfw_content": False
		# }

		# config["Additional"] = {
		# 	"generate_button_shortcut": "Ctrl+Return",
		# 	"interrupt_button_shortcut": "Ctrl+Shift+Return",
		# 	"save_config_shortcut": "Ctrl+S"
		# }

		# config.write(open("config.ini", "w"))


	def changeConfigTab(self) -> None:
		# TODO: Implement config menu, widgets
		tab_name = self.config_window.listView1.model().itemData(self.config_window.listView1.selectedIndexes()[0])[0]
		
		# Hide and disable widgets
		self.hideAndDisableWidgets()

		# Read and load config
		self.config_parser.read("config.ini")
		self.loadConfig(tab_name)

		# Show and enable widget
		match tab_name:
			case "General":
				self.config_window.widget1.show()
				self.config_window.widget1.setEnabled(True)
			case "Image generation":
				self.config_window.widget2.show()
				self.config_window.widget2.setEnabled(True)
			case "Images and prompts":
				self.config_window.widget3.show()
				self.config_window.widget3.setEnabled(True)
			case "Additional":
				self.config_window.widget4.show()
				self.config_window.widget4.setEnabled(True)


	def loadConfig(self, config_tab) -> None:
		match config_tab:
			case "General":
				self.config_window.lineEdit1_1.setText(self.config_parser.get("General", "image_output_dir").replace("<date>", ""))
				self.config_window.lineEdit1_2.setText(self.config_parser.get("General", "prompt_output_dir").replace("<date>", ""))
				self.config_window.lineEdit1_3.setText(self.config_parser.get("General", "image_prompt_filename"))
				self.config_window.lineEdit1_4.setText(self.config_parser.get("General", "date_format"))
				self.config_window.lineEdit1_5.setText(self.config_parser.get("General", "time_format"))
			case "Image generation":
				self.config_window.lineEdit2_1.setText(self.config_parser.get("Image generation", "model_id"))
			case "Images and prompts":
				self.config_window.checkBox3_1.setChecked(self.config_parser.getboolean("Images and prompts", "save_images"))
				self.config_window.checkBox3_2.setChecked(self.config_parser.getboolean("Images and prompts", "save_prompts"))
				self.config_window.checkBox3_3.setChecked(self.config_parser.getboolean("Images and prompts", "show_prompt_image"))
				self.config_window.checkBox3_4.setChecked(self.config_parser.getboolean("Images and prompts", "nsfw_content"))
			case "Additional":
				self.main_window.pushButton3.setShortcut(QtGui.QKeySequence(self.config_parser.get("Additional", "generate_button_shortcut")))


	def saveConfig(self, config_tab) -> None:
		match config_tab:
			case "General":
				self.config_parser.set("General", "image_output_dir", self.config_window.lineEdit1_1.text())
				self.config_parser.set("General", "prompt_output_dir", self.config_window.lineEdit1_2.text())
				self.config_parser.set("General", "image_prompt_filename", self.config_window.lineEdit1_3.text())
				self.config_parser.set("General", "date_format", self.config_window.lineEdit1_4.text())
				self.config_parser.set("General", "time_format", self.config_window.lineEdit1_5.text())
			case "Image generation":
				self.config_parser.set("Image generation", "model_id", self.config_window.lineEdit2_1.text())
			case "Images and prompts":
				self.config_parser.set("Images and prompts", "save_images", self.config_window.checkBox3_1.isChecked())
				self.config_parser.set("Images and prompts", "save_prompts", self.config_window.checkBox3_2.isChecked())
				self.config_parser.set("Images and prompts", "show_prompt_image", self.config_window.checkBox3_3.isChecked())
				self.config_parser.set("Images and prompts", "nsfw_content", self.config_window.checkBox3_4.isChecked())





	def aboutWindow(self) -> None:
		self.AboutWindow = QtWidgets.QDialog()
		self.about_window = Ui_About_Dialog()
		self.about_window.setupUi(self.AboutWindow)
		self.setupAboutWindowUI()
		self.AboutWindow.show()

	def setupAboutWindowUI(self) -> None:
		self.about_window.textEdit1.setMarkdown(license.text)

	def openImage(self, image_path: str) -> None:
		pixmap: QtGui.QPixmap = QtGui.QPixmap(image_path)

		# Resize image
		if (
			pixmap.width() > self.main_window.image.width()
			or pixmap.height() > self.main_window.image.height()
		):
			pixmap = pixmap.scaled(
				self.main_window.image.width(),
				self.main_window.image.height(),
				QtCore.Qt.AspectRatioMode.KeepAspectRatio,
				QtCore.Qt.TransformationMode.SmoothTransformation,
			)

		self.main_window.image.setPixmap(pixmap)

	def getMetadataFromImage(self, image_path: str) -> None:
		image: Image = Image.open(image_path)
		return Image.open(image_path).text

	def openFile(self) -> None:
		try:
			filename = QtWidgets.QFileDialog().getOpenFileName(
				caption="Open image/prompt file",
				# filter="Image files (*.png);;Text files (*.txt)"
				filter="Image/Text files (*.png *.txt)",
			)

			# If image file
			if filename[0].endswith(".png"):
				data: dict = self.getMetadataFromImage(filename[0])

				if self.main_window.show_image_prompt.isChecked():
					self.openImage(filename[0])

				self.addImageToList(filename[0])

			# If text file
			else:
				with open(filename[0], "r") as f:
					data: dict = json.load(f)
					f.close()

			try:
				self.setValues(data)
				self.last_used_seed = int(data["seed"])
				threading.Thread(target=self.setMainWindowStatusBarText, args=(f"Prompt settings loaded from {filename[0]}", 5, "#5CB85C")).start()
			except:
				threading.Thread(target=self.setMainWindowStatusBarText, args=("No prompt data found!", 3, "#FF3333")).start()
		except:
			...

	def savePrompt(self) -> None:
		try:
			filename = QtWidgets.QFileDialog().getSaveFileName(
				caption="Save prompt file", filter="Text files (*.txt)"
			)

			with open(filename[0], "w") as f:
				data: dict = self.getValues()
				data["seed"] = self.last_used_seed
				f.write(json.dumps(data, indent=4))
				f.close()
		except:
			...

	def togglePromptSettingsSidebar(self) -> None:
		size: QtCore.QSize = self.MainWindow.geometry().size()

		if self.main_window.prompt_sidebar.isChecked():
			self.MainWindow.setFixedSize(size.width() + 260, self.MainWindow.height())
			self.main_window.image.setGeometry(QtCore.QRect(270, 10, 800, 800))
			self.main_window.widget2.setGeometry(QtCore.QRect(1080, 10, 160, 800))
			self.main_window.widget1.setEnabled(True)
			self.main_window.widget1.show()
		else:
			self.MainWindow.setFixedSize(size.width() - 260, self.MainWindow.height())
			self.main_window.image.setGeometry(QtCore.QRect(10, 10, 800, 800))
			self.main_window.widget2.setGeometry(QtCore.QRect(820, 10, 160, 800))
			self.main_window.widget1.setEnabled(False)
			self.main_window.widget1.hide()

	def toggleImageViewSidebar(self) -> None:
		size: QtCore.QSize = self.MainWindow.geometry().size()

		if self.main_window.image_view_sidebar.isChecked():
			self.MainWindow.setFixedSize(size.width() + 168, self.MainWindow.height())
			self.main_window.widget2.setEnabled(True)
			self.main_window.widget2.show()
		else:
			self.MainWindow.setFixedSize(size.width() - 168, self.MainWindow.height())
			self.main_window.widget2.setEnabled(False)
			self.main_window.widget2.hide()

	def getValues(self) -> dict:
		return {
			"prompt": self.main_window.textEdit1.toPlainText(),
			"negative_prompt": self.main_window.textEdit2.toPlainText(),
			"seed": int(self.main_window.lineEdit1.text()),
			"sampling_steps": self.main_window.spinBox1.value(),
			"width": self.main_window.spinBox2.value(),
			"height": self.main_window.spinBox3.value(),
			"guidance_scale": self.main_window.spinBox4.value(),
			"num_images": self.main_window.spinBox5.value(),
			"NSFW_content": int(self.main_window.NSFW_content.isChecked()),
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
			self.main_window.spinBox5.setValue(int(data["num_images"]))
		except:
			self.main_window.spinBox5.setValue(1)

		try:
			self.main_window.NSFW_content.setChecked(data["NSFW_content"])
		except:
			self.main_window.NSFW_content.setChecked(False)

	def setMainWindowStatusBarText(self, text: str, time: int = 2, color: str = "#000000", keep: bool = False) -> None:
		self.MainWindow.statusBar().showMessage(text)
		self.MainWindow.statusBar().setStyleSheet(f"color: {color};")
		self.main_window.statusbar.show()
		sleep(time)
		self.main_window.statusbar.hide() if keep == False else ...

	def imageRequest(self, url: str, data: dict) -> tuple:
		# Update status bar
		threading.Thread(target=self.setMainWindowStatusBarText, args=("Generating image(s)...", 2, "#5CB85C", True)).start()

		# get response from server
		if self.in_generation_process == True:
			try:
				response: requests.Response = requests.post(url, data)
				response_data: dict = json.loads(response.content)
			except Exception as e:
				threading.Thread(target=self.setMainWindowStatusBarText, args=(f"{e}", 2, "#FF3333")).start()
				return
		else:
			threading.Thread(target=self.setMainWindowStatusBarText, args=("Image generation interrupted", 2, "#FF3333")).start()
			return

		# Final result
		if self.in_generation_process == True:
			final_image: bytes = base64.b64decode(response_data["final"])
		else:
			threading.Thread(target=self.setMainWindowStatusBarText, args=(f"Image generation interrupted", 2, "#FF3333")).start()
			return

		# Try to get all images
		if self.in_generation_process == True:
			try:
				all_images: list = [base64.b64decode(image) for image in response_data["images"]]
			except:
				all_images: list = None
		else:
			threading.Thread(target=self.setMainWindowStatusBarText, args=(f"Image generation interrupted", 2, "#FF3333")).start()
			return

		# Update status bar
		threading.Thread(target=self.setMainWindowStatusBarText, args=(f"Image(s) generated successfully!", 2, "#5CB85C")).start()

		return final_image, all_images

	def saveImagesAndPrompts(self, data, final, all) -> None:
		# Get date and time
		date: str = QtCore.QDate.currentDate().toString("dd-MM-yyyy")
		time: str = QtCore.QTime.currentTime().toString("hh-mm-ss")

		# Save images
		if self.main_window.save_images.isChecked():
			# Final image
			if final != None:
				image_file: str = f"output/images/{date}/image_{time}_0.png"
				os.makedirs(os.path.dirname(image_file), exist_ok=True)
				open(image_file, "wb").write(final)
				self.addImageToList(image_file)

			# All images
			if all != None:
				for i, image in enumerate(all):
					image_file: str = f"output/images/{date}/image_{time}_{i+1}.png"
					os.makedirs(os.path.dirname(image_file), exist_ok=True)
					open(image_file, "wb").write(image)
					self.addImageToList(image_file)

		# Save prompts
		if self.main_window.save_prompts.isChecked():
			# Final image
			if final != None:
				prompt_file: str = f"output/prompts/{date}/image_{time}_0.txt"
				os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
				open(prompt_file, "w").write(json.dumps(data, indent=4))

			# All images
			if all != None:
				for i, image in enumerate(all):
					prompt_file: str = f"output/prompts/{date}/image_{time}_{i+1}.txt"
					os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
					open(prompt_file, "w").write(json.dumps(data, indent=4))

	def addImageToList(self, image_path) -> None:
		pixmap: QtGui.QPixmap = QtGui.QPixmap(image_path)
		pixmap = pixmap.scaledToWidth(
			self.main_window.listWidget1.iconSize().width(),
			QtCore.Qt.TransformationMode.SmoothTransformation,
		)
		icon: QtGui.QIcon = QtGui.QIcon(pixmap)
		item: QtWidgets.QListWidgetItem = QtWidgets.QListWidgetItem(icon, image_path)
		self.main_window.listWidget1.addItem(item)

	def generate(self, batch_count) -> None:
		if self.in_generation_process == True:
			self.in_generation_process = False
			self.main_window.pushButton3.setText("Generate (Ctrl + Return)")
			self.main_window.pushButton3.setShortcut(QtGui.QKeySequence("Ctrl+Return"))
			return

		# Update generation status
		self.in_generation_process = True

		if self.in_generation_process == True:
			# Get url and prompt data
			url: str = self.main_window.lineEdit2.text()
			data: dict = self.getValues()

			# Update last used seed
			global last_used_seed
			last_used_seed = int(data["seed"])

			# Check if seed is random
			random_seed: bool = data["seed"] == -1

			# Update generation button
			self.main_window.pushButton3.setText("Interrupt (Ctrl + Shift + Return)")
			self.main_window.pushButton3.setShortcut(QtGui.QKeySequence("Ctrl+Shift+Return"))

		else:
			threading.Thread(target=self.setMainWindowStatusBarText, args=("Image generation interrupted!", 2, "#FF3333")).start()
			return

		if self.in_generation_process == True:
			for _ in range(batch_count):
				# Randomize seed
				if self.in_generation_process == True:
					data["seed"] = (
						random.randint(0, 9999_9999_9999_9999)
						if random_seed == True
						else data["seed"]
					)
				else:
					threading.Thread(target=self.setMainWindowStatusBarText,args=("Image generation interrupted!", 2, "#FF3333")).start()
					return

				# POST request
				if self.in_generation_process == True:
					try:
						final_image, all_images = self.imageRequest(url, data)
					except Exception as e:
						self.in_generation_process = False
						self.main_window.pushButton3.setText("Generate (Ctrl + Return)")
						self.main_window.pushButton3.setShortcut(
							QtGui.QKeySequence("Ctrl+Return")
						)
						return
				else:
					threading.Thread(target=self.setMainWindowStatusBarText,args=("Image generation interrupted!", 2, "#FF3333")).start()
					return

				# Save images and prompts
				if self.in_generation_process == True:
					if final_image != None:
						self.saveImagesAndPrompts(data, final_image, all_images)
				else:
					threading.Thread(target=self.setMainWindowStatusBarText,args=("Image generation interrupted!", 2, "#FF3333"),).start()
					self.in_generation_process = False
					self.main_window.pushButton3.setText("Generate (Ctrl + Return)")
					self.main_window.pushButton3.setShortcut(QtGui.QKeySequence("Ctrl+Return"))
					return

				# Create pixmap
				pixmap: QtGui.QPixmap = QtGui.QPixmap()
				pixmap.loadFromData(final_image)

				# Resize image
				if (
					pixmap.width() > self.main_window.image.width()
					or pixmap.height() > self.main_window.image.height()
				):
					pixmap = pixmap.scaled(
						self.main_window.image.width(),
						self.main_window.image.height(),
						QtCore.Qt.AspectRatioMode.KeepAspectRatio,
						QtCore.Qt.TransformationMode.SmoothTransformation,
					)

				# Display image
				self.main_window.image.setPixmap(pixmap)
		else:
			threading.Thread(target=self.setMainWindowStatusBarText, args=("Image generation interrupted!", 2, "#FF3333")).start()
			return

		self.in_generation_process = False
		self.main_window.pushButton3.setText("Generate (Ctrl + Return)")
		self.main_window.pushButton3.setShortcut(QtGui.QKeySequence("Ctrl+Return"))


if __name__ == "__main__":
	os.system("cls")
	app = IMGenAI()
	app.run()
