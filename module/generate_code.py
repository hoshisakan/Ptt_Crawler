import secrets
import string

def createRandomCode():
    # TODO 提取所有大小寫字母與數字
    alphabet = string.ascii_letters + string.digits

    # TODO 產生固定長度的隨機碼，目前預設長度為6字元
    while True:
        code = ''.join(secrets.choice(alphabet) for i in range(6))
        # TODO 如果有小寫字母在隨機產生的代碼中，返回True；反之，若皆為空沒有任何的小寫字母存在，則返回False
        if (any(c.islower() for c in code)
                # TODO 產生2個大寫字母
                and sum(c.isupper() for c in code) > 1
                # TODO 產生2個數字
                and sum(c.isdigit() for c in code) > 1):
            break
    return code
