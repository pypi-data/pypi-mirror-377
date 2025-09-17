import re

# 1. Roman digits convert to words.
def roman2digit(s):
    roman = {'I':1, 'V':5, 'X':10, 'L':50, 'C':100, 'D':500, 'M':1000, 'IV':4, 'IX':9, 'XL':40, 'XC':90, 'CD':400, 'CM':900}
    i = 0
    num = 0
    while i < len(s):
        if i+1<len(s) and s[i:i+2] in roman:
            num+=roman[s[i:i+2]]
            i+=2
        else:
            num+=roman[s[i]]
            i+=1
    return num

def replace_roman(match):
    matched = match.group(2)
    # IIV is not roman digit. It means "Ichki ishlar vazirligi"
    if matched == 'IIV':
        return match.group(1)+'iiv'+match.group(3)
    number = roman2digit(matched)
    word = num2word(number)
    if word[-1] == 'i' or word[-1] == 'a':
        word += 'nchi'
    else:
        word += 'inchi'
    return match.group(1)+word+match.group(3)


# 2. Numbers to words
def three_digit(a):
    yuz = a // 100
    on = a // 10 % 10
    bir = a % 10
    word = ''
    # yuzlar xonasi

    if yuz == 1:
        word +="bir"
    elif yuz == 2:
        word += "ikki"
    elif yuz == 3:
        word += "uch"
    elif yuz == 4:
        word += "toʻrt"
    elif yuz == 5:
        word += "besh"
    elif yuz == 6:
        word += "olti"
    elif yuz == 7:
        word += "yetti"
    elif yuz == 8:
        word += "sakkiz"
    elif yuz == 9:
        word += "toʻqqiz"
    if yuz != 0:
        word += " yuz"

    # o'nlar xonasi

    if on == 1:
        word += " oʻn"
    elif on == 2:
        word += " yigirma"
    elif on == 3:
        word += " oʻttiz"
    elif on == 4:
        word += " qirq"
    elif on == 5:
        word += " ellik"
    elif on == 6:
        word += " oltmish"
    elif on == 7:
        word += " yetmish"
    elif on == 8:
        word += " sakson"
    elif on == 9:
        word += " toʻqson"

    # birlar xonasi

    if bir == 1:
        word +=" bir"
    elif bir == 2:
        word += " ikki"
    elif bir == 3:
        word += " uch"
    elif bir == 4:
        word += " toʻrt"
    elif bir == 5:
        word += " besh"
    elif bir == 6:
        word += " olti"
    elif bir == 7:
        word += " yetti"
    elif bir == 8:
        word += " sakkiz"
    elif bir == 9:
        word += " toʻqqiz"
    
    return word

def num2word(n):
    if n == 0:
        return 'nol'
    names = ["", "ming", "million", "milliard", "trillion", "kvadrillion", "kvintillion", "sekstillion", "septillion", "oktalon", "nonalon", "dekalon", "endekalon", "dodekalon"]
    digit = 0
    word = ''
    d = n
    while d > 0:
        d //= 10
        digit += 1

    if digit % 3 == 0:
        x = 0
    else:
        x = 1
    while n > 0:
        if x:
            k = n // 10 ** (digit - digit % 3)
            n %= 10 ** (digit - digit % 3)
        else:
            k = n // 10 ** (digit-3)
            n %= 10 ** (digit-3)
        word += three_digit(k)+' '
        if x:
            word += names[digit//3]+' '
        else:
            word += names[digit//3-1]+' '
        if x:
            digit -= digit % 3
            x = 0
        else:
            digit -= 3

    return word.strip()

def float_num2word(n):
    n = re.sub(r"[,]", r"\.", n)
    tens = [' oʻndan ', 'yuzdan ', 'mingdan ', ' oʻn mingdan ', ' yuz mingdan ', ' milliondan ']
    whole = n.split('.')[0]
    frac = n.split('.')[1]
    if frac == '0':
        return num2word(int(whole))
    return num2word(int(whole)) + ' butun' + tens[len(frac) - 1]+num2word(int(frac))
