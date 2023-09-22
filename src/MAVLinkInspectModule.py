from pymavlink import mavutil

def mavlinkInspectBranch(mav_connection, item_number):
    result_msg = None
    if item_number == 'T46':
        result, result_msg = hwInspect(mav_connection)
    else:
        print('구현중..')
        result = 0
    return result, result_msg

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
    else :
        result = 0
    result_msg_str = 'COMMAND_ACK ' + '{command : ' + str(result_msg.command) + ', result : ' + str(result_msg.result) + ', target_system : ' + str(result_msg.target_system) + ', target_component : '+ str(result_msg.target_component) + '}'
    return result, result_msg_str

def mavlinkInspectSuccessResultMessage(item_number):
    if item_number == 'T46':
        result = '성공'
    else:
        result = '구현중'
    return result

def mavlinkInspectHoldResultMessage(item_number):
    if item_number == 'T46':
        result = 'ARMING 명령이 Accepted 되었으나, GPS 설정 등이 제대로 이루어지지 않아 일시적으로 명령이 보류된 상태입니다. 드론 설정을 마친 후에 재시도하십시오.'
    else:
        result = '적절하지 않은 항목입니다.'
    return result