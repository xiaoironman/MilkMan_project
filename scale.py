import statistics


def get_current_weight(ser):
    w = []
    for i in range(10):
        x = ser.readline()
        x = x.decode('ascii')
        if not 'M' in x:
            w.append(float(x[:9]))
    return statistics.mean(w)




