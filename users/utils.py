import random

def generate_otp(length=6):
    
    return '{:06d}'.format(random.randint(0, 999999))