#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 00:02:19 2018

@author: wuxiaobai24
"""


import sys
import os
import time

from PyQt5.QtWidgets import (QApplication, QWidget, QDialog, QMessageBox, QErrorMessage,
                             QPushButton, QToolTip, QMainWindow)
from PyQt5 import QtGui
from PyQt5.QtCore import QCoreApplication

from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config



from PyQt5.uic import loadUi
import configparser

# config_path = './template_config.ini'
config_path = "./config.ini"

tmp_file = './tmp.png'


def now():
    return str(time.time())


def get_tmp_file():
    return now() + ".png"


def showErrorMsg(s):
    '''show the error diglog.'''
    error_msg = QErrorMessage.qtHandler()
    error_msg.showMessage(s)


class QiniuUploader():
    '''upload the image using qiniu'''

    def __init__(self, access_key: str, secret_key: str, bucket_name: str):
        self.bucket_name = bucket_name
        try:
            self.qiniu = qiniu.Auth(access_key, secret_key)
            print('init', access_key, secret_key)
        except Exception as e:
            showErrorMsg(
                "Access Key or Secret Key is error, please check setting.")
            print(e.args)
            self.qiniu = None

    def update(self, access_key: str, secret_key: str, bucket_name: str):
        try:
            print('update', access_key, secret_key, bucket_name)
            self.qiniu = qiniu.Auth(access_key, secret_key)
            self.bucket_name = bucket_name
        except Exception as e:
            showErrorMsg(
                "Access Key or Secret Key is error, please check setting.")
            print(e.args)

    def put_file(self, file_path: str, key: str, test=False):
        print('put_file', file_path)
        if not test:
            token = self.qiniu.upload_token(self.bucket_name, key, 3600)
            ret, _ = put_file(token, key, file_path)
            assert ret['key'] == key
            assert ret['hash'] == etag(file_path)
        else:
            print("just test, not upload")


def parseTrueOrFalse(s: str):
    if s == 'True':
        return True
    else:
        return False


def test():
    print("test---")


class PicUploader(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.clipboard = QApplication.clipboard()
        self.buffer = ""

        # init the PicUploader ui
        loadUi('PicUploader.ui', self)
        self.copyButton.clicked.connect(self.click_copy)
        # init setting ui
        self.setting = QWidget()
        loadUi('setting.ui', self.setting)

        # set some signals
        self.settingButton.clicked.connect(self.setting.show)
        self.setting.saveButton.clicked.connect(self.setting_save)

        # read config and set setting
        self.cf = configparser.ConfigParser()
        self.cf.read(config_path)

        # markdown, auto_upload, auto_copy
        self.markdown = parseTrueOrFalse(self.cf.get('QINIU', 'markdown'))
        self.auto_upload = parseTrueOrFalse(
            self.cf.get('QINIU', 'auto_upload'))
        self.auto_copy = parseTrueOrFalse(self.cf.get('QINIU', 'auto_copy'))
        self.outside_catenary = self.cf.get('QINIU', 'outside_catenary')

        self.setting.access_key.setText(self.cf.get('QINIU', 'access_key'))
        self.setting.secret_key.setText(self.cf.get('QINIU', 'secret_key'))
        self.setting.bucket_name.setText(self.cf.get('QINIU', 'bucket_name'))
        self.setting.outside_catenary.setText(
            self.cf.get('QINIU', 'outside_catenary'))
        self.setting.markdown.setChecked(self.markdown)
        self.setting.auto_copy.setChecked(self.auto_copy)
        self.setting.auto_upload.setChecked(self.auto_upload)

        # init qiniu
        self.qiniu = QiniuUploader(self.setting.access_key.text(),
                                   self.setting.secret_key.text(),
                                   self.setting.bucket_name.text())

        self.clipboard.dataChanged.connect(test)

        if self.auto_upload:
            self.clipboard.dataChanged.connect(self.getClipboard)

        self.show()

    def save_config(self):
        '''save the config to file'''
        self.cf.set('QINIU', 'secret_key', self.setting.access_key.text())
        self.cf.set('QINIU', 'secret_key', self.setting.secret_key.text())
        self.cf.set('QINIU', 'bucket_name', self.setting.bucket_name.text())
        self.cf.set('QINIU', 'outside_catenary',
                    self.setting.outside_catenary.text())
        self.cf.set('QINIU', 'markdown', str(self.markdown))
        self.cf.set('QINIU', 'auto_copy', str(self.auto_copy))
        self.cf.set('QINIU', 'auto_upload', str(self.auto_upload))
        with open(config_path, 'w') as f:
            self.cf.write(f)

    def setting_save(self):
        self.qiniu.update(self.setting.access_key.text(),
                          self.setting.secret_key.text(),
                          self.setting.bucket_name.text())
        self.markdown = self.setting.markdown.isChecked()
        # self.auto_upload = self.setting.auto_upload.isChecked()
        self.auto_copy = self.setting.auto_copy.isChecked()

        if not self.auto_upload and self.setting.auto_upload.isChecked():
            self.clipboard.dataChanged.connect(self.getClipboard)
            self.auto_upload = True
        elif self.auto_upload and not self.setting.auto_upload.isChecked():
            self.clipboard.dataChanged.disconnect(self.getClipboard)
            self.auto_upload = False

        self.save_config()
        print("setting save")

    def getClipboard(self):
        print('getClipBoard' + now())
        mimeData = self.clipboard.mimeData()
        if not mimeData.hasImage():
            return

        image = mimeData.imageData()
        if image.isNull():
            print("image is Null")
            return

        image.save('./' + now().replace('.', '-') + '.png')
        if not image.save(tmp_file):
            showErrorMsg("Save image fail.")
            return

        t = time.localtime(time.time())
        key = time.strftime('%y-%m-%d/%H%M%S.png', t)  # file name in qiniu
        print(key)

        try:
            self.qiniu.put_file(tmp_file, key)
        except Exception:
            showErrorMsg("Upload Fail, please check setting.")
            os.remove(tmp_file)
            return

        os.remove(tmp_file)

        if self.markdown:
            self.buffer = "![](http://%s/%s)" % (self.outside_catenary, key)
        else:
            self.buffer = "http://%s/%s" % (self.outside_catenary, key)
        if self.auto_copy:
            self.clipboard.clear()
            self.clipboard.setText(self.buffer)

    def click_copy(self):
        print('copy')
        self.clipboard.setText(self.buffer)


# test the QApplication.clipboard
# i find the clipboard will emit tice the dataChanged signals
# when i use the deepin-screenshot and Ctrl-C copy the image to clipboard
# i can not fix the bug now, but it does not influence the work


# def test_clipboard():
#     clipboard = QApplication.clipboard()
#     clipboard.dataChanged.connect(save_image)
#     print(clipboard.ownsSelection())

# def save_image():
#     print(now())
#     clipboard = QApplication.clipboard()
#     mimeData = clipboard.mimeData()
#     if clipboard.image().isNull():
#         print("Null")
#     if mimeData.hasImage():
#         print('image')
#         image = mimeData.imageData()
#         if image.isNull():
#             print("image is null")
#             return
#         image.save('./' + now().replace('.', '-') + '.png')


def main():
    app = QApplication(sys.argv)
    ex = PicUploader()
    # test_clipboard()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
