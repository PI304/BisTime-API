import random


def generate_random_timeblock():
    s = ""
    for n in range(48):
        s += str(random.randint(0, 1))

    return s


print(generate_random_timeblock())
