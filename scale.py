import statistics


def get_current_weight(ser):
    w = []
    for i in range(10):
        x = ser.readline()
        x = x.decode('ascii')
        if not 'M' in x:
            w.append(float(x[1:9]))

    old_weight = statistics.mean(w)
    print('Wight is: {}'.format(old_weight))
    return old_weight




