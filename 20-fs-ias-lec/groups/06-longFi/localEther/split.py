

def split_data(data):

    data = [data[i:i+1500] for i in range(0, len(data), 1500)]
    return data