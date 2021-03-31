def getMaxIndex(line, space, length, leftOver, n):
    last_working_index = 0
    if space >= length:  # if the length of the inut is smaller than the space we can print the whole line, no need to check
        return length
    for i in range(space):
        if leftOver <= space:
            last_working_index = leftOver
            break
        if line[i] == " ":
            last_working_index = i + 1  # remove the space by adding +1 so it's all on the same line
    if last_working_index == 0 and leftOver != 0:  # if the input is >= 25 chars without a space we have to break it anyways
        # print("line break forced: break at index 25:")
        return space
    else:
        # print("sucessfully wrapped a line at index", last_working_index,":")
        return last_working_index


def textWrap(text, N):
    text = list(text)  # creates a list of chars out of the given string
    wrapped_text = list()  # where we store our wrapped text
    tmp = list()  # temporary variable which holds the string to be placed in the spots of wrappedTextArray
    wrapped_text_list = list()  # array which holds enough space for a max of 40 lines of text
    k = 0  # index of the wrappedTextArray
    n = N  # total number of spaces we want indent the text by
    total = 25  # total number of spaces we are able to fill (left to right)
    start = 0  # index where we currently are in the input (Text)
    space = total - n  # how much space we have to write on (before the line break needs to occur)
    length = len(text)  # length of the text
    left_over = length - start  # how many chars we have left to process
    while start < length:  # while we are not through all the chars
        for i in range(n):  # we start a new line by indenting it by n spaces  
            wrapped_text.append("  ")  # indent text by n spaces
            tmp.append("  ")
        if space > left_over:  # so we don't get index out of bounds for inputs smaller than space
            sequence = list("".join(text[start:(
                        start + left_over)]))  # give it the max amount of chars which could fit and make it a list again
        else:
            sequence = list("".join(text[start:(start + space)]))
        maxIndex = getMaxIndex(sequence, space, length, left_over,
                               n)  # find out what the maximum index is (end of the last word we can print on the line without cutting it)
        for i in range(maxIndex):
            wrapped_text.append(text[start + i])  # add as many words as possible on the rest of the line
            tmp.append(text[start + i])
        start += maxIndex
        left_over = length - start  # how many chars we have left to process

        wrapped_text_list.append("".join(tmp))
        tmp = list()
        k += 1
    return wrapped_text_list


def shorten_name(name, space):
    output = list(name)
    if space < len(name) + 3:
        del output[space - 3:]  # delete chars of the name
        output.append('...')
    return ''.join(output)


def check_for_abnormal(name, List, Type):
    name = list(name)
    too_big = List
    adjust = 1.5
    adjust_value = -1.2
    if Type == 'ts':
        adjust_value = 0.3
    for i in range(len(name)):
        for j in range(len(too_big)):
            if name[i] == too_big[j]:
                adjust += adjust_value
    return int(adjust)


def mergeNameCounter(name, counter):
    sign = "(" + str(counter) + ")"
    if counter == 0:  # we don't need to indicate ne messages in this case
        sign = ""
    return str(name + "  " + sign)

'''
def mergeNameCounter(name, counter, space):
    output = ""
    # too_big = ['W','m','w',]
    # too_small = ['I','f','i','j','l','t']
    # adjust = check_for_abnormal(name, too_big, 'tb')
    # adjust += check_for_abnormal(name, too_small, 'ts')
    if counter > 9:
        counter = '*'
    sign = "(" + str(counter) + ")"
    if counter == 0:  # we don't need to indicate ne messages in this case
        sign = ""

    if space >= len(name) + 3:  # name needs to be extended (too short)
        output = '{:<40}{:>3}'.format(name, sign)
    elif space < len(name) + 3:  # name needs to be cut (too long)
        name_space = space - 3 - 3  # + adjust  # space the name is allowed to occupy (plus the space 3 dots will occupy to indicate the name was cut off)
        output = list(name)
        del output[name_space:]  # delete chars of the name
        output.append('...')
        # output.append(sign)
        output = ''.join(output)
        output = '{:<40}{:>3}'.format(output, sign)
    return output
'''
