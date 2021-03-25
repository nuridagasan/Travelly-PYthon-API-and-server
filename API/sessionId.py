# Create random session ID
import random
def createRandomId():
    random_digits = 'abcdefghijklmnopABCDEFGHIJKLMNOP123456789'
    sess_id=''
    for i in range(len(random_digits)):
        random_digit = random.choice(random_digits)
        sess_id += random_digit
    return sess_id

createRandomId()