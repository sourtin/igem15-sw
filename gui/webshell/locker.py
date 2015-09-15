lockobj = ['', '']

def locked(user):
    global lockobj
    return False if lockobj[0] == '' else (True)

def lock(user, reason):
    global lockobj
    if lockobj[0] == '':
        lockobj = [user, reason]
        return True
    else:
        return False

def unlock(user):
    global lockobj
    if lockobj[0] == user:
        lockobj = ['', '']
        return True
    else:
        return False
