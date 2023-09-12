# PX4 Inspector project

# Getting Started
## 1. Download resource
```commandline
cd C:\Users\{username}\Desktop
해당 디렉토리에 PX4Inspector 폴더 전체를 다운로드합니다.
```

## 2. Install packages

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