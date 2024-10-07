"""
Copyright (c) 2024, Oderline
All rights reserved.

This project is based in part on the work of the following projects:

	- PyQt (https://www.riverbankcomputing.com/software/pyqt).
	- Diffusers (https://huggingface.co/spaces/huggingface/diffusers).
	- Pillow (fork of PIL) (https://pillow.readthedocs.io/en/stable).
	- and others.

These projects are licensed under their respective licenses.
You can find more information about these licenses at:

	- GPLv3: https://www.gnu.org/licenses/gpl-3.0.
	- Apache-2.0: https://www.apache.org/licenses/LICENSE-2.0.
	- PIL License: https://github.com/python-pillow/Pillow/blob/main/LICENSE.
	- MIT License: https://mit-license.org.

This project is licensed under MIT License. See the LICENSE file for details.

Permission is granted to use, copy, modify, and distribute this software
while comply the license agreements of the respective projects.
"""


# from PIL import Image, ImageFilter

import threading, requests, base64, random, sys, os
from PyQt6 import QtCore, QtGui, QtWidgets
from time import sleep
from PIL import Image
import ujson as json
import configparser
import platform

from window import Ui_MainWindow
from config import Ui_Config_Dialog
from about import Ui_About_Dialog


class IMGenAI:
	def __init__(self) -> None:
		self.last_used_seed: int = -1
		self.in_generation_process: bool = False

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
		self.checkIfConfigFileExist()
		config = configparser.ConfigParser()
		config.read("config.ini")

		# Change window height when statusbar is shown
		if config.getboolean("General", "show_status_bar"):
			self.MainWindow.setFixedHeight(862)
			self.main_window.statusbar.show()
		else:
			self.MainWindow.setFixedHeight(841)
			self.main_window.statusbar.hide()

		# Set icons
		self.main_window.open_file.setIcon(QtGui.QIcon().fromTheme("document-open"))
		self.main_window.save_prompt.setIcon(QtGui.QIcon().fromTheme("document-save"))
		self.main_window.configuration.setIcon(QtGui.QIcon().fromTheme("document-properties"))
		self.main_window.reset_prompt.setIcon(QtGui.QIcon().fromTheme("view-restore"))
		self.main_window.about.setIcon(QtGui.QIcon().fromTheme("help-about"))

		# Set shortcut keys
		self.setGenerateButtonTextAndShortcut("generate")

		# Configure "File" menu functions
		self.main_window.open_file.triggered.connect(self.openFile)
		self.main_window.save_prompt.triggered.connect(self.savePromptDataToFile)

		# Configure "Settings" menu functions
		self.main_window.prompt_sidebar.triggered.connect(self.togglePromptSettingsSidebar)
		self.main_window.image_view_sidebar.triggered.connect(self.toggleImageViewSidebar)
		self.main_window.configuration.triggered.connect(self.configWindow)
		self.main_window.reset_prompt.triggered.connect(
			lambda: self.setPromptData(
				{
					"prompt": "",
					"negative_prompt": "",
					"seed": "-1",
					"sampling_steps": 20,
					"width": 512,
					"height": 512,
					"guidance_scale": 7,
					"num_images": 1,
				},
				batch_count=1
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
		self.main_window.pushButton3.clicked.connect(
			lambda: threading.Thread(
				target=self.generateImage,
				args=(
					self.main_window.spinBox6.value(),
				)
			).start()
		)
		self.main_window.listWidget1.clicked.connect(lambda: self.imageSelected())


	def addImageToList(self, image_path) -> None:
		pixmap: QtGui.QPixmap = QtGui.QPixmap(image_path)
		pixmap = pixmap.scaledToWidth(
			self.main_window.listWidget1.iconSize().width(),
			QtCore.Qt.TransformationMode.SmoothTransformation,
		)
		icon: QtGui.QIcon = QtGui.QIcon(pixmap)
		item: QtWidgets.QListWidgetItem = QtWidgets.QListWidgetItem(icon, image_path)
		self.main_window.listWidget1.addItem(item)


	def generateImage(self, batch_count) -> None:
		if self.in_generation_process == True:
			self.checkIfConfigFileExist()
			self.setGenerateButtonTextAndShortcut("generate")
			self.in_generation_process = False
			return

		# Update generation status
		self.in_generation_process = True

		if self.in_generation_process == True:
			# Get url and prompt data
			url: str = self.main_window.lineEdit2.text()
			data: dict = self.getPromptData()

			# Update last used seed
			global last_used_seed
			last_used_seed = int(data["seed"])

			# Check if seed is random
			random_seed: bool = data["seed"] == -1

			# Update generation button
			self.checkIfConfigFileExist()
			self.setGenerateButtonTextAndShortcut("interrupt")
		else:
			threading.Thread(
				target=self.setMainWindowStatusBarText,
				args=("Image generation interrupted!", 2, "#FF3333")
			).start()
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
					threading.Thread(
						target=self.setMainWindowStatusBarText,
						args=("Image generation interrupted!", 2, "#FF3333")
					).start()
					return

				# POST request
				if self.in_generation_process == True:
					try:
						final_image, all_images = self.imageRequest(url, data)
					except Exception as e:
						self.in_generation_process = False
						self.checkIfConfigFileExist()
						self.setGenerateButtonTextAndShortcut("generate")
						return
				else:
					threading.Thread(
						target=self.setMainWindowStatusBarText,
						args=("Image generation interrupted!", 2, "#FF3333")
					).start()
					return

				# Save images and prompts
				if self.in_generation_process == True:
					if final_image != None:
						self.saveImagesAndPrompts(data, final_image, all_images)
				else:
					threading.Thread(
						target=self.setMainWindowStatusBarText,
						args=("Image generation interrupted!", 2, "#FF3333")
					).start()
					self.in_generation_process = False
					self.checkIfConfigFileExist()
					self.setGenerateButtonTextAndShortcut("generate")
					return

				# Create pixmap
				pixmap: QtGui.QPixmap = QtGui.QPixmap()
				pixmap.loadFromData(final_image)

				# Resize image
				if (pixmap.width() > self.main_window.image.width() or pixmap.height() > self.main_window.image.height()):
					pixmap = pixmap.scaled(
						self.main_window.image.width(),
						self.main_window.image.height(),
						QtCore.Qt.AspectRatioMode.KeepAspectRatio,
						QtCore.Qt.TransformationMode.SmoothTransformation
					)

				# Display image
				self.main_window.image.setPixmap(pixmap)
		else:
			threading.Thread(
				target=self.setMainWindowStatusBarText,
				args=("Image generation interrupted!", 2, "#FF3333")
			).start()
			return

		self.in_generation_process = False
		self.main_window.pushButton3.setText("Generate (Ctrl + Return)")
		self.main_window.pushButton3.setShortcut(QtGui.QKeySequence("Ctrl+Return"))


	def getMetadataFromImage(self, image_path: str) -> None:
		image: Image = Image.open(image_path)
		return Image.open(image_path).text


	def getPromptData(self) -> dict:
		self.checkIfConfigFileExist()
		config = configparser.ConfigParser()
		config.read("config.ini")
		return {
			"prompt": self.main_window.textEdit1.toPlainText(),
			"negative_prompt": self.main_window.textEdit2.toPlainText(),
			"seed": int(self.main_window.lineEdit1.text()),
			"sampling_steps": self.main_window.spinBox1.value(),
			"width": self.main_window.spinBox2.value(),
			"height": self.main_window.spinBox3.value(),
			"guidance_scale": self.main_window.spinBox4.value(),
			"num_images": self.main_window.spinBox5.value(),
			"nsfw_content": config.get("Images and prompts", "nsfw_content")
		}


	def imageRequest(self, url: str, data: dict) -> tuple:
		# Update status bar
		threading.Thread(
			target=self.setMainWindowStatusBarText,
			args=("Generating image(s)...", 2, "#5CB85C", True)
		).start()

		# get response from server
		if self.in_generation_process == True:
			try:
				response: requests.Response = requests.post(url=url, data=data, timeout=None)
				response_data: dict = json.loads(response.content)
			except Exception as e:
				threading.Thread(
					target=self.setMainWindowStatusBarText,
					args=(f"{e}", 2, "#FF3333")
				).start()
				return
		else:
			threading.Thread(
				target=self.setMainWindowStatusBarText,
				args=("Image generation interrupted", 2, "#FF3333")
			).start()
			return

		# Final result
		if self.in_generation_process == True:
			final_image: bytes = base64.b64decode(response_data["final"])
		else:
			threading.Thread(
				target=self.setMainWindowStatusBarText,
				args=(f"Image generation interrupted", 2, "#FF3333")
			).start()
			return

		# Try to get all images
		if self.in_generation_process == True:
			try:
				all_images: list = [base64.b64decode(image) for image in response_data["images"]]
			except:
				all_images: list = None
		else:
			threading.Thread(
				target=self.setMainWindowStatusBarText,
				args=(f"Image generation interrupted", 2, "#FF3333")
			).start()
			return

		# Update status bar
		threading.Thread(
			target=self.setMainWindowStatusBarText,
			args=(f"Image(s) generated successfully!", 2, "#5CB85C")
		).start()

		return final_image, all_images


	def imageSelected(self) -> None:
		image_path: str = self.main_window.listWidget1.model() \
			.itemData(self.main_window.listWidget1.selectedIndexes()[0])[0]
		self.openImage(image_path)

		try:
			data = self.getMetadataFromImage(image_path)
			self.setPromptData(data)
			self.last_used_seed = data["seed"]
		except:
			threading.Thread(
				target=self.setMainWindowStatusBarText,
				args=("No prompt data found!", 3, "#FF3333")
			).start()
			return


	def openFile(self) -> None:
		try:
			filename = QtWidgets.QFileDialog().getOpenFileName(
				caption="Open image/prompt file",
				filter="Image/Text files (*.png *.txt)"
			)

			# If image file
			if filename[0].endswith(".png"):
				data: dict = self.getMetadataFromImage(filename[0])

				config = configparser.ConfigParser()
				config.read("config.ini")

				if config.getboolean("Images and prompts", "show_prompt_image") == True:
					self.openImage(filename[0])

				self.addImageToList(filename[0])

			# If text file
			else:
				with open(filename[0], "r") as f:
					data: dict = json.load(f)
					f.close()

			try:
				self.setPromptData(data)
				self.last_used_seed = int(data["seed"])
				threading.Thread(
					target=self.setMainWindowStatusBarText,
					args=(f"Prompt settings loaded from {filename[0]}", 5, "#5CB85C")
				).start()
			except:
				threading.Thread(
					target=self.setMainWindowStatusBarText,
					args=("No prompt data found!", 3, "#FF3333")
				).start()
		except:
			...


	def openImage(self, image_path: str) -> None:
		pixmap: QtGui.QPixmap = QtGui.QPixmap(image_path)

		# Resize image
		if (pixmap.width() > self.main_window.image.width() or pixmap.height() > self.main_window.image.height()):
			pixmap = pixmap.scaled(
				self.main_window.image.width(),
				self.main_window.image.height(),
				QtCore.Qt.AspectRatioMode.KeepAspectRatio,
				QtCore.Qt.TransformationMode.SmoothTransformation,
			)

		self.main_window.image.setPixmap(pixmap)
		data = self.getPromptData()


	def saveImagesAndPrompts(self, data, final, all) -> None:
		# Get config
		config = configparser.ConfigParser()
		config.read("config.ini")

		# Get date and time
		date: str = QtCore.QDate.currentDate().toString(config.get("General", "date_format"))
		time: str = QtCore.QTime.currentTime().toString(config.get("General", "time_format"))

		# Save images
		if config.getboolean("Images and prompts", "save_images") == True:
			# Final image
			if final != None:
				image_file: str = f"{
					config.get('General', 'image_output_dir')
						.replace("$date", date)
						.replace("$time", time)
					}/{
						config.get('General', 'image_prompt_filename')
							.replace("$date", date)
							.replace("$time", time)
							.replace("$index", "0")
					}.png"
				os.makedirs(os.path.dirname(image_file), exist_ok=True)
				open(image_file, "wb").write(final)
				self.addImageToList(image_file)

			# All images
			if all != None:
				for i, image in enumerate(all):
					image_file: str = f"{
						config.get('General', 'image_output_dir')
							.replace("$date", date)
							.replace("$time", time)
						}/{
							config.get('General', 'image_prompt_filename')
								.replace("$date", date)
								.replace("$time", time)
								.replace("$index", str(i+1))
						}.png"
					os.makedirs(os.path.dirname(image_file), exist_ok=True)
					open(image_file, "wb").write(image)
					self.addImageToList(image_file)

		# Save prompts
		if config.getboolean("Images and prompts", "save_prompts") == True:
			# Final image
			if final != None:
				prompt_file: str = f"{
					config.get('General', 'prompt_output_dir')
						.replace("$date", date)
						.replace("$time", time)
					}/{
						config.get('General', 'image_prompt_filename')
							.replace("$date", date)
							.replace("$time", time)
							.replace("$index", "0")
					}.txt"
				os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
				open(prompt_file, "w").write(json.dumps(data, indent=4))

			# All images
			if all != None:
				for i, image in enumerate(all):
					prompt_file: str = f"{
						config.get('General', 'prompt_output_dir')
							.replace("$date", date)
							.replace("$time", time)
						}/{
							config.get('General', 'image_prompt_filename')
								.replace("$date", date)
								.replace("$time", time)
								.replace("$index", str(i+1))
						}.txt"
					os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
					open(prompt_file, "w").write(json.dumps(data, indent=4))


	def savePromptDataToFile(self) -> None:
		try:
			filename = QtWidgets.QFileDialog().getSaveFileName(
				caption="Save prompt file", filter="Text files (*.txt)"
			)

			with open(filename[0], "w") as f:
				data: dict = self.getPromptData()
				data["seed"] = self.last_used_seed
				f.write(json.dumps(data, indent=4))
				f.close()
		except:
			...


	def setGenerateButtonTextAndShortcut(self, type: str) -> None:
		self.checkIfConfigFileExist()
		config = configparser.ConfigParser()
		config.read("config.ini")

		text = f"Generate ({config.get('Additional', 'generate_button_shortcut')})" if type == "generate" \
			else f"Interrupt ({config.get('Additional', 'interrupt_button_shortcut')})"

		shortcut = config.get('Additional', 'generate_button_shortcut') if type == "generate" \
			else config.get('Additional', 'interrupt_button_shortcut')

		self.main_window.pushButton3.setText(text)
		self.main_window.pushButton3.setShortcut(shortcut)


	def setMainWindowStatusBarText(self, text: str, time: int = 2, color: str = "#000000", keep: bool = False) -> None:
		self.checkIfConfigFileExist()
		config = configparser.ConfigParser()
		config.read("config.ini")

		self.MainWindow.statusBar().showMessage(text)
		self.MainWindow.statusBar().setStyleSheet(f"color: {color};")
		self.main_window.statusbar.show() \
			if config.getboolean("General", "show_status_bar") == True \
			else self.main_window.statusbar.hide()
		sleep(time)
		self.main_window.statusbar.hide() if keep == False else ...


	def setPromptData(self, data: dict, batch_count=1) -> None:
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

		self.main_window.spinBox6.setValue(batch_count)


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


	def configWindow(self) -> None:
		self.ConfigWindow = QtWidgets.QDialog()
		self.config_window = Ui_Config_Dialog()
		self.config_window.setupUi(self.ConfigWindow)
		self.ConfigWindow.setFixedSize(self.ConfigWindow.size())
		self.setupConfigWindowUI()
		self.ConfigWindow.show()


	def setupConfigWindowUI(self) -> None:
		self.hideAndDisableWidgets()

		self.checkIfConfigFileExist()
		config = configparser.ConfigParser()
		config.read("config.ini")

		# Connect buttons
		self.config_window.pushButton2_1.clicked.connect(
			lambda: threading.Thread(
				target=self.setDiffusionModel,
				args=()
			).start()
		)
		self.config_window.save_button.clicked.connect(self.saveConfig)

		# Set save shortcut
		self.config_window.save_button.setShortcut(QtGui.QKeySequence(config.get("Additional", "save_config_shortcut")))

		self.config_window.listView1.setMovement(QtWidgets.QListView.Movement.Static)
		self.config_window.listView1.setModel(QtGui.QStandardItemModel())

		# List of configuration window items
		self.config_window.listView1.model().appendRow(QtGui.QStandardItem("General"))
		self.config_window.listView1.model().appendRow(QtGui.QStandardItem("Image generation"))
		self.config_window.listView1.model().appendRow(QtGui.QStandardItem("Images and prompts"))
		self.config_window.listView1.model().appendRow(QtGui.QStandardItem("Additional"))

		self.config_window.listView1.clicked.connect(self.changeConfigTab)


	def checkIfConfigFileExist(self) -> None:
		# Try to open 'config.ini' file
		try:
			config = configparser.ConfigParser()
			config.read("config.ini")
			# Try to get a setting
			config.get("General", "image_output_dir")
		except:
			# Config file not found, create new one
			config = configparser.ConfigParser()
			config.read("config.ini")

			config["General"] = {
				"image_output_dir": "output/images/$date",
				"prompt_output_dir": "output/prompts/$date",
				"image_prompt_filename": "image_$time_$index",
				"date_format": "dd-MM-yyyy",
				"time_format": "hh-mm-ss",
				"show_status_bar": True,
			}
			config["Image generation"] = {"model_id": "runwayml/stable-diffusion-v1-5"}
			config["Images and prompts"] = {
				"save_images": True,
				"save_prompts": True,
				"show_prompt_image": True,
				"nsfw_content": False,
			}
			config["Additional"] = {
				"generate_button_shortcut": "Ctrl+Return",
				"interrupt_button_shortcut": "Ctrl+Shift+Return",
				"save_config_shortcut": "Ctrl+S",
			}

			# Save config
			config.write(open("config.ini", "w"))
			threading.Thread(
				target=self.setConfigStatusbarText,
				args=("Config file created!", 2, "#5CB85C")
			).start()


	def changeConfigTab(self) -> None:
		tab_name = self.config_window.listView1.model() \
			.itemData(self.config_window.listView1.selectedIndexes()[0])[0]
		
		# Hide and disable widgets
		self.hideAndDisableWidgets()

		# Load config from file
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


	def hideAndDisableWidgets(self) -> None:
		self.config_window.widget1.hide()
		self.config_window.widget1.setEnabled(False)
		self.config_window.widget2.hide()
		self.config_window.widget2.setEnabled(False)
		self.config_window.widget3.hide()
		self.config_window.widget3.setEnabled(False)
		self.config_window.widget4.hide()
		self.config_window.widget4.setEnabled(False)


	def loadConfig(self, config_tab) -> None:
		self.checkIfConfigFileExist()
		config = configparser.ConfigParser()
		config.read("config.ini")

		# General
		self.config_window.lineEdit1_1.setText(config.get("General", "image_output_dir"))
		self.config_window.lineEdit1_2.setText(config.get("General", "prompt_output_dir"))
		self.config_window.lineEdit1_3.setText(config.get("General", "image_prompt_filename"))
		self.config_window.lineEdit1_4.setText(config.get("General", "date_format"))
		self.config_window.lineEdit1_5.setText(config.get("General", "time_format"))
		self.config_window.checkBox1_1.setChecked(config.getboolean("General", "show_status_bar"))

		# Image generation
		self.config_window.lineEdit2_2.setText(config.get("Image generation", "model_id"))

		# Images and prompts
		self.config_window.checkBox3_1.setChecked(config.getboolean("Images and prompts", "save_images"))
		self.config_window.checkBox3_2.setChecked(config.getboolean("Images and prompts", "save_prompts"))
		self.config_window.checkBox3_3.setChecked(config.getboolean("Images and prompts", "show_prompt_image"))
		self.config_window.checkBox3_4.setChecked(config.getboolean("Images and prompts", "nsfw_content"))

		# Additional
		self.config_window.keySequenceEdit4_1.setKeySequence(QtGui.QKeySequence(config.get("Additional", "generate_button_shortcut")))
		self.config_window.keySequenceEdit4_2.setKeySequence(QtGui.QKeySequence(config.get("Additional", "interrupt_button_shortcut")))
		self.config_window.keySequenceEdit4_3.setKeySequence(QtGui.QKeySequence(config.get("Additional", "save_config_shortcut")))


	def saveConfig(self) -> None:
		config = configparser.ConfigParser()
		config.read("config.ini")

		# General
		config.set("General", "image_output_dir", self.config_window.lineEdit1_1.text())
		config.set("General", "prompt_output_dir", self.config_window.lineEdit1_2.text())
		config.set("General", "image_prompt_filename", self.config_window.lineEdit1_3.text())
		config.set("General", "date_format", self.config_window.lineEdit1_4.text())
		config.set("General", "time_format", self.config_window.lineEdit1_5.text())
		config.set("General", "show_status_bar", str(self.config_window.checkBox1_1.isChecked()))

		# Image generation
		config.set("Image generation", "model_id", self.config_window.lineEdit2_2.text())

		# Images and prompts
		config.set("Images and prompts", "save_images", str(self.config_window.checkBox3_1.isChecked()))
		config.set("Images and prompts", "save_prompts", str(self.config_window.checkBox3_2.isChecked()))
		config.set("Images and prompts", "show_prompt_image", str(self.config_window.checkBox3_3.isChecked()))
		config.set("Images and prompts", "nsfw_content", str(self.config_window.checkBox3_4.isChecked()))

		# Additional
		config.set("Additional", "generate_button_shortcut", self.config_window.keySequenceEdit4_1.keySequence().toString())
		config.set("Additional", "interrupt_button_shortcut", self.config_window.keySequenceEdit4_2.keySequence().toString())
		config.set("Additional", "save_config_shortcut", self.config_window.keySequenceEdit4_3.keySequence().toString())

		# Change window height when statusbar is shown
		if config.getboolean("General", "show_status_bar"):
			self.MainWindow.setFixedHeight(862)
			self.main_window.statusbar.show()
		else:
			self.MainWindow.setFixedHeight(841)
			self.main_window.statusbar.hide()

		# Set shortcuts and text
		self.main_window.pushButton3.setText(f"Generate ({config.get("Additional", "generate_button_shortcut")})")
		self.main_window.pushButton3.setShortcut(QtGui.QKeySequence(config.get("Additional", "generate_button_shortcut")))
		self.config_window.save_button.setShortcut(QtGui.QKeySequence(config.get("Additional", "save_config_shortcut")))

		# Save config
		config.write(open("config.ini", "w"))
		threading.Thread(
			target=self.setConfigStatusbarText,
			args=("Config file saved!", 2, "#5CB85C")
		).start()


	def setConfigStatusbarText(self, text: str, time: int = 2, color: str = "#000000", keep: bool = False) -> None:
		self.config_window.label_statusbar.setText(text)
		self.config_window.label_statusbar.setStyleSheet(f"color: {color};")
		self.config_window.label_statusbar.show()
		sleep(time)
		self.config_window.label_statusbar.hide() if keep == False else ...


	def setDiffusionModel(self) -> None:
		threading.Thread(
			target=self.setConfigStatusbarText,
			args=("Applying model...", 2, "#5CB85C", True)
		).start()

		url = self.config_window.lineEdit2_1.text()
		model_id = self.config_window.lineEdit2_2 \
			.text().replace(" ", "") \
			.replace("\"", "")

		try:
			response = requests.post(f"{url}/setmodel", {"model_id": model_id}).content
			if bool(response["same_model"]) == True:
				threading.Thread(
					target=self.setConfigStatusbarText,
					args=("This model already set!", 2, "#FF3333")
				).start()
				return
			else:
				threading.Thread(
					target=self.setConfigStatusbarText,
					args=(f"Model {response["model_id"]} applied successfully!", 2, "#5CB85C")
				).start()
		except Exception as e:
			threading.Thread(
				target=self.setConfigStatusbarText,
				args=(f"{e}", 2, "#FF3333")
			).start()
			return


	def aboutWindow(self) -> None:
		self.AboutWindow = QtWidgets.QDialog()
		self.about_window = Ui_About_Dialog()
		self.about_window.setupUi(self.AboutWindow)
		self.AboutWindow.show()


if __name__ == "__main__":
	try:
		os.system("cls") if platform.system() == "Windows" \
			else os.system("clear") if platform.system() == "Linux" \
			else ...

		app = IMGenAI()
		app.run()
	except Exception as e:
		print("Error while running program:", e)
