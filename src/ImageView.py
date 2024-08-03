import PyQt6.QtWidgets
import PyQt6.QtCore
import PyQt6.QtGui

from PIL.PngImagePlugin import PngInfo
from PIL import Image


class ImageView(PyQt6.QtWidgets.QLabel):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setGeometry(PyQt6.QtCore.QRect(0, 0, 512, 512))
		self.setAcceptDrops(True)

	def getMetadata(self, image_path):
		try:
			# Get metadata
			image = Image.open(image_path)
			metadata = PngInfo()
			print(image.text)

			# Set values
			
		except Exception as e:
			print(e)
			return

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
		else:
			event.ignore()

	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
			self.pixmap = PyQt6.QtGui.QPixmap(event.mimeData().urls()[0].toLocalFile())
			self.pixmap = self.pixmap.scaled(720, 720, PyQt6.QtCore.Qt.AspectRatioMode.KeepAspectRatio, PyQt6.QtCore.Qt.TransformationMode.SmoothTransformation)
			self.setPixmap(self.pixmap)
			self.getMetadata(event.mimeData().urls()[0].toLocalFile())
		else:
			event.ignore()
