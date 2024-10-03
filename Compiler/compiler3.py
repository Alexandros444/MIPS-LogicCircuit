cmds = [(":","","s"),           # Label         - : label_x
        ("nop","","s"),         # No Operation  - nop
        ("const","","s"),       # Constante im Speicher, Statisch       - const abc <init_wert> (abc referiert im weiteren Code auf die Speicherstelle von <init_wert>)
        ("lw","100011","i"),    # Load Word     - lw $dest $src <src+_imm>
        ("sw","101011","i"),
        ("beq","000100","i"),
        ("j","000010","j"),
        ("add","000000","r","00000","100000"),
        ("and","000000","r","00000","100100"),
        ("addi","001000","i"),
        ("andi","001100","i"),
        ("or","000000","r","00000","100101"),
        ("slt","000000","r","00000","101011"),
        ("jal","000011","j"),("jr","000000","r","00000","001000"),("lip","010100","i"), # LIP Load Input
        ("dwr","010101","i"),("li","001000","i"),("mv","001000","i"),("inc","001000","i"),
        ("sub","000000","r","00000","100010"),("ladr","001000","i"),("dec","001000","i"),
        ("bne","000101","i"),("blt","","p"),("bgt","","p"),("bge","","p"),("ble","","p"),
        ("if","","p"),("ifend","","p"),("while","","p"),("whileend","","p"),("call","","p"),
        ("spstore","","p"),("spload","","p")]
        # extra methodennamen, und scopes -> keine label mehr
        # Konstanten $t0 == 1 usw bei ifs und whiles hinzufühen
        # Konstanten $t0 == abc usw hinzufügen


reg = [("$zero",0), # Zero Register
       ("$at",1), # Unused
       ("$v0",2),("$v1",3),                     # Return Register von Funktion
       ("$a0",4),("$a1",5),("$a2",6),("$a3",7), # Argum,ente Register Für Funktion
       ("$t0",8),("$t1",9),("$t2",10),("$t3",11),("$t4",12),("$t5",13),("$t6",14),("$t7",15),("$t8",24),("$t9",25), # Temporäre Register
       ("$s0",16),("$s1",17),("$s2",18),("$s3",19),("$s4",20),("$s5",21),("$s6",22),("$s7",23), # Persistente Register
       ("$k0",26),("$k1",27), # Vergleich Register (Set less Than, oder Swap)
       ("$gp",28), # Unused
       ("$sp",29), # using it for function stack data starting at : end of static program data
       ("$fp",30), # using it for dynamic data, starting at 0xffff, memory management required... argh
       ("$ra",31)  # always the return adress from function calls
]


# Function
# save ra on stack
# save s0 - s7 on stack
# inc sp



# return values in a0 - a3
# dec sp
# restore ra
# restore s0 - s7
# jump ra

# Example

# : func_update_bullet_pos
#     sw $ra $sp 0
#     sw $s0 $sp 1
#     sw $s1 $sp 2
#     addi $sp $sp 3

#     Do Stuff

#     addi $sp $sp -3
#     lw $ra $sp 0
#     lw $s0 $sp 1
#     lw $s1 $sp 2
#     jr $ra

# IF





# Ziel : Compiler von Python like to Assembly to Binary mit Compiler2.py