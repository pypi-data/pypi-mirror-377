import re

def three_digit(a):
    if len(a) < 3:
        a = '0'*(3-len(a))+a
    yuz, on, bir = a
    word = ''

    birlik = {
        '0': "",
        '1': "bir",
        '2': "ikki",
        '3': "uch",
        '4': "to'rt",
        '5': "besh",
        '6': "olti",
        '7': "yetti",
        '8': "sakkiz",
        '9': "to'qqiz"
    }
    onlik = {
        '0': "",
        '1': " o'n",
        '2': " yigirma",
        '3': " o'ttiz",
        '4': " qirq",
        '5': " ellik",
        '6': " oltmish",
        '7': " yetmish",
        '8': " sakson",
        '9': " to'qson"
    }
    yuzlik = {
        '0': "",
        '1': "bir yuz",
        '2': "ikki yuz",
        '3': "uch yuz",
        '4': "to'rt yuz",
        '5': "besh yuz",
        '6': "olti yuz",
        '7': "yetti yuz",
        '8': "sakkiz yuz",
        '9': "to'qqiz yuz"
    }
    # yuzlar xonasi
    word += yuzlik[yuz]
    # o'nlar xonasi
    word += onlik[on]
    # birlar xonasi
    word = word+' '+birlik[bir]
    
    return word

def num2word(n):
    # main function which convert number to word
    # if length of the number greater 15, the function return word of each digit in the number
    # 10 - o'n, 3412355 - uch million to'rt yuz o'n ikki ming uch yuz ellik besh
    # 12345678910111213 - bir ikki uch (...) bir ikki bir uch
    if "." in n: n = n[:n.find(".")]
    if "," in n: n = n[:n.find(",")]
    # clear zeros that do not affect the value
    if n.count("0") != len(n):
        n = n.lstrip("0")
    if len(n) <= 15:
        if int(n) == 0:
            return 'nol'
        names = ["", "ming", "million", "milliard", "trillion", "kvadrillion", "kvintillion", "sekstillion", "septillion", "oktalon", "nonalon", "dekalon", "endekalon", "dodekalon"]
        word = ''
        index = 0
        while len(n) > 3:
            triple = n[len(n)-3:]
            if int(triple) != 0:
                word = three_digit(triple)+' '+names[index]+' '+word
            n = n[:len(n)-3]
            index += 1
        else:
            if int(n) != 0:
                word = three_digit(n)+' '+names[index]+' '+word
        return re.sub(r" +", " ", word).strip()
    elif len(n) == 16:
        return ' '.join(re.sub(r"(0*)(\d+)", zeros, n[i:i+2]) for i in range(0, 16, 2))
    else:
        birlik = {
            '0': "nol",
            '1': "bir",
            '2': "ikki",
            '3': "uch",
            '4': "to'rt",
            '5': "besh",
            '6': "olti",
            '7': "yetti",
            '8': "sakkiz",
            '9': "to'qqiz"
        }
        return ' '.join(birlik[digit] for digit in n)

def float_num2word(n):
    # clear zeros that do not affect the value
    # 35,33400 -> 35,334
    n = n.rstrip("0")
    # float number to words:
    # 1,3 - bir butun o'ndan uch, 15.12 - o'n besh butun yuzdan o'n ikki
    tens = ["o'ndan ", "yuzdan ", "mingdan ", "o'n mingdan ", "yuz mingdan ", "milliondan "]
    if n[-1] in '.,':
        whole, frac = n[:-1], '0'
    elif '.' not in n and ',' not in n:
        whole, frac = n, '0'
    else:
        whole, frac = re.findall(r'\d+', n)
    frac = re.sub(r"(0)(0+$)", r"\1", frac)
    if frac == '0':
        return num2word(whole)
    if len(frac) > len(tens):
        return num2word(whole)+' butun '+' '.join([num2word(num) for num in frac])
    return num2word(whole) + ' butun ' + tens[len(frac)-1] + num2word(frac)

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
