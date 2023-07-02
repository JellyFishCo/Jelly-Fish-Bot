import random
import string
def punishment_id():
    letters = string.ascii_uppercase
    stringrandom = ''.join(random.choice(letters) for i in range(6))
    punishment_id = 'JF-' + stringrandom
    return punishment_id