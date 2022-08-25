import array
file2 = open("liitle vs big","wb")

byte = 0x524F5247
em = 0
file2.write(byte.to_bytes(4, byteorder='big'))
file2.write(em.to_bytes(4, byteorder='big'))
file2.write(byte.to_bytes(4, byteorder='little'))

file2.close()











#newFileBytes = [65]
#bytes = bytearray(newFileBytes)
#file.write(bytes)