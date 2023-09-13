# TODO : 로그 파일 존재 유무 확인 기능

import sys
import os.path
import getpass
import glob
import hashlib
import platform
from PyQt5.QtWidgets import *
from src.mavlink_shell import get_serial_item
from src.FTPReader import FTPReader
from src.Mission.PyMavlinkCRC32 import crc
from src.Mission.PX4MissionParser import missionParser
from src.Mission.tools import SerialPort, command

from src.PX4Mission import hash_sha1, hash_md5, createdTime, dataman_is_encrypted #mission
from src.PX4Log import hash_sha1, hash_md5, createdTime, is_encrypted # logger
from src.Logger.PX4LogParser import *

import csv
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QVariant

from PyQt5 import uic
from os import environ
import os
from matplotlib import patches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from haversine import inverse_haversine, Direction, Unit
import pandas as pd
from pandas import Series, DataFrame
from ui.PX4InspectorParameter import Parameterclass

# Use if it have to set port manually
# if you use linux os, check your serial port that connected with px4
# example: Serial = '/dev/ttyACM0'
Serial = None

def suppress_qt_warnings():   # 해상도별 글자크기 강제 고정하는 함수
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("ui/PX4Inspector.ui")[0]
download_class = uic.loadUiType("ui/downloadProgress.ui")[0]

#CSV 파일 존재 유무 확인
username = getpass.getuser()
# dirpath = 'C:/Users/' + username + '/Desktop/PX4Forensic/fs/microsd/log/2022-07-18/'
# fileExe = '*.csv'
# csvlist = glob.glob(dirpath+fileExe)
# if csvlist == []:
#     shell_ulog_2_csv()

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # self.parameter_ui = Parameterclass(self.parameterList, self.parameterDescription, self.parameterValue, self.parameterRange, self.parameterInformation)
        self.progressbar = QProgressBar()
        self.statusbar.addPermanentWidget(self.progressbar)
        self.step = 0
        self.modulePath = ""
        # self.tabWidget.currentChanged.connect(self.onChange)
        self.clicked_log = ""
        self.parent_log = ""
        self.mavPort = None
        self.label_connected.setText(f"unconnected")
        self.login = None
        self.ftp = None

        # 시작 시 자동 연결
        self.connectSerial(serial=Serial)
        
        # 로고
        self.initUI()

        self.dataman = "./fs/microsd/dataman"

        try:
            parser_fd = os.open(self.dataman, os.O_BINARY)
            self.parser = missionParser(parser_fd)
            # 파일 정보 표시(mission)
            # self.fileInfo(self.dataman, self.tableWidget_file)
            QMessageBox.about(self, '기존 데이터 발견', '이전 작업에서 불러왔던 데이터가 발견되었습니다. 해당 데이터를 로드합니다.')
        except FileNotFoundError as e:
            QMessageBox.about(self, '기존 데이터 없음', '검사 대상 PX4 드론에서 데이터를 불러온 적이 없습니다. 데이터를 새로 추출합니다. 해당 작업은 몇 분 정도 소요될 수 있습니다.')
            self.getFileFromUAV()
            # parser_fd = os.open(self.dataman, os.O_BINARY)
            # self.parser = missionParser(parser_fd)
            pass
        except AttributeError as a:
            print(a)            
            parser_fd = os.open(self.dataman,0)
            self.parser = missionParser(parser_fd)

        self.dataRefreshButton.clicked.connect(self.getFileFromUAV)

        self.fig = plt.Figure(figsize=(1,1))
        self.canvas = FigureCanvas(self.fig)

        self.log_fig = plt.Figure(figsize=(1,1))
        self.log_canvas = FigureCanvas(self.log_fig)
        
        # self.tabWidget.setCurrentIndex(0)
        
    def initUI(self):
        self.setWindowTitle('PX4Inspector')
        self.setWindowIcon(QIcon('drone.png'))
        self.setGeometry(300,300,300,200)
        self.show()
    
    def returnClickedItem(self, tw):
        return(tw.text())

    def connectSerial(self, serial = None):
        if serial is not None:
            self.mavPort = SerialPort(serial)
            self.label_connected.setText(f"connected: {serial}")
        elif serial is None:
            # port 연결
            serial_list = get_serial_item()

            if len(serial_list) != 0:
                if serial_list[0][0].find("통신 포트") > 0:
                    return -1
                self.mavPort = SerialPort(serial_list[0][0])
                self.label_connected.setText(f"connected: {serial_list[0][1]}({serial_list[0][0]})")
            else:
                self.mavPort = None
                self.label_connected.setText(f"unconnected")

        # self.login = self.loginCheck()
        
        # 핵심 코드
        self.ftp = FTPReader(_port=self.mavPort)

        return 1

    def getFileFromUAV(self):

        if self.ftp is None:
            res = self.connectSerial()
            if res == -1:
                QMessageBox.about(self, '연결 오류', 'PX4와 연결되어 있지 않습니다.')
                return -1
        # self.radio_safepoint.setDisabled(True)
        # self.radio_geofencepoint.setDisabled(True)
        # self.radio_waypoint.setDisabled(True)
        self.dataRefreshButton.setDisabled(True)

        st = []
        root = self.ftp.tree_root
        search_result = []
        st.append(root)
        i = 0
        while len(st) > 0:
            item = st.pop()
            # item = 부모 노드
            # item이 디렉토리면, chdir(item.data)
            # item이 파일이면, 아래 과정 무시

            if item != root:
                if item.data.find('/') != -1:
                    while (not os.path.exists(item.data)):
                        os.chdir("..")
                    os.chdir(item.data)

            for sub in item.child:

                # sub = 자식 노드
                # sub이 디렉토리면, mkdir(sub.data)
                # sub이 파일이면, 파일 생성

                cur = sub
                filename = ""
                # 현재 노드가 파일일 경우
                if cur.data.find('/') == -1:
                    while cur.parent != None:
                        filename = cur.data + filename
                        cur = cur.parent
                    # root 경로 추가
                    filename = '/' + filename
                    # 해당 디렉토리에 파일 받기
                    print(filename, self.ftp.total_count)
                    if self.step >= 100:
                        self.step = 0

                    self.statusbar.showMessage(filename)
                    self.statusbar.repaint()
                    while True:
                        res = self.ftp.get_file_by_name(filename)
                        if res[0] == -1:
                            print("재요청중...")
                            # self.mav_port.ftp_close(seq_num=0)
                        elif res[0] == 0:
                            search_result.append([filename, 'SUCCESS'])
                            # 화면 하단 진행바 표시 코드
                            self.step = int((i / self.ftp.total_count)*100)
                            self.progressbar.setValue(self.step)
                            print(i)
                            QApplication.processEvents()
                            i += 1
                            break
                        elif res[0] == 2:
                            if res[1] == 13:
                                search_result.append([filename, 'EACCES'])
                                break
                        elif res[0] == 4:
                            print("Session not found. reloading...")
                        elif res[0] == 10:
                            search_result.append([filename, 'FILEEXISTSERROR'])
                            break
                        else:
                            break
                else:
                    try:
                        foldername = sub.data
                        while foldername[0] == " ":
                            foldername = foldername[1:]
                        os.makedirs(foldername)
                    except FileExistsError:
                        pass
                st.append(sub)
        self.statusbar.showMessage("")
        self.statusbar.repaint()
        self.progressbar.setValue(0)

        try:
            parser_fd = os.open(self.modulePath, os.O_BINARY)
            self.parser = missionParser(parser_fd)

            # 파일 정보 표시(mission)
            self.fileInfo(self.modulePath, self.tableWidget_file)

        except FileNotFoundError as e:
            print(os.getcwd())
            self.parser = None
            print(e)
            pass
        except AttributeError as a:
            print(a)
            parser_fd = os.open(self.dataman,0)
            self.parser = missionParser(parser_fd)
            self.fileInfo(self.modulePath, self.tableWidget_file)
            pass

        QApplication.processEvents()
        self.dataRefreshButton.setEnabled(True)

    def HMAC_calc(self, filename):
        command("cd /\n", self.mavPort)
        s = command("cat " + filename.strip(".") + "h\n", self.mavPort).split("\n")[1]
        print("received raw: ", s)
        s = s[40:68]

        res = 0
        a = [ord(i) for i in s]
        for i in a:
            res = (res << 8) + i
        hmac_rec = str(hex(res))[2:]
        print("received hmac file: ", hmac_rec)

        h = hashlib.sha3_224()
        plain = open(filename, 'rb').read()
        plain = plain + b"mesl:1234"
        h.update(plain)
        hmac_cur = h.hexdigest()
        print("hmac of current file: ", hmac_cur)

        return hmac_rec == hmac_cur

    def getCurrentItems(self):
        if self.log_treeWidget.indexOfTopLevelItem(self.log_treeWidget.currentItem()) == -1:
            self.parent_log = self.log_treeWidget.currentItem().parent().text(0)

    #TODO: 로그 데이터 경로 수정
    def onChange(self):
        tabIndex = self.tabWidget.indexOf(self.tabWidget.currentWidget())
        #비행 데이터

        if tabIndex == 1:
            self.modulePath = "./fs/microsd/dataman"
            

        #로그 데이터

        elif tabIndex == 2:
            username = getpass.getuser()
            self.modulePath = "C:/Users/" + username  + "/Desktop/PX4Forensic/fs/microsd/log/2022-07-18/09_39_09.ulg"   
            #정보 출력
            self.fileInfo(self.modulePath, self.tableWidget_file_log)
            self.logParams(self.tableWidget_log_params, self.modulePath)
            self.logMessages(self.tableWidget_log_messages, self.modulePath)
                        
        #설정 데이터
        elif tabIndex == 3:
            self.parameter_ui.show_parameter_list()

    def fileInfo(self, filename, table):
        try:
            fd = os.open(filename, os.O_BINARY)
        except FileNotFoundError:
            return
        except AttributeError as a:
            print(a)            
            fd = os.open(filename,0)
            
        if fd < 0:
            if self.ftp is not None:
                self.getFileFromUAV()
                try:
                    fd = os.open(filename, os.O_BINARY)
                except AttributeError as a:
                    print(a)            
                    fd = os.open(filename,0)
            elif fd < 0 or self.ftp is None:
                return -1

        if "dataman" in filename :
            datamanId = self.parser.get_mission()[3]
            encrypt = dataman_is_encrypted(self.parser.get_safe_points(), self.parser.get_fence_points(),
                               self.parser.get_mission_item(datamanId), self.parser.get_mission())
            if self.ftp is not None:
                inte = self.HMAC_calc(filename)
            else:
                inte = "unconnected"

        if "ulg" in filename:
            encrypt = is_encrypted(filename)
            inte = True

        created = createdTime(filename)
        hashSha = hash_sha1(filename)
        hashMD5 = hash_md5(filename)

        if self.ftp is not None:
            ftpcrc = self.ftp.get_crc_by_name(filename[filename.find("/"):], 0)
            Crc = crc()
            CrcResult = Crc.crc32Check(filename=filename, checksum=ftpcrc[1])
        else:
            CrcResult = "unconnected"


        if encrypt == 0:
            encrypt = "False"
        elif encrypt ==1 :
            encrypt = "True"

        header = ["created", "MD5", "SHA-1","CRC", "integrity"]
        data = [created, hashSha,hashMD5,CrcResult,inte]

        table.setColumnCount(2)
        table.setRowCount(len(header))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)

        for i in range(len(header)):
            table.setItem(i, 0, QTableWidgetItem(header[i]))
            table.setItem(i, 1, QTableWidgetItem(str(data[i])))

        table.resizeRowsToContents()
        table.resizeColumnsToContents()
        os.close(fd)

    def logParams(self, table, filepath):
        _list = shell_log_params(filepath)
        table.setColumnCount(2)
        table.setRowCount(len(_list))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)

        for i in range(len(_list)):
            table.setItem(i, 0, QTableWidgetItem(_list[i][0]))
            table.setItem(i, 1, QTableWidgetItem(str(_list[i][1])))

        table.resizeRowsToContents()
        table.resizeColumnsToContents()

    def logMessages(self, table, filepath):
        _list = shell_log_messages(filepath)
        table.setColumnCount(1)
        table.setRowCount(len(_list))
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        
        for i in range(len(_list)):
            table.setItem(i, 0, QTableWidgetItem(_list[i]))
  
        table.resizeRowsToContents()
        table.resizeColumnsToContents()

def PX4Inspector():
    suppress_qt_warnings()
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()