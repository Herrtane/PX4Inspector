from pymavlink import mavutil
from pymavlink.generator import mavcrc

def mavlinkInspectBranch(mav_connection, item_number):
    result_msg = None
    if item_number == 'T46':
        result, result_msg = hwInspect(mav_connection)
    elif item_number == 'T06':
        result, result_msg = mavcryptInspect(mav_connection)
    elif item_number == 'T22':
        result, result_msg = msgintegrityInspect(mav_connection)
    elif item_number == 'T54':
        result, result_msg = timesyncInsepct(mav_connection)
    else:
        print('구현중..')
        result = 0
        result_msg = '구현중..'
    return result, result_msg

def msgParsor(msg):
    msg_to_dict = msg.to_dict()
    msg_to_string = '{'
    for key, value in msg_to_dict.items() :
        msg_to_string += str(key)
        msg_to_string += ': '
        msg_to_string += str(value)
        msg_to_string += ', '
    msg_to_string = msg_to_string[:-2]
    msg_to_string += '}'
    return msg_to_string


def hwInspect(mav_connection):
    mav_connection.mav.command_long_send(mav_connection.target_system, mav_connection.target_component,
                                         mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
    result_msg = mav_connection.recv_match(type='COMMAND_ACK', blocking=True)
    print(result_msg)
    if result_msg and result_msg.command == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM :
        if result_msg.result == 0 :
            result = 1
        # result가 1이면 GPS 등의 설정 오류로 일시적으로 명령이 보류된 상태
        elif result_msg.result == 1 :
            result = 2
        result_msg_str = msgParsor(result_msg)
    else :
        result = 0
        result_msg_str = '[Error] Cannot capture the packet'
    return result, result_msg_str

def msgintegrityInspect(mav_connection):
    # mav_connection.disable_signing()
    temp_secret_key = chr(42) * 32
    temp_link_id = 0
    temp_timestamp = 0
    mav_connection.setup_signing(temp_secret_key)

    return 1, '1'

def timesyncInsepct(mav_connection):
    mav_connection.mav.timesync_send(0, 0)
    result_msg = mav_connection.recv_match(type='TIMESYNC', blocking=True)
    print(result_msg)
    if result_msg and result_msg.ts1:
        result = 1
        result_msg_str = msgParsor(result_msg)
    else:
        result = 0
        result_msg_str = '[Error] Cannot capture the packet'
    return result, result_msg_str

def mavcryptInspect(mav_connection):
    result_msg = mav_connection.recv_match(type='HEARTBEAT', blocking=True)
    print(result_msg.to_dict())
    if result_msg:
        result = 2
        result_msg_str = msgParsor(result_msg)
    else:
        result = 0
        result_msg_str = '[Error] Cannot capture the packet'
    return result, result_msg_str

def mavlinkInspectSuccessResultMessage(item_number):
    if item_number == 'T46':
        result = 'T46 성공'
    elif item_number == 'T06':
        result = 'T06 성공'
    elif item_number == 'T54':
        result = 'T54 성공'
    else:
        result = '구현중'
    return result

def mavlinkInspectHoldResultMessage(item_number):
    if item_number == 'T46':
        result = 'ARMING 명령이 Accepted 되었으나, GPS 설정 등이 제대로 이루어지지 않아 일시적으로 명령이 보류된 상태입니다. 드론 설정을 마친 후에 재시도하십시오.'
    elif item_number == 'T06':
        result = '드론으로부터 수신된 HEARTBEAT 메시지를 캡쳐하였습니다. 점검자에 의한 암호화 여부 추가 점검이 필요합니다.'
    else:
        result = '적절하지 않은 항목입니다.'
    return result