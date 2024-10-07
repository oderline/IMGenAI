# Form implementation generated from reading ui file 'IMGenAI\src\ui\about.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_About_Dialog(object):
    def setupUi(self, About_Dialog):
        About_Dialog.setObjectName("About_Dialog")
        About_Dialog.setEnabled(True)
        About_Dialog.resize(460, 420)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(About_Dialog.sizePolicy().hasHeightForWidth())
        About_Dialog.setSizePolicy(sizePolicy)
        self.textEdit1 = QtWidgets.QTextEdit(parent=About_Dialog)
        self.textEdit1.setGeometry(QtCore.QRect(0, 0, 460, 420))
        self.textEdit1.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.textEdit1.setReadOnly(True)
        self.textEdit1.setObjectName("textEdit1")

        self.retranslateUi(About_Dialog)
        QtCore.QMetaObject.connectSlotsByName(About_Dialog)

    def retranslateUi(self, About_Dialog):
        _translate = QtCore.QCoreApplication.translate
        About_Dialog.setWindowTitle(_translate("About_Dialog", "About IMGenAI"))
        self.textEdit1.setHtml(_translate("About_Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:\'Segoe UI\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">IMGenAI</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Open source client-server diffusers-based Text2Img generation application.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Version: 0.4, 06.10.2024</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Copyright (c) 2024, Oderline</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">All rights reserved.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">This project is based in part on the work of the following projects:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">    - PyQt (</span><a href=\"https://www.riverbankcomputing.com/software/pyqt\"><span style=\" text-decoration: underline; color:#0078d7;\">https://www.riverbankcomputing.com/software/pyqt</span></a><span style=\" font-size:10pt;\">).</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">    - Diffusers (</span><a href=\"https://huggingface.co/spaces/huggingface/diffusers\"><span style=\" text-decoration: underline; color:#0078d7;\">https://huggingface.co/spaces/huggingface/diffusers</span></a><span style=\" font-size:10pt;\">).</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">    - Pillow (fork of PIL) (</span><a href=\"https://pillow.readthedocs.io/en/stable\"><span style=\" text-decoration: underline; color:#0078d7;\">https://pillow.readthedocs.io/en/stable</span></a><span style=\" font-size:10pt;\">).</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">    - and others.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">These projects are licensed under their respective licenses.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">You can find more information about these licenses at:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">    - GPLv3: </span><a href=\"https://www.gnu.org/licenses/gpl-3.0\"><span style=\" text-decoration: underline; color:#0078d7;\">https://www.gnu.org/licenses/gpl-3.0</span></a><span style=\" font-size:10pt;\">.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">    - Apache-2.0: </span><a href=\"https://www.apache.org/licenses/LICENSE-2.0\"><span style=\" text-decoration: underline; color:#0078d7;\">https://www.apache.org/licenses/LICENSE-2.0</span></a><span style=\" font-size:10pt;\">.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">    - PIL License: </span><a href=\"https://github.com/python-pillow/Pillow/blob/main/LICENS\"><span style=\" text-decoration: underline; color:#0078d7;\">https://github.com/python-pillow/Pillow/blob/main/LICENS</span></a><span style=\" font-size:10pt;\">.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">    - MIT License: </span><a href=\"https://mit-license.org\"><span style=\" text-decoration: underline; color:#0078d7;\">https://mit-license.org</span></a><span style=\" font-size:10pt;\">.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">This project is licensed under MIT License. See the LICENSE file for details. Permission is granted to use, copy, modify, and distribute this software while comply the license agreements of the respective projects.</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    About_Dialog = QtWidgets.QDialog()
    ui = Ui_About_Dialog()
    ui.setupUi(About_Dialog)
    About_Dialog.show()
    sys.exit(app.exec())
