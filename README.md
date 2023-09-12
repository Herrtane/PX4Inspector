# PX4 Inspector project

# Introduction
> ###PX4 Autopilot 내부 데이터를 분석하고 무결성 검증을 제공하는 응용 프로그램입니다.
* 무결성 검증 기능은 khu-mesl-348/PX4-Autopilot 펌웨어와 호환됩니다.
* 일부 기능은 PX4와 USB Serial 연결이 필요합니다.
# Getting Started
## 1. Download resource
```commandline
cd C:\Users\{username}\Desktop
git clone https://github.com/khu-mesl-348/PX4Forensic.git
```

## 2. install packages

![python3.9](https://img.shields.io/badge/python-3.9-blue) 
![altgraph](https://img.shields.io/badge/altgraph-0.17.3-random)
![bson](https://img.shields.io/badge/bson-0.5.10-random)
![contourpy](https://img.shields.io/badge/contourpy-1.0.5-random)
![crccheck](https://img.shields.io/badge/crccheck-1.2.0-random)
![cycler](https://img.shields.io/badge/cycler-0.11.0-random)
![fonttools](https://img.shields.io/badge/fonttools-4.37.2-random)
![future](https://img.shields.io/badge/future-0.18.2-random)
![haversine](https://img.shields.io/badge/haversine-2.7.0-random)
![iso8601](https://img.shields.io/badge/iso8601-1.0.2-random)
![kiwisolver](https://img.shields.io/badge/kiwisolver-1.4.4-random)
![lxml](https://img.shields.io/badge/lxml-4.9.1-random)
![matplotlib](https://img.shields.io/badge/matplotlib-3.6.0-random)
![numpy](https://img.shields.io/badge/numpy-1.23.3-random)
![packaging](https://img.shields.io/badge/packaging-21.3-random)
![pandas](https://img.shields.io/badge/pandas-1.4.4-random)
![pefile](https://img.shields.io/badge/pefile-2022.5.30-random)
![Pillow](https://img.shields.io/badge/Pillow-9.2.0-random)
![pymavlink](https://img.shields.io/badge/pymavlink-2.4.31-random)
![pyparsing](https://img.shields.io/badge/pyparsing-3.0.9-random)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.7-random)
![pyserial](https://img.shields.io/badge/pyserial-3.5-random)
![pytz](https://img.shields.io/badge/pytz-2022.2.1-random)
![PyYAML](https://img.shields.io/badge/PyYAML-6.0-random)
![six](https://img.shields.io/badge/six-1.16.0-random)
![pyulog](https://img.shields.io/badge/pyulog-1.0.0-random)
```
pip install -r requirements.txt
```

* Windows 환경에서 사용 시
```
pip install windows-curses
```

* Linux 환경에서 사용 시
> /ui/PX4Inspector.py 파일에서 Serial={PX4가 연결된 시리얼 포트명} 으로 설정해준다. 
> ex) Serial = '/dev/ttyACM0'

### 분석 도구 실행
```
python main.py
```

# How to Use