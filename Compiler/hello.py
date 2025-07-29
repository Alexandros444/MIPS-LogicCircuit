#!/usr/bin/env python3

import array

labels = []
cmds = [(":","Label:","s"),("nop","0","s"),("#","Comment","s"),("lw","100011","i"),
        ("sw","101011","i"),("beq","000100","i"),("j","000010","j"),("add","000000","r","00000","100000")]
pos = 0



def strToBin(string):
    data = array.array('B')
    for i in range(3,-1,-1):
        data.append(int(string[i*8:i*8+8],2))
    return data


def int2bin(integer, digits):
    if integer >= 0:
        return bin(integer)[2:].zfill(digits)
    else:
        return bin(2**digits + integer)[2:]


def passCommand(string, pos):
    tokens = string.split()
    #for t in tokens:
    #    print(t)
    for cmd in cmds:
        if(tokens[0] == cmd[0]):
            break
    if(tokens[0] != cmd[0]):
        exit("Failed at Line: %d" % pos)
    result = ""
    #Spezialbefehle
    if(cmd[2] == "s"):
        if(cmd[0] == ":"):
            labels.append((tokens[1],pos))
        elif(cmd[0] == "nop"):
            result = "00000000000000000000000000000000"
    else:
        #Normale Befehle
        result = cmd[1]
        if(cmd[2] == "r"):
            result = result+int2bin(int(tokens[2][1:]),5)+int2bin(int(tokens[3][1:]),5)+int2bin(int(tokens[1][1:]),5)+cmd[3]+cmd[4]
        elif(cmd[2] == "i"):
            result = result+int2bin(int(tokens[2][1:]),5)+int2bin(int(tokens[1][1:]),5)+int2bin(int(tokens[3]),16)
        elif(cmd[2] == "j"):
            result = result+int2bin(int(tokens[1]),26)
    space = ""
    for i in range(0,40-len(string[:-1])):
        space = space+" "
    print("#"+str(pos)+": "+string[:-1]+space+"BIN: "+result)
    return result





f_src = open("src.txt","rt")
f_comp = open("compiled","wb")

for line in f_src:
    cmd = passCommand(line,pos)
    if(cmd and cmd != ""):
        pos=pos+1
        strToBin(cmd).tofile(f_comp)

f_src.close()
f_comp.close()
























