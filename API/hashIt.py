def hashIt(string):
    val = 31
    new_val = 0
    for i in range(len(string)):
        new_val += val * new_val + ord(string[i])
    return new_val

