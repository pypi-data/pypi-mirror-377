# cbases

A powerful Python library for number base conversion (2-62) with Roman numeral support.

## Features

- Convert numbers between bases 2-62
- Support for Roman numerals (conversion to/from decimal)
- Easy-to-use API with both functional and OOP approaches
- Comprehensive error handling

## Installation

```bash
pip install cbases

##USAGE:
#Functional approach:

from cbases import convert

result = convert("FF", 16, 10)  # "255"
result = convert("255", 10, 2)  # "11111111"

#Object-oriented approach:

from cbases import EquBase

num = EquBase("FF", 16)
print(num.b10())  # "255"
print(num.b2())   # "11111111"
print(num.bn(11)) # "212"

    #Roman numerals
roman_num = EquBase("XIV", "roman")
print(roman_num.b10())  # "14"

num = EquBase("10", 10)
print(num.roman()) #"X"

#Str function:
num = EquBase("FF", 16)
print(num) #"The number contained in the called object is FF which is in base 16."

roman_num = EquBase("X", "roman")
print(roman_num) #"The number contained in the called object is X (stocked as 10 for calculations) which is in base roman (converted to base 10 for operations)."
