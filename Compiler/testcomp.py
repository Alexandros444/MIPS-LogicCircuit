def passFile(src_file,dest_file):
    src_lines = []
    for line in src_file:
        src_lines.append(line)
    cmd_lines = []
    for line in src_lines:
        tokens = line.split()
        if(tokens and tokens[0][0] != '#'):
            if("\n" in line):
                cmd_lines.append(line[:-1])
            else:
                cmd_lines.append(line[:])
    for line in cmd_lines:
        print(line)


##f = open("src.txt","rt")
##passFile(f,f)


def add(a,b):
    a += b
    print(a)

#s = 1
#p = 2
#add(s,p)
#print(s)


#cmds = [("hello",2)]
#for cmd in cmds:
#    print (cmd)


for i in range(0,1):
    print("ad")