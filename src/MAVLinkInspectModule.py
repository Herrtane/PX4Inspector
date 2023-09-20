def mavlinkInspectBranch(item_number):
    if item_number == 'T06':
        result = 1
    else:
        print('구현중..')
        result = 0
    return result

def mavlinkInspectSuccessResultMessage(item_number):
    if item_number == 'T06':
        result = 'T06 구현중'
    else:
        result = '구현중'
    return result

def mavlinkInspectHoldResultMessage(item_number):
    if item_number == 'T06':
        result = 'T06 구현중.'
    else:
        result = '적절하지 않은 항목입니다.'
    return result