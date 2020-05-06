#test = "test this phrase which is way too long to be displayed on a single line in the listBox where it should ultimately be placed and wrapped around correctly so the user is able to read it without having to scroll."
#test2 = "testthisphrasewhichiswaytoolongtobedisplayedonasinglelineinthelistBoxwhereitshouldultimatelybeplacedandwrappedaroundcorrectlysotheuserisabletoreaditwithouthavingtoscroll."

#print("12345678901234567890123456789012345678901234567890")  # exactly 50 spots (to compare output)

def getMaxIndex(line, space, length, leftOver, n):
    lastWorkingIndex = 0
    if space >= length: # if the length of the inut is smaller than the space we can print the whole line, no need to check
        return length
    for i in range(space):
        if leftOver <= space:
            lastWorkingIndex = leftOver
            break
        if line[i] == " ":
            lastWorkingIndex = i+1 # remove the space by adding +1 so it's all on the same line
    if lastWorkingIndex == 0 and leftOver !=0: # if the input is >= 25 chars without a space we have to break it anyways
        #print("line break forced: break at index 25:")
        return space
    else:
        #print("sucessfully wrapped a line at index", lastWorkingIndex,":")
        return lastWorkingIndex

def textWrap(Text, N):
    text = list(Text)  # creates a list of chars out of the given string
    wrappedText = list()  # where we store our wrapped text
    tmp = list()  # temporary variable which holds the string to be placed in the spots of wrappedTextArray
    wrappedTextList = list()  # array which holds enough space for a max of 40 lines of text
    k = 0  # index of the wrappedTextArray
    n = N  # total number of spaces we want indent the text by
    total = 25 # total number of spaces we are able to fill (left to right)
    start = 0  # index where we currently are in the input (Text)
    space = total-n  # how much space we have to write on (before the line break needs to occur)
    length = len(Text)  # length of the text
    leftOver = length-start  # how many chars we have left to process
    while start < length:  # while we are not through all the chars
        for i in range(n):  # we start a new line by indenting it by n spaces  
            wrappedText.append("  ")  # indent text by n spaces
            tmp.append("  ")
        if space > leftOver:  # so we don't get index out of bounds for inputs smaller than space
            sequence = list("".join(text[start:(start+leftOver)]))  # give it the max amount of chars which could fit and make it a list again
        else:
            sequence = list("".join(text[start:(start+space)]))
        maxIndex = getMaxIndex(sequence, space, length, leftOver, n)  # find out what the maximum index is (end of the last word we can print on the line without cutting it)
        for i in range(maxIndex):
            wrappedText.append(text[start+i])  # add as many words as possible on the rest of the line
            tmp.append(text[start+i])
        start += maxIndex
        leftOver = length-start  # how many chars we have left to process
        #wrappedText.append("\n")

        wrappedTextList.append("".join(tmp))
        tmp = list()
        k += 1
    
    #return "".join(wrappedText)
    return wrappedTextList

#T = textWrap(test, 25)
#print(T)
#for line in T:
#    print(line)


def mergeNameCounter(name, counter, space):
    output = ""
    sign = "(" + str(counter) + ")"
    if counter == 0:
        sign = "   "
    if len(name) == space - len(str(
            counter)) - 2:  # if the length of the name is not too long to leave no space for the counter (inclusive brackets)
        output = ''.join([name, sign])  # join the two and save it as output
    elif space > len(name) + len(str(counter)) + 2:  # name needs to be extended (too short)
        extendBy = space - len(name) - len(
            str(counter)) - 2  # how many spaces we need to balance it and show the counter at the end of the line
        oldOutput = list(name)
        for i in range(extendBy):  # add spaces to the name
            oldOutput.append(" ")
        output = ''.join(oldOutput)
        output = ''.join([output, sign])
    else:  # name needs to be cut (too long)
        nameSpace = space - len(str(
            counter)) - 2 - 3  # space the name is allowed to occupy (plus the space 3 dots will occupy to indicate the name was cut off)
        oldOutput = list(name)
        del oldOutput[nameSpace:]  # delete chars of the name
        output = ''.join(oldOutput)
        output = ''.join([output, "...", sign])
    return output