import os
from os import path
from src.Mission.PX4MissionParser import missionParser

# 추가적으로 모든 하위 디렉토리 구조를 전부 검색
# 출력 형식 : 튜플 - (경로, 경로 내 디렉토리 리스트, 경로 내 파일 리스트)

# result
# 0 : 요구사항 만족 안함
# 1 : 요구사항 만족
# 2 : 점검자에 의한 추가 점검 요 (보류)

def ftpInspectBranch(mav_port, ftp, item_number):
    if item_number == 'T07':
        result = cryptInspect()
    elif item_number == 'T10':
        result = accessInspect()
    elif item_number == 'T11':
        result = backupInspect()
    elif item_number == 'T12':
        result = infoExposureInspect()
    elif item_number == 'T31':
        result = fileintegrityInspect(mav_port, ftp)
    elif item_number == 'T38':
        result = logInspect()
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
        result = '드론의 임무 데이터를 포함하고 있는 /fs/microsd/dataman 파일을 다운로드하고 수정하여 업로드 하였으나, 드론에서 수정을 거부하였습니다. 중요 파일에 대한 무결성 검증이 이루어지는 것으로 판단됩니다만, 점검자의 추가 분석이 필요합니다.'
    else:
        result = '구현중'
    return result

def ftpInspectFailedResultMessage(item_number):
    if item_number == 'T07':
        result = 'PX4-Inspector 작업 폴더 내 ./bin, ./dev, ./obj, ./proc ./etc, ./fs, 드론의 데이터 추출이 완료되었습니다. 해당 폴더 내 주요 데이터 암호화가 이루어지지 않은 것으로 판단됩니다만, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T10':
        result = 'PX4-Inspector 작업 폴더 내 ./bin, ./dev, ./obj, ./proc ./etc, ./fs, 드론의 데이터 추출이 완료되었습니다. 임의의 파일에 접근 가능하여, 파일 및 디렉터리에 대한 접근 통제가 이루어지지 않는 것으로 판단됩니다만, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T11':
        result = '중요 데이터에 대한 백업 파일을 찾을 수 없습니다. 해당 항목의 요구사항을 만족하지 않습니다.'
    elif item_number == 'T12':
        result = 'PX4-Inspector 작업 폴더 내 ./bin, ./dev, ./obj, ./proc ./etc, ./fs, 드론의 데이터 추출이 완료되었습니다. 해당 폴더내 모든 정보가 노출되어 있는 것으로 판단됩니다만, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T31':
        result = '드론의 임무 데이터를 포함하고 있는 /fs/microsd/dataman 파일을 다운로드하고 수정하여 업로드 하였으나 정상적으로 동작을 하였습니다. 중요 파일에 대한 무결성 검증이 이루어지지 않는 것으로 판단됩니다만, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T38':
        result = './fs/microsd/log' + ' 위치에서 로그 파일 및 디렉터리를 찾을 수 없어, 해당 항목의 요구사항을 만족하지 않는 것으로 판단됩니다.'
    else:
        result = '구현중'
    return result

def ftpInspectHoldResultMessage(item_number):
    if item_number == 'T07':
        result = '파일을 추출하는 과정에서 오류가 발생하였습니다. 드론으로부터 파일을 다시 추출한 이후 재시도하십시오.'
    elif item_number == 'T11':
        result = 'PX4-Inspector 작업 폴더 내 ./bin, ./dev, ./obj, ./proc ./etc, ./fs, 드론의 데이터 추출이 완료되었습니다. \n./fs/microsd/parameters_backup.bson 파일이 존재하며, 설정 데이터의 백업이 존재합니다만, 점검자의 추가 분석이 필요합니다. (다른 중요 데이터의 백업 유무는 발견되지 않았습니다.)'
    elif item_number == 'T12':
        result = '파일을 추출하는 과정에서 오류가 발생하였습니다. 드론으로부터 파일을 다시 추출한 이후 재시도하십시오.'
    elif item_number == 'T31':
        result = '항목을 점검하는 과정에서 오류가 발생하였습니다. 드론과의 연결상태, 점검하려는 드론 내의 대상 파일의 상태 등을 확인하고 다시 시도해주십시오.'
    elif item_number == 'T38':
        result = 'PX4-Inspector 작업 폴더 내 ./bin, ./dev, ./obj, ./proc ./etc, ./fs, 드론의 데이터 추출이 완료되었습니다. ./fs/microsd/log 폴더에 로그 정보를 확인하였습니다만, 점검자의 추가 분석이 필요합니다. 추가로, 드론 운용사의 문서를 통해 주기적인 로그 감사 여부를 확인해야 합니다.'
    else:
        result = '적절하지 않은 항목입니다.'
    return result

def fileintegrityInspect(mav_port, ftp):
    filename = "/fs/microsd/dataman"

    f = open("." + filename, 'rb')
    file_data = f.read()
    backup_data = []
    for i in file_data:
        backup_data.append(i)
    f.close()
    print(backup_data)
    backup_data_2 = backup_data[:]
    backup_data_2[0] = 77
    backup_data_2[1] = 66
    print(backup_data_2)

    result = 2
    offset = 0
    send_size = 0
    # 매우 주의 : Sequence number 설정 안하면 드론에서 계속 똑같은 메시지만 보낸다...

    # Open and Read
    ftpSend(mav_port, opcode=4, data=filename, size=len(filename), seq_number=1)
    recv_msg = ftpRecvParsor(mav_port)
    print(recv_msg)
    total_size = 0
    for i in range(4):
        total_size += recv_msg['data'][i] * pow(256, i)
    filesize = total_size
    if total_size - offset > 230:
        read_size = 230
    elif total_size - offset == 0:
        read_size = 1
    else:
        read_size = total_size - offset
    print(filesize)
    ftpSend(mav_port, opcode=5, data=filename, size=read_size, offset=0, seq_number=2)
    recv_msg = ftpRecvParsor(mav_port)
    print(recv_msg)

    ftpSend(mav_port, opcode=1, seq_number=3)
    recv_msg = ftpRecvParsor(mav_port)
    print(recv_msg)


    # Create and Write
    ftpSend(mav_port, opcode=6, data=filename, size=len(filename), seq_number=4)
    recv_msg = ftpRecvParsor(mav_port)
    print(recv_msg)

    while True:
        if offset >= len(backup_data_2):
            break
        if len(backup_data_2) > 230:
            send_size = 230
        else:
            send_size = len(backup_data_2)
        ftpSend(mav_port, opcode=7, size=send_size, data=backup_data_2, offset=offset, seq_number=5)
        print(f"{filename}: {offset} of {len(backup_data_2)}")
        recv_msg = ftpRecvParsor(mav_port)
        print(recv_msg)
        offset += send_size

    ftpSend(mav_port, opcode=1, seq_number=6)
    recv_msg = ftpRecvParsor(mav_port)
    print(recv_msg)

    # Open and Read
    ftpSend(mav_port, opcode=4, data=filename, size=len(filename), seq_number=7)
    recv_msg = ftpRecvParsor(mav_port)
    print(recv_msg)
    ftpSend(mav_port, opcode=5, data=filename, size=230, offset=0, seq_number=8)
    recv_msg = ftpRecvParsor(mav_port)
    print(recv_msg)
    print(recv_msg['data'][0])
    print(recv_msg['data'][1])
    if recv_msg['data'][0] == 77 and recv_msg['data'][1] == 66:
        result = 0
    else:
        result = 1

    ftpSend(mav_port, opcode=1, seq_number=9)
    recv_msg = ftpRecvParsor(mav_port)
    print(recv_msg)

    return result

def ftpSend(mavPort, opcode=0, data='', size=0, offset=0, session=0, seq_number=0):
    payload = []

    # write sequence
    for i in range(2):
        payload.append(seq_number % 256)
        seq_number = int((seq_number - seq_number % 256) / 256)

    # write session
    payload.append(session)

    # write opcode
    payload.append(opcode)

    # write size
    payload.append(size)

    # write req opcode
    payload.append(0)

    # write burst_complete
    payload.append(0)

    # write padding
    payload.append(0)

    # write offset
    for i in range(4):
        payload.append(offset % 256)
        offset = int((offset - offset % 256) / 256)

    # write data
    for x in data:
        if str(type(x)) == "<class 'str'>":
            payload.append(ord(x))
        else:
            payload.append(x)

    # write some bytes
    print("sending '%s' of len %u" % (payload, len(payload)), 2)

    payload.extend([0] * (251 - len(payload)))
    mavPort.mav.mav.file_transfer_protocol_send(0, mavPort.mav.target_system, mavPort.mav.target_component, payload)

def ftpRecvParsor(mavPort):
    msg = mavPort.mav.recv_match(type='FILE_TRANSFER_PROTOCOL', blocking=True)
    data = msg.payload
    ret = {
        'seq_number': data[0] + data[1] * 256,
        'session': data[2],
        'opcode': data[3],
        'size': data[4],
        'burst_complete': data[6],
        'req_opcode': data[5],
        'offset': data[8] + data[9] * 256 + data[10] * (256 * 256) + data[11] * (256 * 256 * 256),
        'data': data[12:12 + data[4]]
    }

    return ret

def cryptInspect():
    # 파일 접근 검사를 통해 파일이 추출되었다면 해당 파일을 점검자가 직접 추가 확인 해서 판단
    if accessInspect() == 0:
        return 0
    else:
        return 2

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
        return 0
    else:
        return 2

def logInspect():
    file_path = './fs/microsd/log'
    log_count = 0
    for file in os.walk(file_path):
        log_count += 1

    if path.exists(file_path) or log_count>0:
        return 2
    else :
        return 0

# 작업 시 주의사항 :
# 스크립트를 import 해서 사용할 경우에는 값이 달라진다.
# os는 현재 실행경로를 반환하기 때문에
# os.getcwd() 코드가 위치하는 파일이 아닌, import한 스크립트를 기준으로 경로가 반환되는 점을 주의해야한다.
# print(os.getcwd())
