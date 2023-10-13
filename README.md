# PX4 Inspector project

# Getting Started
## 1. Download resource

```commandline
cd C:\Users\{username}\Desktop
해당 디렉토리에 PX4Inspector 폴더 전체를 다운로드합니다.
```

## 2. Install packages and Configuration

```
pip install -r requirements.txt
```

* Windows 환경에서 사용 시
```
pip install windows-curses
```

> /src/FTPInspectModule.py 파일에서 def geofenceInspect(): 함수 아래의 주석을 수정합니다

* Linux, MacOS 환경에서 사용 시
> /ui/PX4Inspector.py 파일에서 Serial={PX4가 연결된 시리얼 포트명} 으로 설정합니다. 
> ex) Serial = '/dev/ttyACM0'

> /src/FTPInspectModule.py 파일에서 def geofenceInspect(): 함수 아래의 주석을 수정합니다

### 분석 도구 실행

```
python main.py
```

### 주의 사항

파일 기반 점검의 **'T31. 중요 파일 무결성 검증' 항목**에서 드문 확률로 아래와 같은 디버깅 메시지 출력과 함께 프로그램 작동이 멈추는 현상이 발생할 수 있습니다. 

```
Attribute Error : NoneType object has no attribute
```

혹은, 오류 메시지 없이 프로그램이 강제종료 되는 현상이 발생할 수 있습니다.

이 경우, 프로그램을 재실행하셔서 **해당 항목을 먼저 점검**하시면 정상적으로 동작합니다. 만약 에러가 반복될 경우, 반복해서 재시도하십시오.