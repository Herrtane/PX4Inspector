import os
from os import path

file_path = './fs/microsd/log'

# 추가적으로 모든 하위 디렉토리 구조를 전부 검색
# 출력 형식 : 튜플 - (경로, 경로 내 디렉토리 리스트, 경로 내 파일 리스트)

def ftpInspect(item_number):
    if item_number == 'T38':
        result = logInspect()
    else:
        print('구현중..')
        result = False

def logInspect():
    log_count = 0
    for file in os.walk(file_path):
        log_count += 1

    if(path.exists(file_path) or log_count>0):
        return True
    else :
        return False