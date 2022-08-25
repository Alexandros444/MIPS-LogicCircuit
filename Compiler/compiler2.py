#!/usr/bin/env python3

import array
from os import close

labels = [("zero",0)]
consts = [("zero",0)]

cmds = [(":","","s"),("nop","","s"),("const","","s"),("lw","100011","i"),
        ("sw","101011","i"),("beq","000100","i"),("j","000010","j"),("add","000000","r","00000","100000"),
        ("and","000000","r","00000","100100"),("addi","001000","i"),("andi","001100","i"),
        ("or","000000","r","00000","100101"),("slt","000000","r","00000","101011"),
        ("jal","000011","j"),("jr","000000","r","00000","001000"),("lip","010100","i"),
        ("dwr","010101","i"),("li","001000","i"),("mv","001000","i"),("inc","001000","i"),
        ("sub","000000","r","00000","100010"),("ladr","001000","i"),("dec","001000","i"),
        ("bne","000101","i"),("blt","","p"),("bgt","","p"),("bge","","p"),("ble","","p"),
        ("if","","p"),("ifend","","p"),("while","","p"),("whileend","","p"),("call","","p"),
        ("spstore","","p"),("spload","","p")]
        # extra methodennamen, und scopes -> keine label mehr
        # Konstanten $t0 == 1 usw bei ifs und whiles hinzufühen
        # Konstanten $t0 == abc usw hinzufügen


reg = [("$zero",0),("$at",1),("$v0",2),("$v1",3),("$a0",4),("$a1",5),("$a2",6),("$a3",7),("$t0",8),("$t1",9),("$t2",10),
        ("$t3",11),("$t4",12),("$t5",13),("$t6",14),("$t7",15),("$s0",16),("$s1",17),("$s2",18),("$s3",19),("$s4",20),
        ("$s5",21),("$s6",22),("$s7",23),("$t8",24),("$t9",25),("$k0",26),("$k1",27),("$gp",28),
        ("$sp",29), # using it for function stack data starting at : end of static program data
        ("$fp",30), # using it for dynamic data, starting at 0xffff, memory management required... argh
        ("$ra",31)  # always the return adress from function calls
]

# Memory Management:
# Momory Block: startet mit gesamter größe, also minumum 3, dann frei oder belegt, dann kontent
#--block end--
# 0x8 Data
# 0x9 Free 1 / 0
# 0xA Size 0x3
#--block start--
#--block end--
# 0xB Data
# 0xC Data
# 0xD Data
# 0xE Free 1 / 0
# 0xF Size 0x5
#--block start--
# Next block ist dann $fp - sizof(Block)
# durchgegangen wird der speicher von unten nach oben

DEBUG_NUMBER = 0
LINE_NUMBER = 0
SCOPES = []
SCOPE_ID = 0
# scope datenstruktur mit pfad. also (0,1,2) oder (0,1,3,5) für ein anderes scope, oder (0,1) oder (0) für das grundcope
# scope ID's werden einfach immer incrementiert pro scope
IF_COUNT = 0
IF_LABLES = []

WHILE_COUNT = 0
WHILE_LABLES = []

def openScope():
    global SCOPES
    global SCOPE_ID
    SCOPE_ID += 1
    if(len(SCOPES) == 0):
        SCOPES.append((0,))        
    else:
        SCOPES.append((SCOPES[-1:][0])+(SCOPE_ID,))

def holdScope():
    global SCOPES
    if(len(SCOPES) == 0):
        SCOPES.append((0,))        
    else:
        SCOPES.append(SCOPES[-1:][0])

def holdScopeNum(num):
    global SCOPES
    for i in range(0,num):
        holdScope()

def closeScope():
    global SCOPES
    SCOPES.append(SCOPES[-1:][0][:-1])
    
def getScopeAtPos(lineNumber):
    return SCOPES[lineNumber][-1:]

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

def spaces(string,lengt):
    space = ""
    for i in range(0,lengt-len(string)):
        space = space+" "
    return space
# TODO
def printDebugLine(cmd,args,binLine):
    lineToPrint = str(LINE_NUMBER)+": "
    #print(len(SCOPES))
    #print(LINE_NUMBER)
    for touple in SCOPES[DEBUG_NUMBER][:-1]:
        lineToPrint += "    "
    if(cmd != ":"):
        lineToPrint += cmd+" "
    else:
        lineToPrint += ": "
    for arg in args:
        lineToPrint += arg+" "
    lineToPrint += spaces(lineToPrint + hex(LINE_NUMBER),50)+hex(LINE_NUMBER)+": "
    if(cmd == ":"):
        lineToPrint += "{0:0>8X}".format(int(int2bin(LINE_NUMBER,32), 2))+"   "+int2bin(LINE_NUMBER,32)
    elif(cmd == "const"):
        lineToPrint += "{0:0>8X}".format(int(int2bin(numToInt(args[1]),32), 2))+"   "+int2bin(numToInt(args[1]),32)
    else:
        lineToPrint += "{0:0>8X}".format(int(binLine, 2))+"   "+binLine
    print(lineToPrint)

def getBinReg(reg_s):
    return int2bin(getReg(reg_s))

def numToBin(num_s):
    return int2bin(numToInt(num_s))

def cmdLineR(cmd,rd,rs,rt):
    return (cmd,rd,rs,rt)

def cmdLineI(cmd,rt,rs,imm_or_label):
    return (cmd,rt,rs,imm_or_label)

def cmdLineJ(cmd,label):
    return (cmd,label)

# func und shamt sind schon binary
def compLineR(cmd_31_26,rs_25_21,rt_20_16,rd_15_11,shamt_10_6,func_5_0):
    return getCommandOfLine(cmd_31_26)[1] + getBinReg(rs_25_21) + getBinReg(rt_20_16) + getBinReg(rd_15_11) + shamt_10_6 + func_5_0

def compLineI(cmd_31_26,reg_25_21,reg_20_16,imm_15_0):
    return getCommandOfLine(cmd_31_26)[1] + getBinReg(reg_25_21) + getBinReg(reg_20_16) + numToBin(imm_15_0)

def compLineJ(cmd_31_26,jmp_25_0):
    return getCommandOfLine(cmd_31_26) + numToBin(jmp_25_0)

def ifCommand(reg0, operator, reg1):
    global IF_COUNT
    cmd_lines = []
    #Vergleich mit hardcode konstanten
    if(reg1[:1] != "$"):
        if(reg1.isdigit() or (len(reg1)>1 and reg1[1:].isdigit())):
            cmd_lines.append(cmdLineI("addi","$at","$zero",reg1))
        else:
            cmd_lines.append(cmdLineI("lw","$at","$zero",reg1))
        reg1 = "$at"
    # invertiere alle Bedingungen, branche zu label, falls bedingung falsch
    if(operator == "=="):
        cmd_lines.append(cmdLineI("bne",reg0,reg1,"ifend_"+str(IF_COUNT)))
    elif(operator == "!="):
        cmd_lines.append(cmdLineI("beq",reg0,reg1,"ifend_"+str(IF_COUNT)))
    elif(operator == "<"):
        cmd_lines.append(cmdLineR("slt","$at",reg0,reg1))
        cmd_lines.append(cmdLineI("beq","$at","$zero","ifend_"+str(IF_COUNT)))
    elif(operator == ">"):
        cmd_lines.append(cmdLineR("slt","$at",reg1,reg0))
        cmd_lines.append(cmdLineI("beq","$at","$zero","ifend_"+str(IF_COUNT)))
    elif(operator == "<="):
        cmd_lines.append(cmdLineR("slt","$at",reg1,reg0))
        cmd_lines.append(cmdLineI("bne","$at","$zero","ifend_"+str(IF_COUNT)))
    elif(operator == ">="):
        cmd_lines.append(cmdLineR("slt","$at",reg0,reg1))
        cmd_lines.append(cmdLineI("bne","$at","$zero","ifend_"+str(IF_COUNT)))
    else:
        exit("if operator not known: "+operator)
    cmd_lines.append(("nop",""))

    IF_LABLES.append("ifend_"+str(IF_COUNT))
    IF_COUNT+=1
    return(cmd_lines)

def whileCommand(reg0, operator, reg1):
    global WHILE_COUNT
    cmd_lines = []
    #Vergleich mit hardcode konstanten
    if(reg1[:1] != "$"):
        if(reg1.isdigit() or (len(reg1)>1 and reg1[1:].isdigit())):
            cmd_lines.append(cmdLineI("addi","$at","$zero",reg1))
        else:
            cmd_lines.append(cmdLineI("lw","$at","$zero",reg1))
        reg1 = "$at"
    # invertiere alle Bedingungen, branche zu label, falls bedingung falsch
    cmd_lines.append((":","whilebeg_"+str(WHILE_COUNT)))
    if(operator == "=="):
        cmd_lines.append(cmdLineI("bne",reg0,reg1,"whileend_"+str(WHILE_COUNT)))
    elif(operator == "!="):
        cmd_lines.append(cmdLineI("beq",reg0,reg1,"whileend_"+str(WHILE_COUNT)))
    elif(operator == "<"):
        cmd_lines.append(cmdLineR("slt","$at",reg0,reg1))
        cmd_lines.append(cmdLineI("beq","$at","$zero","whileend_"+str(WHILE_COUNT)))
    elif(operator == ">"):
        cmd_lines.append(cmdLineR("slt","$at",reg1,reg0))
        cmd_lines.append(cmdLineI("beq","$at","$zero","whileend_"+str(WHILE_COUNT)))
    elif(operator == "<="):
        cmd_lines.append(cmdLineR("slt","$at",reg1,reg0))
        cmd_lines.append(cmdLineI("bne","$at","$zero","whileend_"+str(WHILE_COUNT)))
    elif(operator == ">="):
        cmd_lines.append(cmdLineR("slt","$at",reg0,reg1))
        cmd_lines.append(cmdLineI("bne","$at","$zero","whileend_"+str(WHILE_COUNT)))
    else:
        exit("while operator not known: "+operator)
    cmd_lines.append(("nop",""))

    WHILE_LABLES.append(("whilebeg_"+str(WHILE_COUNT),"whileend_"+str(WHILE_COUNT)))
    WHILE_COUNT+=1
    return(cmd_lines)

def whileEnd():
    cmd_lines = []
    whiletouple = WHILE_LABLES.pop()
    cmd_lines.append(cmdLineJ("j",whiletouple[0]))
    cmd_lines.append(("nop",""))
    cmd_lines.append((":",whiletouple[1]))
    return(cmd_lines)

def callCommand(args):
    cmd_lines = []
    pre_cmd_lines = []
    return_lines = []
    argument_lines = []
    argcount = 0
    if(args[0][:1] == "$"):
        return_lines.append((cmdLineI("addi",args[0],"$v0","0")))
        argcount+=1
        if(args[1][:1] == "$"):
            return_lines.append((cmdLineI("addi",args[1],"$v1","0")))
            argcount+=1
    pre_cmd_lines.append((cmdLineJ("jal",args[argcount])))
    pre_cmd_lines.append(("nop",""))
    if(len(args) > argcount+1 and args[argcount+1][:1]=="$"):
        argument_lines.append((cmdLineI("addi","$a0",args[argcount+1],"0")))
    if(len(args) > argcount+2 and args[argcount+2][:1]=="$"):
        argument_lines.append((cmdLineI("addi","$a1",args[argcount+2],"0")))
    if(len(args) > argcount+3 and args[argcount+3][:1]=="$"):
        argument_lines.append((cmdLineI("addi","$a2",args[argcount+3],"0")))
    for line in argument_lines:
        cmd_lines.append(line)
    for line in pre_cmd_lines:
        cmd_lines.append(line)
    for line in return_lines:
        cmd_lines.append(line)
    return cmd_lines


def stackPointerStore(args):
    cmd_lines = []
    argcount = 0
    for arg in args:
        if(arg[:1] != "$"):break
        cmd_lines.append(cmdLineI("sw",arg,"$sp",str(argcount)))
        argcount += 1
    cmd_lines.append(cmdLineI("addi","$sp","$sp",str(argcount)))
    return cmd_lines

def stackPointerLoad(args):
    cmd_lines = []
    load_lines = []
    argcount = 0
    for arg in args:
        if(arg[:1] != "$"):break
        load_lines.append(cmdLineI("lw",arg,"$sp",str(argcount)))
        argcount += 1
    cmd_lines.append(cmdLineI("addi","$sp","$sp",str(-argcount)))
    for line in load_lines:
        cmd_lines.append(line)
    return cmd_lines

def printDebugCmdLine(cmd_t):
    lineToPrint = str(LINE_NUMBER)+": "
    if(cmd_t[0] != ":"):
        lineToPrint += cmd_t[0]+" "
    else:
        lineToPrint += "Label "
    for arg in cmd_t[1:]:
        lineToPrint += arg+" "
    print(lineToPrint)

def getNumLinesOfCmd(cmd):
    if(cmd == ":"):
        return 0
    #elif(cmd == "beq" or cmd == "j" or cmd == "jal" or cmd == "jr"):
    #    return 2   // wird auseinandergezogen, in cmdLines, dadurch gibt es nur 0 oder 1. 
    else:
        return 1

def getCommandOfLine(line):
    if(line == "nop"):
        token = "nop"
    else:
        token = line.split()[0]
    for cmd in cmds:
        if(token == cmd[0]):
            return cmd
    return None

def getCommandOfCmd(cmd):
    for cmd_temp in cmds:
        if(cmd == cmd_temp[0]):
            return cmd_temp
    return None

def writeToFile(file, string):
    for line in string:
        strToBin(line).tofile(file)

# Isoliert die command lines, argumente und struktur, löst pseudobefehle in richtige befehle auf, es bleiben nur const und label noch gleich
def createCmdLines(cmd_t,args):
    cmd = cmd_t[0]
    cmd_lines = []
    #Spezialbefehle
    if(cmd_t[2] == "s"):
        if(cmd == "nop"):
            cmd_lines.append((cmd,""))
        elif(cmd == "const"):
            cmd_lines.append((cmd,args[0],args[1]))
        elif(cmd == ":"):
            cmd_lines.append((cmd,args[0]))
    #Normale Befehle
    # R-type
    if(cmd_t[2] == "r"):
        if(cmd=="jr"):
            cmd_lines.append((cmdLineR(cmd,args[0],"$zero","$zero")))
            cmd_lines.append(("nop",""))
        else:
            cmd_lines.append((cmdLineR(cmd,args[0],args[1],args[2])))
    # I-Type
    if(cmd_t[2] == "i"):
        if(cmd=="lw" or cmd=="sw"):
            # check for lw $reg $reg imm vs lw $reg imm as not offset shortcut
            if(args[1][:1] == "$"):
                # normal lw $reg $reg imm
                cmd_lines.append((cmdLineI(cmd,args[0],args[1],args[2])))
            else:
                # shortcut lw $reg imm
                cmd_lines.append((cmdLineI(cmd,args[0],"$zero",args[1])))
        elif(cmd == "ladr"):
            cmd_lines.append((cmdLineI(cmd,args[0],"$zero",args[1])))
        elif(cmd == "lip"):
            cmd_lines.append((cmdLineI(cmd,args[0],"$zero","0")))
        elif(cmd == "dwr"):
            cmd_lines.append((cmdLineI(cmd,args[0],args[1],"0")))
        elif(cmd == "li"):
            cmd_lines.append((cmdLineI("addi",args[0],"$zero",args[1])))
        elif(cmd == "mv"):
            cmd_lines.append((cmdLineI("addi",args[0],args[1],"0")))
        elif(cmd == "inc"):
            cmd_lines.append((cmdLineI("addi",args[0],args[0],"1")))
        elif(cmd == "dec"):
            cmd_lines.append((cmdLineI("addi",args[0],args[0],"-1")))
        elif(cmd == "addi" or cmd == "andi"):
            # check for shortcut
            if(args[1][:1]=="$"):
                cmd_lines.append((cmdLineI(cmd,args[0],args[1],args[2])))
            else:
                cmd_lines.append((cmdLineI(cmd,args[0],args[0],args[1])))
        elif(cmd == "beq" or cmd == "bne"):
            cmd_lines.append((cmdLineI(cmd,args[0],args[1],args[2])))
            cmd_lines.append(("nop",""))
    # J-Type
    if(cmd_t[2] == "j"):
        if(cmd == "j" or cmd == "jal"):
            cmd_lines.append((cmdLineJ(cmd,args[0])))
            cmd_lines.append(("nop",""))
            
    # P-Type, mehrzeilige pseudobefehle #TODO
    if(cmd_t[2] == "p"):
        if(cmd == "blt"):
            cmd_lines.append(cmdLineR("slt","$at",args[0],args[1]))
            cmd_lines.append(cmdLineI("bne","$at","$zero",args[2]))
            cmd_lines.append(("nop",""))
        elif(cmd == "bgt"):
            cmd_lines.append(cmdLineR("slt","$at",args[1],args[0]))
            cmd_lines.append(cmdLineI("bne","$at","$zero",args[2]))
            cmd_lines.append(("nop",""))
        elif(cmd == "ble"):
            cmd_lines.append(cmdLineR("slt","$at",args[1],args[0]))
            cmd_lines.append(cmdLineI("beq","$at","$zero",args[2]))
            cmd_lines.append(("nop",""))
        elif(cmd == "bge"):
            cmd_lines.append(cmdLineR("slt","$at",args[0],args[1]))
            cmd_lines.append(cmdLineI("beq","$at","$zero",args[2]))
            cmd_lines.append(("nop",""))
        elif(cmd == "if"):
            for line in ifCommand(args[0],args[1],args[2]):
                cmd_lines.append(line)
            holdScopeNum(len(cmd_lines)-1)
            openScope()
        elif(cmd == "ifend"):
            cmd_lines.append((":",IF_LABLES.pop()))
            closeScope()
        elif(cmd == "while"):
            for line in whileCommand(args[0],args[1],args[2]):
                cmd_lines.append(line)
            holdScopeNum(len(cmd_lines)-1)
            openScope()
        elif(cmd == "whileend"):
            for line in whileEnd():
                cmd_lines.append(line)
            holdScopeNum(len(cmd_lines)-1)
            closeScope()
        elif(cmd == "call"):
            for line in callCommand(args):
                cmd_lines.append(line)
        elif(cmd == "spstore"):
            for line in stackPointerStore(args):
                cmd_lines.append(line)
        elif(cmd == "spload"):
            for line in stackPointerLoad(args):
                cmd_lines.append(line)
    if(cmd != "if" and cmd != "ifend" and cmd != "while" and cmd != "whileend"):
        holdScopeNum(len(cmd_lines))
    #print(cmd_lines)
    #print(SCOPES)
    # Debug
    #for line in cmd_lines:
    #    printDebugCmdLine(line)
    return cmd_lines

# cmd der Kommand, tokens die argumente des Commands
def createReferenz(cmd_t):
    cmd = cmd_t[0]
    args = []
    for arg in cmd_t[1:]:
        args.append(arg)
    #Befehle
    if(cmd == ":"):
        # wenn ein label definiert wurde
        labelPos = inList(labels,args[0])
        if(labelPos != -1):
            exit("Double Lable "+args[0])
        labels.append((args[0],LINE_NUMBER))
        printDebugLine(cmd,args,"")
    elif(cmd == "const"):
        constPos = inList(consts,args[0])
        if(constPos != -1):
            exit("Double Constant "+args[0])
        consts.append((args[0],LINE_NUMBER))
        printDebugLine(cmd,args,"")

def createCompiledLines(cmd_code):
    cmd = cmd_code[0]
    cmd_t = getCommandOfCmd(cmd)
    if(cmd_t == None):
        print("comp lines got cmd_code: "+cmd_code)
    args = []
    for arg in cmd_code[1:]:
        args.append(arg)
    compiled_line = ""
    #Spezialbefehle
    if(cmd_t[2] == "s"):
        if(cmd == "nop"):
            compiled_line += int2bin(0,32)
        elif(cmd == "const"):
            compiled_line += int2bin(numToInt(args[1]),32)
        elif(cmd == ":"):
            compiled_line = ""
    else:
        #Normale Befehle
        # Füge binär-cmd-code an anfang von der line ein
        compiled_line += cmd_t[1]
        # R-type
        if(cmd_t[2] == "r"):
            if(cmd=="jr"):
                compiled_line += int2bin(getReg(args[0]),5)+int2bin(0,10)+cmd_t[3]+cmd_t[4]
            else:
                compiled_line += int2bin(getReg(args[1]),5)+int2bin(getReg(args[2]),5)+int2bin(getReg(args[0]),5)+cmd_t[3]+cmd_t[4]
        # I-Type
        if(cmd_t[2] == "i"):
            if(cmd=="lw" or cmd=="sw"):
                posEntryInList = inList(consts,args[2])
                if(posEntryInList != -1):
                    compiled_line += int2bin(getReg(args[1]),5)+int2bin(getReg(args[0]),5)+int2bin(posEntryInList,16)
                else:
                    #exit("Label not found "+args[2])
                    compiled_line += int2bin(getReg(args[1]),5)+int2bin(getReg(args[0]),5)+int2bin(numToInt(args[2]),16)
            elif(cmd == "lip"):
                compiled_line += int2bin(0,5)+int2bin(getReg(args[0]),5)+int2bin(0,16)
            elif(cmd == "dwr"):
                compiled_line += int2bin(getReg(args[1]),5)+int2bin(getReg(args[0]),5)+int2bin(0,16)
            elif(cmd == "li"):
                compiled_line += int2bin(0,5)+int2bin(getReg(args[0]),5)+int2bin(numToInt(args[1]),16)
            elif(cmd == "mv"):
                compiled_line += int2bin(getReg(args[1]),5)+int2bin(getReg(args[0]),5)+int2bin(0,16)
            elif(cmd == "inc"):
                compiled_line += int2bin(getReg(args[0]),5)+int2bin(getReg(args[0]),5)+int2bin(1,16)
            elif(cmd == "dec"):
                compiled_line += int2bin(getReg(args[0]),5)+int2bin(getReg(args[0]),5)+int2bin(-1,16)
            elif(cmd == "ladr"):
                compiled_line += int2bin(0,5)+int2bin(getReg(args[0]),5)
                pos_label = inList(labels,args[2])
                if(pos_label != -1):
                        #print("pos_comp "+str(pos_comp)+" pos_label "+str(pos_label))
                        compiled_line += int2bin(pos_label,16)
                else:
                    print("lable not found: "+args[2])
            elif(cmd == "addi"):
                compiled_line += int2bin(getReg(args[1]),5)+int2bin(getReg(args[0]),5)+int2bin(numToInt(args[2]),16)
            elif(cmd == "andi"):
                compiled_line += int2bin(getReg(args[1]),5)+int2bin(getReg(args[0]),5)+int2bin(numToInt(args[2]),16)
            elif(cmd == "beq" or cmd == "bne"):
                compiled_line += int2bin(getReg(args[1]),5)+int2bin(getReg(args[0]),5)
                pos_label = inList(labels,args[2])
                if(pos_label):
                        jumpLengt = pos_label-LINE_NUMBER-2
                        #print("pos_comp "+str(pos_comp)+" pos_label "+str(pos_label))
                        compiled_line += int2bin(jumpLengt,16)
                else:
                    print("lable not found: "+args[2])
        if(cmd_t[2] == "j"):
            if(cmd == "j"):
                label_pos = inList(labels,args[0])
                if(label_pos != -1):
                        compiled_line += int2bin(label_pos,26)
                else:
                    print("Jump lable not found: "+args[0])
            if(cmd == "jal"):
                if(inList(labels,args[0])):
                        compiled_line += int2bin(inList(labels,args[0]),26)
                else:
                    print("lable not found: "+args[0])
    printDebugLine(cmd,args,compiled_line)
    return compiled_line


def passFile(src_file,dest_file):
    global LINE_NUMBER
    global DEBUG_NUMBER
    #Get all Source file lines
    src_lines = []
    for line in src_file:
        src_lines.append(line)
    #Get only the Commands of them
    code_lines = []
    for line in src_lines:
        tokens = line.split()
        if(tokens and tokens[0][0] != '#'):
            if("\n" in line):
                code_lines.append(line[:-1])
            else:
                code_lines.append(line[:])
    #Command-lines verarbeiten

    cmd_lines = []
    #print("__Pre__")
    for line in code_lines:
        for cmd_line in createCmdLines(getCommandOfLine(line),line.split()[1:]):
            cmd_lines.append(cmd_line)
    print("__Consts__")
    for cmd in cmd_lines:
        passLineOfFile(cmd,True)
    print("__Program__")
    #Dann nicht referenzen, und erstellen von compiled_lines, zurücksetzen der Line_Number, die gezählt wurde
    LINE_NUMBER = 0
    DEBUG_NUMBER = 0
    compiled_lines = []
    for cmd in cmd_lines:
        for comp_line in passLineOfFile(cmd, False):
            if(getNumLinesOfCmd(cmd[0]) != 0):
                compiled_lines.append(comp_line)
    #Dann in die Datei schreiben
    writeToFile(dest_file,compiled_lines)

# gibt x lines aus, die anstelle einer line im source code dann im compiled code stehen
def passLineOfFile(cmd_t, is_reference):
    global LINE_NUMBER
    global DEBUG_NUMBER
    # für alle referenz strukturen gehe dies beim ersten mal durch, beim nächsten mal dann die ganzen normalen befehle und verweise auf diese referenzen
    compiled_lines = []
    if(is_reference):
        createReferenz(cmd_t)
    else:
        comp_line = createCompiledLines(cmd_t)
        if(comp_line):
            compiled_lines.append(comp_line)
    #print(cmd_t)
    LINE_NUMBER += getNumLinesOfCmd(cmd_t[0])
    DEBUG_NUMBER += 1
    return compiled_lines
    

def main():
    global LINE_NUMBER
    LINE_NUMBER = 0
    src_file = open("src3.txt","rt")
    compiled_file = open("srcCompiled","wb")
    passFile(src_file,compiled_file)
    src_file.close()
    compiled_file.close()

main()