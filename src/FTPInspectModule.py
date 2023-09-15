import os
from os import path

# 추가적으로 모든 하위 디렉토리 구조를 전부 검색
# 출력 형식 : 튜플 - (경로, 경로 내 디렉토리 리스트, 경로 내 파일 리스트)

# result
# 0 : 요구사항 만족 안함
# 1 : 요구사항 만족
# 2 : 점검자에 의한 추가 점검 요 (보류)

def ftpInspectBranch(item_number):
    if item_number == 'T10':
        result = accessInspect()
    elif item_number == 'T12':
        result = infoExposureInspect()
    elif item_number == 'T38':
        result = logInspect()
    else:
        print('구현중..')
        result = 0
    return result

def ftpInspectSuccessResultMessage(item_number):
    if item_number == 'T10':
        result = '파일 및 디렉터리에 대한 접근 통제가 이루어지고 있는 것이 확인되었습니다.'
    elif item_number == 'T12':
        result = '파일 및 디렉터리에 대한 불필요한 정보 노출이 없는 것이 확인되었습니다.'
    elif item_number == 'T38':
        result = './fs/microsd/log' + ' 위치에서 로그 파일 및 디렉터리가 확인되었습니다.'
    else:
        result = '구현중'
    return result

def ftpInspectHoldResultMessage(item_number):
    if item_number == 'T12':
        result = 'PX4Inspector 작업 폴더 내 ./bin, ./dev, ./etc, ./fs, ./obj, ./proc 디렉토리 추출이 완료되었습니다. 해당 디렉토리 내 T12 항목에 대한 점검자의 추가 분석이 필요합니다.'
    else:
        result = '적절하지 않은 항목입니다.'
    return result

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
