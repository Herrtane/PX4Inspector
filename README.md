# PX4-Inspector project

# Getting Started
## 1. Download resource

```commandline
cd C:\Users\{username}\Desktop
해당 디렉토리에 PX4-Inspector 폴더 전체를 다운로드합니다.
```

## 2. Install packages and Configuration

```
pip install -r requirements.txt
```

* 실행하기 전
> /ui/PX4Inspector.py 파일의 Initial Configuration Code 에서 OS에 따라 Windows 용, Mac 용의 주석을 해제하고, 사용하지 않는 OS의 line 2줄을 주석처리합니다.
> ex) Windows 환경일 경우, Windows 용 부분 주석 해제, Mac 부분 주석처리

* Windows 환경에서 사용 시
```
pip install windows-curses
```

* Linux, MacOS 환경에서 사용 시
> /ui/PX4Inspector.py 파일에서 Serial={PX4가 연결된 시리얼 포트명} 으로 설정합니다. 
> ex) Serial = '/dev/ttyACM0'

### 분석 도구 실행

```
python main.py
```

## 3. 주의 사항

### 첫 프로그램 실행 시

프로그램의 정상적인 초기화 및 동작을 위해, 첫 프로그램 실행 후 드론의 파일을 자동 불러오기 (혹은 수동 불러오기) 한 이후, **반드시 아래의 절차를 따른 후 점검을 재개하시기 바랍니다**

1. 프로그램을 종료한 후
2. PX4 드론과 PC의 연결을 해제하고, 재연결합니다
3. 이후, 프로그램을 재실행하십시오.

### 오류 현상 대응방법

파일 기반 점검의 **'T31. 중요 파일 무결성 검증' 항목**에서 드문 확률로 아래와 같은 디버깅 메시지 출력과 함께 프로그램 작동이 멈추는 현상이 발생할 수 있습니다. 

```
Attribute Error : NoneType object has no attribute
```

혹은, 오류 메시지 없이 프로그램이 강제종료 되는 현상이 발생할 수 있습니다.

이 경우, 프로그램을 재실행하셔서 **해당 항목을 먼저 점검**하시면 정상적으로 동작합니다. 만약 에러가 반복될 경우, 반복해서 재시도하십시오.

## Contributor

본 연구는 **경희대학교 컴퓨터공학과 및 융합보안대학원 MESL 연구실**에서 진행하였습니다.