#!/usr/bin/env python3

import array

labels = [("zero",0)]
consts = [("zero",0)]

cmds = [(":","Label:","s"),("nop","0","s"),("#","Comment","s"),("","","s"),("const","store","s"),("lw","100011","i"),
        ("sw","101011","i"),("beq","000100","ij"),("j","000010","j"),("add","000000","r","00000","100000"),
        ("and","000000","r","00000","100100"),("addi","001000","i"),("andi","001100","i"),
        ("or","000000","r","00000","100101"),("slt","000000","r","00000","101011"),
        ("jal","000011","j"),("jr","000000","r","00000","001000"),("lip","010100","i"),
        ("dwr","010101","i"),("li","001000","i"),("mv","001000","i"),("inc","001000","i"),
        ("sub","000000","r","00000","100010"),("ladr","001000","i"),("dec","001000","i")]
        # nop unter jumps

reg = [
    ("$zero",0),
    ("$at",1),
    ("$v0",2),
    ("$v1",3),
    ("$a0",4),
    ("$a1",5),
    ("$a2",6),
    ("$a3",7),
    ("$t0",8),
    ("$t1",9),
    ("$t2",10),
    ("$t3",11),
    ("$t4",12),
    ("$t5",13),
    ("$t6",14),
    ("$t7",15),
    ("$s0",16),
    ("$s1",17),
    ("$s2",18),
    ("$s3",19),
    ("$s4",20),
    ("$s5",21),
    ("$s6",22),
    ("$s7",23),
    ("$t8",24),
    ("$t9",25),
    ("$k0",26),
    ("$k1",27),
    ("$gp",28),
    ("$sp",29), # using it for function stack data starting at : end of static program data
    ("$fp",30), # using it for dynamic data, starting at 0xffff, memory management required... argh
    ("$ra",31)
]

# Memory Management:
# Momory Block: Statisch mit Wortgröße 4 (4 * 32bit), als static gespeichert, um Vergößerung nachher easy zu machen!
# wäre eher praktisch sich für gegner und bullets jewails statisch 32 structs zu alloziieren und in ner größeren struktur die dann die anzahl noch speicher zu verwalten
#--block end--
# 0x8 Data
# 0x9 Data
# 0xA Data
# 0xB Free
#--block start--
#--block end--
# 0xC Data
# 0xD Data
# 0xE Data
# 0xF Free
#--block start--




def getReg(string):
    for register in reg:
        if(string == register[0]):
            return register[1]
    exit("Error Register: "+string+" not found.")

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

def numToInt(string):
    if(not string):
        exit("empty string")
    if(len(string)<3):
        return int(string,10)
    if(string[:2] == "0b"):
        return int(string,2)
    if(string[:2] == "0x"):
        return int(string,16)
    return int(string)

def inList(list,elem):
    for entry in list:
        #print (entry)
        if(elem == entry[0]):
            return entry[1]
    return -1

def passCommand(string, pos_comp,pos_src):
    tokens = string.split()
    if(len(tokens)==0):
        return ""        
    for cmd in cmds:
        if(tokens[0] == cmd[0]):
            break
    if(tokens[0] != cmd[0]):
        exit("Failed at Line: %d" % pos_src)
    result = ""
    #Spezialbefehle
    if(cmd[2] == "s"):
        if(cmd[0] == "nop"):
            result = "00000000000000000000000000000000"
        elif(cmd[0] == "const"):
            result = int2bin(int(tokens[2]),32)
        elif(cmd[0] == ":"):
            result = ""
        else:
            return ""
    else:
        #Normale Befehle
        result = cmd[1]
        if(cmd[2] == "r"):
            if(cmd[0]=="jr"):
                result += int2bin(getReg(tokens[1]),5)+int2bin(0,10)+cmd[3]+cmd[4]
            else:
                result += int2bin(getReg(tokens[2]),5)+int2bin(getReg(tokens[3]),5)+int2bin(getReg(tokens[1]),5)+cmd[3]+cmd[4]
        elif(cmd[2] == "i"):
            if(cmd[0]=="lw" or cmd[0]=="sw"):
                posEntryInList = inList(consts,tokens[3])
                if(posEntryInList != -1):
                    result += int2bin(getReg(tokens[2]),5)+int2bin(getReg(tokens[1]),5)+int2bin(posEntryInList,16)
                else:
                    #exit("Label not found "+tokens[3]+" at pos: "+str(pos_src))
                    result += int2bin(getReg(tokens[2]),5)+int2bin(getReg(tokens[1]),5)+int2bin(numToInt(tokens[3]),16)    
            elif(cmd[0] == "lip"):
                result += int2bin(0,5)+int2bin(getReg(tokens[1]),5)+int2bin(0,16)
            elif(cmd[0] == "dwr"):
                result += int2bin(getReg(tokens[2]),5)+int2bin(getReg(tokens[1]),5)+int2bin(0,16)
            elif(cmd[0] == "li"):
                result += int2bin(0,5)+int2bin(getReg(tokens[1]),5)+int2bin(numToInt(tokens[2]),16)
            elif(cmd[0] == "mv"):
                result += int2bin(getReg(tokens[2]),5)+int2bin(getReg(tokens[1]),5)+int2bin(0,16)
            elif(cmd[0] == "inc"):
                result += int2bin(getReg(tokens[1]),5)+int2bin(getReg(tokens[1]),5)+int2bin(1,16)
            elif(cmd[0] == "dec"):
                result += int2bin(getReg(tokens[1]),5)+int2bin(getReg(tokens[1]),5)+int2bin(-1,16)
            elif(cmd[0] == "ladr"):
                result += int2bin(0,5)+int2bin(getReg(tokens[1]),5)
                pos_label = inList(labels,tokens[2])
                if(pos_label != -1):
                        #print("pos_comp "+str(pos_comp)+" pos_label "+str(pos_label))
                        result += int2bin(pos_label,16)
                else:
                    print("lable not found: "+tokens[2]+" pos "+str(pos_src))
            elif(cmd[0] == "addi" and len(tokens)==3):
                result += int2bin(getReg(tokens[1]),5)+int2bin(getReg(tokens[1]),5)+int2bin(numToInt(tokens[2]),16)
            else:
                result += int2bin(getReg(tokens[2]),5)+int2bin(getReg(tokens[1]),5)+int2bin(numToInt(tokens[3]),16)
        elif(cmd[2] == "ij"):
            result += int2bin(getReg(tokens[2]),5)+int2bin(getReg(tokens[1]),5)
            pos_label = inList(labels,tokens[3])
            if(pos_label != -1):
                    jumpLengt = pos_label-pos_comp-2
                    #print("pos_comp "+str(pos_comp)+" pos_label "+str(pos_label))
                    result += int2bin(jumpLengt,16)
            else:
                print("lable not found: "+tokens[3]+" pos "+str(pos_src))
        elif(cmd[2] == "j"):
            if(inList(labels,tokens[1]) != -1):
                    result += int2bin(inList(labels,tokens[1]),26)
            else:
                print("lable not found: "+tokens[1]+" pos "+str(pos_src))

    space = ""
    for i in range(0,100-len(string[:-1])-len(hex(pos_comp)[2:])):
        space = space+" "
    if(cmd[0] != ":"):
        print("#"+hex(pos_comp)[2:]+": "+string[:-1]+space+"HEX: "+"{0:0>8X}".format(int(result, 2))+"   BIN: "+result)
    else:
        print("#"+hex(pos_comp)[2:]+": "+string[:-1]+space+"HEX: "+"{0:0>8X}".format(int(int2bin(pos_comp,32), 2))+"   BIN: "+int2bin(pos_comp,32))
    return result


def passConstant(string,pos_comp,pos_src):
    tokens = string.split()
    if(len(tokens)==0):
        return ":";        
    for cmd in cmds:
        if(tokens[0] == cmd[0]):
            break
    if(tokens[0] != cmd[0]):
        exit("Failed at Line: %d" % pos_src)
    #Befehle
    if(cmd[0] == ":"):
        labelPos = inList(labels,tokens[1])
        if(labelPos != -1):
            exit("Double Lable "+tokens[1]+" at Line: %d" % pos_src)
        labels.append((tokens[1],pos_comp))
        space = ""
        for i in range(0,100-len(string[:-1])-len(hex(pos_comp)[2:])):
            space = space+" "
        print("#"+hex(pos_comp)[2:]+": "+string[:-1]+space+"HEX: "+"{0:0>8X}".format(int(int2bin(pos_comp,32), 2))+"   BIN: "+int2bin(pos_comp,32))
        return ":"
    elif(cmd[0] == "const"):
        constPos = inList(consts,tokens[1])
        if(constPos != -1):
            exit("Double Constant "+tokens[1]+" at Line: %d" % pos_src)
        consts.append((tokens[1],pos_comp))
        space = ""
        for i in range(0,100-len(string[:-1])-len(hex(pos_comp)[2:])):
            space = space+" "
        print("#"+hex(pos_comp)[2:]+": "+string[:-1]+space+"HEX: "+"{0:0>8X}".format(int(int2bin(int(tokens[2]),32), 2))+"   BIN: "+int2bin(int(tokens[2]),32))
        return "const"
    elif(cmd[0] == "" or cmd[0] == "#"):
        return ":"

def main():
    f_src = open("src.txt","rt")
    f_comp = open("compiled","wb")
    pos_comp = 0
    pos_src = 1

    #Gehe alle Konstanten durch, adde sie als Komponenten
    print("__CONST__")
    for line in f_src:
        const = passConstant(line,pos_comp,pos_src)
        if(const != ":"):
            pos_comp+=1
        pos_src+=1
    #neu öffnen, weil lines alle durch sind
    f_src.close()
    f_src = open("src.txt","rt")
    pos_comp = 0
    pos_src = 1
    #gehe programm code durch
    print("__PROGAM__")
    for line in f_src:
        cmd = passCommand(line,pos_comp,pos_src)
        if(cmd and cmd != ""):
            strToBin(cmd).tofile(f_comp)
            pos_comp += 1
        pos_src

    f_src.close()
    f_comp.close()

main()



















