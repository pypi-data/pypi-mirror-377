# Number to words
This project is to convert numbers to words in Uzbek language.
## Usage
1. Integer numbers
```code
from num2word_uz import num2word
number = int(input("Sonni kiriting:")) # 15
num2word(number) # o'n besh
```
2. Float point numbers
```code
from num2word_uz import float_num2word
number = float(input("Sonni kiriting:")) # 2.3
float_num2word(number) # ikki butun o'ndan uch
```
3. Roman numbers to numbers
```code
from num2word_uz import roman2digit
number = input("Rim raqamini kiriting:") # VI
roman2digit(number) # olti
```
#### Requirements
- Python >= 3.8
