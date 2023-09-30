import os
from os import path
from src.Mission.PX4MissionParser import missionParser

# 추가적으로 모든 하위 디렉토리 구조를 전부 검색
# 출력 형식 : 튜플 - (경로, 경로 내 디렉토리 리스트, 경로 내 파일 리스트)

# result
# 0 : 요구사항 만족 안함
# 1 : 요구사항 만족
# 2 : 점검자에 의한 추가 점검 요 (보류)

def ftpInspectBranch(mav_port, item_number):
    if item_number == 'T07':
        result = cryptInspect()
    elif item_number == 'T10':
        result = accessInspect()
    elif item_number == 'T11':
        result = backupInspect()
    elif item_number == 'T12':
        result = infoExposureInspect()
    elif item_number == 'T31':
        result = fileintegrityInspect(mav_port)
    elif item_number == 'T38':
        result = logInspect()
    elif item_number == 'T43':
        result = geofenceInspect()
    else:
        print('구현중..')
        result = 0
    return result

def ftpInspectSuccessResultMessage(item_number):
    if item_number == 'T10':
        result = '파일 및 디렉터리에 대한 접근 통제가 이루어지고 있는 것이 확인되었습니다.'
    elif item_number == 'T11':
        result = '중요 데이터가 백업되는 것이 확인되었습니다.'
    elif item_number == 'T12':
        result = '파일 및 디렉터리에 대한 불필요한 정보 노출이 없는 것이 확인되었습니다.'
    elif item_number == 'T31':
        result = 'PX4내의 /fs/microsd 내부의 임의의 파일을 수정하려고 시도하였으나, 해당 파일에 대한 수정이 보호되었습니다. 따라서, 파일에 대한 무결성 검증이 이루어지는 것이 확인되었습니다.'
    elif item_number == 'T38':
        result = './fs/microsd/log' + ' 위치에서 로그 파일 및 디렉터리가 확인되었습니다.'
    elif item_number == 'T43':
        result = './fs/microsd/dataman 파일에서 geofence 정보가 설정되어 특정 지역 접근 방지 기능이 정상적으로 작동하는 것이 확인되었습니다.'
    else:
        result = '구현중'
    return result

def ftpInspectHoldResultMessage(item_number):
    if item_number == 'T07':
        result = 'PX4Inspector 작업 폴더 내 ./bin, ./dev, ./etc, ./fs, ./obj, ./proc 디렉토리 추출이 완료되었습니다. 해당 디렉토리 내 파일에 대한 주요 데이터 암호화 여부에 대한 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T11':
        result = './fs/microsd/parameters_backup.bson 파일이 발견되었습니다. 해당 파일 내 중요 데이터 백업에 대한 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T12':
        result = 'PX4Inspector 작업 폴더 내 ./bin, ./dev, ./etc, ./fs, ./obj, ./proc 디렉토리 추출이 완료되었습니다. 해당 디렉토리 내 불필요한 정보 노출에 대한 점검자의 추가 분석이 필요합니다.'
    else:
        result = '적절하지 않은 항목입니다.'
    return result

def fileintegrityInspect(mav_port):
    filename = "/fs/microsd/kkk"
    mavMsg = {
        'seq_number': 0,
        'session': 0,
        'opcode': 0,
        'size': 0,
        'req_opcode': 0,
        'burst_complete': 0,
        'offset': 0,
        'data': []
    }

    while True:
        mavBuffer = mav_port.ftp_read(4096)
        if mavBuffer and len(mavBuffer) > 0:
            print(mavBuffer)
        else:
            break

    result = 0
    mavMsg['data'] = 'hi'
    mav_port.ftp_write(opcode=7, session=mavMsg['session'], data=mavMsg['data'], size=len(mavMsg['data']), offset=0)
    while True:
        mavMsg['seq_number'] = 0
        mavBuffer = mav_port.ftp_read(4096)
        if mavBuffer and len(mavBuffer) > 0:
            print(mavBuffer)
            if mavBuffer['opcode'] == 129:  # 오류 처리
                if mavBuffer['data'][0] == 9:   # 파일이 Write Protected일 경우 (점검 목적)
                    print("File protected")
                    result = 1
                else:
                    if mavBuffer['data'][0] == 2:  # 운영체제 사이드에서 오류
                        if mavBuffer['data'][1] == 13:  # Permission denied
                            print("Permission denied")
                            mav_port.ftp_close(seq_num=mavBuffer['seq_number'], session=0)
                    result = 0
                break
            else:
                mavMsg = mavBuffer
                result = 0
                break

    mav_port.ftp_close(seq_num=mavMsg['seq_number'], session=0)
    return result

def geofenceInspect():
    parser_fd = os.open("./fs/microsd/dataman", os.O_RDONLY)
    parser = missionParser(parser_fd)
    geoPoints = parser.get_fence_points()
    print(geoPoints)
    geo_count = 0
    for i in geoPoints:
        geo_count += 1
    if geo_count > 0:
        return 1
    else:
        return 0

def cryptInspect():
    # 파일 접근 검사를 통해 파일이 추출되었다면 해당 파일을 점검자가 직접 추가 확인 해서 판단
    if accessInspect() == 0:
        return 2
    else:
        return 0

def accessInspect():
    access_count = 0
    if path.exists('./bin'):
        for file in os.walk('./bin'):
            access_count += 1

    if path.exists('./dev'):
        for file in os.walk('./dev'):
            access_count += 1

    if path.exists('./etc'):
        for file in os.walk('./etc'):
            access_count += 1

    if path.exists('./fs'):
        for file in os.walk('./fs'):
            access_count += 1

    if path.exists('./obj'):
        for file in os.walk('./obj'):
            access_count += 1

    if path.exists('./proc'):
        for file in os.walk('./proc'):
            access_count += 1

    # 파일이 존재한다는 건 파일 접근 통제가 안된다는 의미
    # logInspect()와는 반대로 파일이 존재하지 않아야 점검 통과인 True 반환
    if access_count > 0:
        return 0
    else:
        return 1

def backupInspect():
    if path.exists('./fs/microsd/parameters_backup.bson'):
        return 2
    else:
        return 0

def infoExposureInspect():
    # 파일 접근 검사를 통해 파일이 추출되었다면 해당 파일을 점검자가 직접 추가 확인 해서 판단
    if accessInspect() == 0:
        return 2
    else:
        return 1

def logInspect():
    file_path = './fs/microsd/log'
    log_count = 0
    for file in os.walk(file_path):
        log_count += 1

    if path.exists(file_path) or log_count>0:
        return 1
    else :
        return 0

# 작업 시 주의사항 :
# 스크립트를 import 해서 사용할 경우에는 값이 달라진다.
# os는 현재 실행경로를 반환하기 때문에
# os.getcwd() 코드가 위치하는 파일이 아닌, import한 스크립트를 기준으로 경로가 반환되는 점을 주의해야한다.
# print(os.getcwd())
