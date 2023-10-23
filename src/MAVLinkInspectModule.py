from pymavlink import mavutil
from pymavlink.generator import mavcrc
from datetime import datetime

def mavlinkInspectBranch(mav_connection, item_number):
    result_msg = None
    if item_number == 'T46':
        result, result_msg, send_msg = hwInspect(mav_connection)
    elif item_number == 'T06':
        result, result_msg, send_msg = mavcryptInspect(mav_connection)
    elif item_number == 'T22':
        result, result_msg, send_msg = msgintegrityInspect(mav_connection)
    elif item_number == 'T40':
        result, result_msg, send_msg = odidInspect(mav_connection)
    elif item_number == 'T43':
        result, result_msg, send_msg = geofenceInspect(mav_connection)
    elif item_number == 'T53':
        result, result_msg, send_msg = sessionInspect(mav_connection)
    elif item_number == 'T54':
        result, result_msg, send_msg = timesyncInsepct(mav_connection)
    elif item_number == 'T60':
        result, result_msg, send_msg = flightmodeInspect(mav_connection)
    elif item_number == 'T62':
        result, result_msg, send_msg = inappropriateorderInspect(mav_connection)
    elif item_number == 'T67':
        result, result_msg, send_msg = dosInspect(mav_connection)
    else:
        print('구현중..')
        result = 0
        result_msg = '구현중..'
        send_msg = '구현중..'
    return result, result_msg, send_msg

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
    send_msg_str = "{mavpackettype : COMMAND_LONG, command : MAV_CMD_COMPONENT_ARM_DISARM(400), confirmation : 0, param1 : 1, param2 : 0, param3 : 0, param4 : 0, param5 : 0, param6 : 0, param7 : 0}"
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
        result_msg_str = '[Error] Cannot receive packets'
    return result, result_msg_str, send_msg_str

def msgintegrityInspect(mav_connection):
    send_msg_str = 'None'
    result_msg = mav_connection.recv_match(type='HEARTBEAT', blocking=True)
    print(result_msg)
    signature_field = mav_connection.mav.signing.secret_key
    if signature_field:
        result = 1
        result_msg_str = msgParsor(result_msg) + '\n'
        result_msg_str += "Signature Field : " + str(signature_field)
    else:
        result = 0
        result_msg_str = msgParsor(result_msg) + "\n"
        result_msg_str += "Signature Field : None"
    return result, result_msg_str, send_msg_str

def timesyncInsepct(mav_connection):
    send_msg_str = "{mavpackettype : TIMESYNC, tc1 : 0, ts1 : 0}"
    mav_connection.mav.timesync_send(0, 0)
    result_msg = mav_connection.recv_match(type='TIMESYNC', blocking=True)
    print(result_msg)
    if result_msg:
        result = 1
        result_msg_str = msgParsor(result_msg)
    else:
        result = 0
        result_msg_str = '[Error] Cannot receive packets'
    return result, result_msg_str, send_msg_str

def mavcryptInspect(mav_connection):
    send_msg_str = 'None'
    result_msg = mav_connection.recv_match(type='HEARTBEAT', blocking=True)
    print(result_msg.to_dict())
    if result_msg:
        result = 0
        result_msg_str = msgParsor(result_msg)
    else:
        result = 2
        result_msg_str = '[Error] Cannot receive packets'
    return result, result_msg_str, send_msg_str

def flightmodeInspect(mav_connection):
    send_msg_str = "{mavpackettype : COMMAND_LONG, command : MAV_CMD_DO_SET_MODE(176), confirmation : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, param5 : 0, param6 : 0, param7 : 0}"
    mav_connection.mav.command_long_send(mav_connection.target_system, mav_connection.target_component,
                                         mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0, 0, 0, 0, 0, 0, 0, 0)
    result_msg = mav_connection.recv_match(type='COMMAND_ACK', blocking=True)
    print(result_msg)
    if result_msg and result_msg.command == mavutil.mavlink.MAV_CMD_DO_SET_MODE :
        if result_msg.result == 0 :
            result = 1
        # result가 1이면 GPS 등의 설정 오류로 일시적으로 명령이 보류된 상태
        elif result_msg.result == 1 :
            result = 2
        result_msg_str = msgParsor(result_msg)
    else :
        result = 0
        result_msg_str = '[Error] Cannot receive packets'
    return result, result_msg_str, send_msg_str

def inappropriateorderInspect(mav_connection):
    send_msg_str = "{mavpackettype : COMMAND_INT, frame : MAV_FRAME_GLOBAL(0), command : MAV_CMD_NAV_LAND(21), current : 0, autocontinue : 0, param1 : 0, param2 : 0, param3 : 0, param4 : 0, x : 0, y : 0, z : 0}"
    mav_connection.mav.command_int_send(mav_connection.target_system, mav_connection.target_component, 0,
                                         mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    result_msg = mav_connection.recv_match(type='COMMAND_ACK', blocking=True)
    print(result_msg)
    if result_msg and result_msg.command == mavutil.mavlink.MAV_CMD_NAV_LAND:
        if result_msg.result == 0:
            result = 0
        # result가 1이면 GPS 등의 설정 오류로 일시적으로 명령이 보류된 상태
        elif result_msg.result == 1:
            result = 2
        result_msg_str = msgParsor(result_msg)
    else:
        result = 1
        result_msg_str = msgParsor(result_msg)
    return result, result_msg_str, send_msg_str

def dosInspect(mav_connection):
    send_msg_str = "{mavpackettype : STATUSTEXT, severity : MAV_SEVERITY_ALERT(1), text : 'dos'}"
    for i in range(30000):
        mav_connection.mav.statustext_send(1, b"dos")
        result_msg = mav_connection.recv_msg()
        print(result_msg)
    if result_msg:
        result = 1
        result_msg_str = msgParsor(result_msg)
    else: # 만약 드론에서 정상적인 응답이 오지 않는다면 DoS 대응을 못한다고 판단할 수 있음
        result = 0
        result_msg_str = '[Error] Cannot receive packets'
    return result, result_msg_str, send_msg_str

def odidInspect(mav_connection):
    send_msg_str = "None"
    for i in range(10):
        result_msg = mav_connection.recv_match(type='HEARTBEAT', blocking=True)
        print(result_msg.to_dict())
        if result_msg:
            if result_msg.type == 34:
                result = 1
                result_msg_str = msgParsor(result_msg)
                break
            else:
                result = 0
                result_msg_str = msgParsor(result_msg)
        else:
            result = 0
            result_msg_str = '[Error] Cannot receive packets'
            break
    return result, result_msg_str, send_msg_str

def sessionInspect(mav_connection):
    send_msg_str = "None"
    result_msg_total = ''
    count = 0
    for i in range(10):
        result_msg = mav_connection.recv_match(type='HEARTBEAT', blocking=True)
        print(result_msg.to_dict())
        if result_msg:
            result_msg_str = msgParsor(result_msg)
            count += 1
        else:
            result_msg_str = '[Error] Cannot receive packets'
        result_msg_total += '[Receive Packet Time : ' + str(datetime.now().time()) + '] '
        result_msg_total += '\n'
        result_msg_total += result_msg_str
        result_msg_total += '\n'
        result_msg_total += '--------------------------------'
        result_msg_total += '\n'
    if count > 5: # 일정 수 이상의 Heartbeat 메시지를 정상 수신하였다면 Connection이 이루어졌다고 판단 가능
        result = 1
    else:
        result = 0
    return result, result_msg_total, send_msg_str

def geofenceInspect(mav_connection):
    send_msg_str = "{mavpackettype : MISSION_ITEM, frame : MAV_FRAME_GLOBAL(0), command : MAV_CMD_NAV_FENCE_CIRCLE_INCLUSION(5003), current : 1, autocontinue : 0, param1 : 1136753143, param2 : 0, param3 : 0, param4 : 0, x : 372394750, y : 1270807222, z : 0, mission_type : 1}"
    mav_connection.mav.mission_count_send(1, 1, 0, 0)
    mav_connection.mav.mission_count_send(1, 1, 1, 1)
    result_msg = mav_connection.recv_match(type='MISSION_REQUEST', blocking=True)
    print(result_msg)
    mav_connection.mav.mission_item_int_send(mav_connection.target_system, mav_connection.target_component, 0, 0, 5003,
                                             1, 0, 1136753143, 0, 0, 0, 372394750, 1270807222, 1, 1)
    result_msg = mav_connection.recv_match(type='MISSION_ACK', blocking=True)
    mav_connection.mav.mission_count_send(1, 1, 0, 2)
    result_msg = mav_connection.recv_match(type='MISSION_ACK', blocking=True)
    print(result_msg)

    if result_msg:
        if result_msg.type == 0:
            result = 1
        # result가 1이면 GPS 등의 설정 오류로 일시적으로 명령이 보류된 상태
        elif result_msg.type == 1:
            result = 2
        result_msg_str = msgParsor(result_msg)
    else:
        result = 0
        result_msg_str = msgParsor(result_msg)
    return result, result_msg_str, send_msg_str

def mavlinkInspectSuccessResultMessage(item_number):
    if item_number == 'T46':
        result = 'ARMING 명령이 Accepted 되었습니다. 따라서, 해당 항목의 요구사항을 만족합니다.'
    elif item_number == 'T06':
        result = 'T06 성공'
    elif item_number == 'T40':
        result = '수신된 다수의 Heartbeat 메시지 내의 type field가 MAV_TYPE_ODID(34)와 일치하여 Open Drone ID에 기반한 드론 식별이 이루어지는 것이 확인되었습니다.'
    elif item_number == 'T43':
        result = '드론으로 geofence 설정 변경 패킷을 전송하고, /fs/microsd/dataman 파일에 정상 반영함을 확인하였으나, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T53':
        result = '드론으로부터 주기적으로 HEARTBEAT 메시지가 전송되고 있습니다만, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T54':
        result = '드론에 Time Sync 메시지를 전송하고 수신하여 시간 동기화가 이루어지는 것을 확인했습니다만, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T60':
        result = '드론에 Preflight 모드로의 비행 모드 변경 명령을 전송하여 정상적으로 이루어지는 것으로 확인됩니다만, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T62':
        result = '비정상적인 비행 지점으로의 비행 명령을 전송하였으나, 드론에서 해당 명령을 거부하였습니다. 제어 명령 오류 확인이 정상적으로 이루어지고 있습니다.'
    elif item_number == 'T67':
        result = 'DoS 공격을 수행하였으나, 드론에서 오류 발생 없이 정상적인 ACK 메시지가 수신되었습니다. 서비스 거부 대응이 이루어지는 것이 확인되었습니다.'
    else:
        result = '구현중'
    return result

def mavlinkInspectFailedResultMessage(item_number):
    if item_number == 'T46':
        result = 'ARMING 명령이 받아들여지지 않아, 해당 요구 사항을 만족하지 않습니다.'
    elif item_number == 'T06':
        result = '드론으로부터 수신된 HEARTBEAT 메시지를 정상적으로 수신하였습니다. 암호 통신이 이루어지지 않는 것으로 판단되나, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T22':
        result = '드론으로부터 수신된 HEARTBEAT 메시지에 signature field가 설정되어 있지 않습니다. 통신 메시지 무결성 검증 기능이 이루어지지 않는 것으로 판단되나, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T40':
        result = '드론으로부터 수신된 HEARTBEAT 메시지 내의 MAV_TYPE_ODID(34) 필드가 존재하지 않습니다만, 점검자의 추가 분석이 필요합니다.'
    elif item_number == 'T43':
        result = '드론으로 geofence 설정 변경 패킷을 전송하였으나, /fs/microsd/dataman 파일에 반영되지 않아, 해당 항목의 요구사항을 만족하지 않는 것으로 판단됩니다.'
    elif item_number == 'T53':
        result = '드론으로부터 주기적으로 전송된 Heartbeat 메시지를 정상적으로 수신하지 못하였습니다. 드론과의 Connection이 정상적으로 이루어지지 않았거나, 연결 상태가 좋지 않습니다.'
    elif item_number == 'T54':
        result = 'Time Sync 메시지가 정상적으로 송수신되지 않았습니다. 시간 동기화 기능이 이루어지지 않습니다.'
    elif item_number == 'T60':
        result = '비행 모드 변경을 시도하였으나, 드론으로부터 NAK 메시지를 수신하였습니다. 비행 모드 설정 및 변경 기능이 제공되지 않습니다.'
    elif item_number == 'T62':
        result = '비정상적인 비행 지점으로의 비행 명령을 전송하였으나, 드론에서 해당 명령을 승인하였습니다. 제어 명령 오류 확인이 정상적으로 이루어지지 않았습니다.'
    elif item_number == 'T67':
        result = '드론에 STATUSTEXT 메시지에 대한 DoS 공격 수행으로 인해, 드론으로부터 정상적인 메시지 수신이 이루어지지 않고 있습니다만, 점검자의 추가 분석이 필요합니다.'
    else:
        result = '구현중'
    return result

def mavlinkInspectHoldResultMessage(item_number):
    if item_number == 'T46':
        result = '드론에 ARMING 명령을 전송하여 Accepted 되었으나, GPS 설정 등이 제대로 이루어지지 않아 일시적으로 명령이 보류된 상태입니다.'
    elif item_number == 'T06':
        result = '드론으로부터 HEARTBEAT 메시지를 정상적으로 수신하지 못하였습니다. 드론 연결 상태를 확인한 후 다시 시도해주십시오.'
    elif item_number == 'T43':
        result = '특정 지역으로의 접근을 방지하는 Geofence 설정 메시지를 전송하였으나, 설정이 제대로 이루어지지 않아 명령이 거부된 상태입니다. (Geofence 설정 기능 지원은 되는 상태입니다.) 드론 설정을 마친 후에 재시도하십시오.'
    elif item_number == 'T60':
        result = '비행 모드 변경 명령이 Accepted 되었으나, GPS 설정 등이 제대로 이루어지지 않았거나 해당 비행 모드가 적절하지 않아 일시적으로 명령이 보류된 상태입니다. 설정을 검토한 후에 재시도하십시오.'
    elif item_number == 'T62':
        result = '드론에 LANDING 명령을 전송하였으나, GPS 설정 등이 제대로 이루어지지 않아 일시적으로 명령이 보류된 상태입니다.'
    else:
        result = '적절하지 않은 항목입니다.'
    return result