# Todo : onChange 같은 코드 정리해도 된다고 판단했으면 정리하기
# Todo : 중요파일 무결성 검증은 Write 관련 연구 필요

import sys
import os.path

from PyQt5.QtWidgets import *
from src.mavlink_shell import get_serial_item
from src.FTPReader import FTPReader
from src.Mission.PX4MissionParser import missionParser
from src.Mission.tools import SerialPort, command
from src.FTPInspectModule import *
from src.MAVLinkInspectModule import *

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from PyQt5 import uic
from os import environ
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


# Use if it have to set port manually
# if you use linux os, check your serial port that connected with px4
# example: Serial = '/dev/ttyACM0'
Serial = None

# 해상도별 글자크기 강제 고정하는 함수
def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

form_class = uic.loadUiType("ui/PX4Inspector.ui")[0]
download_class = uic.loadUiType("ui/downloadProgress.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.progressbar = QProgressBar()
        self.statusbar.addPermanentWidget(self.progressbar)
        self.step = 0
        self.modulePath = ""
        self.clicked_log = ""
        self.parent_log = ""

        # MAVLink Connection 핵심 객체 (이후 주로 사용할 객체)
        # MavPort.py 파일에서 클래스 변수, 메서드 참고
        self.mavPort = None

        self.label_connected.setText(f"unconnected")
        self.login = None
        self.ftp = None

        # 시작 시 자동 연결
        self.connectSerial(serial=Serial)
        self.initUI()

        self.dataman = "./fs/microsd/dataman"

        try:
            parser_fd = os.open(self.dataman, os.O_BINARY)
            self.parser = missionParser(parser_fd)
            QMessageBox.about(self, '기존 데이터 발견', '이전 작업에서 불러왔던 데이터가 발견되었습니다. 해당 데이터를 로드합니다.')
        except FileNotFoundError as e:
            QMessageBox.about(self, '기존 데이터 없음', '검사 대상 PX4 드론에서 데이터를 불러온 적이 없습니다. 데이터를 새로 추출합니다. 해당 작업은 몇 분 정도 소요될 수 있습니다.')
            self.getFileFromUAV()
            pass
        except AttributeError as a:
            print(a)            
            parser_fd = os.open(self.dataman,0)
            self.parser = missionParser(parser_fd)

        self.dataRefreshButton.clicked.connect(self.getFileFromUAV)
        self.ftp_listWidget.itemDoubleClicked.connect(self.ftpDoubleClicked)
        self.ftp_start_pushButton.clicked.connect(self.ftpStartClicked)
        self.mavlink_listWidget.itemDoubleClicked.connect(self.mavlinkDoubleClicked)
        self.mavlink_start_pushButton.clicked.connect(self.mavlinkStartClicked)

        self.fig = plt.Figure(figsize=(1, 1))
        self.canvas = FigureCanvas(self.fig)

        self.log_fig = plt.Figure(figsize=(1, 1))
        self.log_canvas = FigureCanvas(self.log_fig)

    def ftpDoubleClicked(self):
        global selected_ftp_item_name
        selected_ftp_item_name = self.ftp_listWidget.currentItem().text()
        self.ftp_selected_textEdit.setText(selected_ftp_item_name)


    def ftpStartClicked(self):
        selected_item_number = selected_ftp_item_name.split('.')[0]
        # FTPInspectModule 함수로 분기
        ftp_result = ftpInspectBranch(selected_item_number)
        items = self.ftp_result_tableWidget.findItems(selected_item_number, Qt.MatchExactly)
        item = items[0]
        if ftp_result == 1:
            temp_item = QTableWidgetItem()
            temp_item.setText("O")
            self.ftp_result_tableWidget.setItem(item.row(), 1, temp_item)
            self.ftp_result_textEdit.setText(ftpInspectSuccessResultMessage(selected_item_number))
        elif ftp_result == 0 :
            temp_item = QTableWidgetItem()
            temp_item.setText("X")
            self.ftp_result_tableWidget.setItem(item.row(), 1, temp_item)
            self.ftp_result_textEdit.setText('이 드론은 선택한 항목의 보안 요구사항을 충족시키지 않습니다.')
        else :
            temp_item = QTableWidgetItem()
            temp_item.setText("보류")
            self.ftp_result_tableWidget.setItem(item.row(), 1, temp_item)
            self.ftp_result_textEdit.setText(ftpInspectHoldResultMessage(selected_item_number))

    def mavlinkDoubleClicked(self):
        global selected_mavlink_item_name
        selected_mavlink_item_name = self.mavlink_listWidget.currentItem().text()
        self.mavlink_selected_textEdit.setText(selected_mavlink_item_name)

    # TODO : mavport 객체를 parameter로 전달해야할듯?
    # TODO : 아직 결과창을 ui에 안만들어서 result 출력 부분에서 에러 발생
    def mavlinkStartClicked(self):
        print("Heartbeat from system (system %u component %u)" % (self.mavPort.mav.target_system, self.mavPort.mav.target_component))
        # self.mavPort.mav.send()
        selected_item_number = selected_mavlink_item_name.split('.')[0]
        # FTPInspectModule 함수로 분기
        mavlink_result = mavlinkInspectBranch(selected_item_number)
        items = self.mavlink_result_tableWidget.findItems(selected_item_number, Qt.MatchExactly)
        item = items[0]
        if mavlink_result == 1:
            temp_item = QTableWidgetItem()
            temp_item.setText("O")
            self.mavlink_result_tableWidget.setItem(item.row(), 1, temp_item)
            self.mavlink_result_textEdit.setText(mavlinkInspectSuccessResultMessage(selected_item_number))
        elif mavlink_result == 0:
            temp_item = QTableWidgetItem()
            temp_item.setText("X")
            self.mavlink_result_tableWidget.setItem(item.row(), 1, temp_item)
            self.mavlink_result_textEdit.setText('이 드론은 선택한 항목의 보안 요구사항을 충족시키지 않습니다.')
        else:
            temp_item = QTableWidgetItem()
            temp_item.setText("보류")
            self.mavlink_result_tableWidget.setItem(item.row(), 1, temp_item)
            self.mavlink_result_textEdit.setText(mavlinkInspectHoldResultMessage(selected_item_number))

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

        # 핵심 코드
        self.ftp = FTPReader(_port=self.mavPort)

        return 1

    def getFileFromUAV(self):

        if self.ftp is None:
            res = self.connectSerial()
            if res == -1:
                QMessageBox.about(self, '연결 오류', 'PX4와 연결되어 있지 않습니다.')
                return -1

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

        except FileNotFoundError as e:
            print(os.getcwd())
            self.parser = None
            print(e)
            pass
        except AttributeError as a:
            print(a)
            parser_fd = os.open(self.dataman,0)
            self.parser = missionParser(parser_fd)
            pass

        QApplication.processEvents()
        self.dataRefreshButton.setEnabled(True)

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