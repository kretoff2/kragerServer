import random

def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def coding(message:str, KEY):
    bits_message = text_to_bits(message)
    key = format(KEY, 'b')
    key_len = len(key)
    i = len(bits_message) % key_len
    text = ""
    j=0
    if i != 0:
        for j in range(0,i):
            text += "0"
            j+=1
        bits_message = text+bits_message
    text = ""
    key_path = 0
    for el in bits_message:
        if key_path >= key_len: key_path=0
        text += logical_xor(el, key[key_path])
        key_path+=1
    return text
def decoding(bits_message:str, KEY):
    try:
        key = format(KEY, 'b')
        key_len = len(key)
        text = ""
        key_path = 0
        for el in bits_message:
            if key_path >= key_len: key_path = 0
            text += logical_xor(el, key[key_path])
            key_path += 1
        integer_value = int(text, 2)
        text = integer_value.to_bytes((integer_value.bit_length() + 7) // 8, 'big').decode()
        return text
    except TypeError or UnicodeDecodeError:
        return -1
def logical_xor(str1, str2):
    boolean = str1 != str2
    i = "0"
    if boolean == False: i = "0"
    else: i = "1"
    return i
def generate_partial_key1(my_public_key, private_key, public_key2):
    partial_key = my_public_key**private_key%public_key2
    return partial_key
def generate_partial_key2(my_public_key, private_key, public_key2):
    partial_key = public_key2**private_key%my_public_key
    return partial_key
def generate_full_key(key_private, key_public, partical_key2):
    full_key = partical_key2 ** key_private % key_public
    return full_key
def second_coding_step(message:str, KEY):
    key = format(KEY, 'b')
    key_len = len(key)
    text = ""
    for el in message:
        if el == "0": text +="1"
        elif el == "1": text +="0"
    text = ""
    key_path = 0
    for el in message:
        if key_path >= key_len: key_path=0
        text += logical_xor(el, key[key_path])
        key_path+=1
    return text
def second_decoder(smessage:str, KEY):
    key = format(KEY, 'b')
    key_len = len(key)
    message = ""
    key_path = 0
    for el in smessage:
        if key_path >= key_len: key_path=0
        message += logical_xor(el, key[key_path])
        key_path+=1
    text = ""
    return message
#message = "This is a very secret message!!!"
#s_public = 197
#s_private = 199
#m_public = 151
#m_private = 157
#partical_key_s = generate_partial_key1(s_public, s_private, m_public)
#partical_key_m = generate_partial_key2(m_public, m_private, s_public)
#full_key_s = generate_full_key(s_private, m_public, partical_key_m)
#full_key_m = generate_full_key(m_private, m_public, partical_key_s)
#my_message = coding(message, "KEY")
#my_message = second_coding_step(my_message, full_key_s)
#my_message2 = second_decoder(my_message, full_key_s)
#my_message = decoding(my_message2, "KEY")
#print(my_message)