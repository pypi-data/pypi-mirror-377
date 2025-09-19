def convert(n, base, dest):
    """
    Convert a number from one base to another.

    Args:
        n: Number to convert (string or integer)
        base: Original base (2-61)
        dest: Target base (2-61)

    Returns:
        str: Number representation in target base

    Raises:
        ValueError: If bases are invalid or number doesn't match original base
    """
    dict1 = {  #Character-to-value mapping for bases up to 62 (alphanumeric representation)
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "A": 10,
    "B": 11,
    "C": 12,
    "D": 13,
    "E": 14,
    "F": 15,
    "G": 16,
    "H": 17,
    "I": 18,
    "J": 19,
    "K": 20,
    "L": 21,
    "M": 22,
    "N": 23,
    "O": 24,
    "P": 25,
    "Q": 26,
    "R": 27,
    "S": 28,
    "T": 29,
    "U": 30,
    "V": 31,
    "W": 32,
    "X": 33,
    "Y": 34,
    "Z": 35,
    "a": 36,
    "b": 37,
    "c": 38,
    "d": 39,
    "e": 40,
    "f": 41,
    "g": 42,
    "h": 43,
    "i": 44,
    "j": 45,
    "k": 46,
    "l": 47,
    "m": 48,
    "n": 49,
    "o": 50,
    "p": 51,
    "q": 52,
    "r": 53,
    "s": 54,
    "t": 55,
    "u": 56,
    "v": 57,
    "w": 58,
    "x": 59,
    "y": 60,
    "z": 61,
    }
    dict2={0: "0", 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G', 17: 'H', 18: 'I', 19: 'J', 20: 'K', 21: 'L', 22: 'M', 23: 'N', 24: 'O', 25: 'P', 26: 'Q', 27: 'R', 28: 'S', 29: 'T', 30: 'U', 31: 'V', 32: 'W', 33: 'X', 34: 'Y', 35: 'Z', 36: 'a', 37: 'b', 38: 'c', 39: 'd', 40: 'e', 41: 'f', 42: 'g', 43: 'h', 44: 'i', 45: 'j', 46: 'k', 47: 'l', 48: 'm', 49: 'n', 50: 'o', 51: 'p', 52: 'q', 53: 'r', 54: 's', 55: 't', 56: 'u', 57: 'v', 58: 'w', 59: 'x', 60: 'y', 61: 'z'} #Value-to-character mapping for bases up to 61 (alphanumeric representation)
    if base>61 or base<2 or dest>61 or dest<2:
        raise ValueError("Unsupported base range. This module doesn't support base above 61 or below 2. Please change your conversion.")
    for i in str(n):
        if int(dict1[i])>=base:
            raise ValueError("The number that you are trying to convert is not in the inital base. Verify that the number matches the specified original base.")
            return ""
    #conversion in base 10
    a=0
    long=len(str(n))-1 #Number of digits minus one (position weight exponent) (ex: 1243=4)
    for i in str(n):    #for each number of number
        a+=dict1[str(i)]*base**long    #Add the number multiplied with the base raised to the power of its position.
        long-=1
    r=[]
    while a>0:
        r.append(dict2[a % dest]) #Add the remainder of the Euclidean division of the initial number by its destination base.
        a//=dest    #keep the quotient of the division.

    return ''.join(reversed(r)) #return the reversed numbers of numbers

class EquBase:
    """
    Number representation in multiple bases.

    Provides conversion methods to all supported bases (2-61).
    """
    dict1 = { #Character-to-value mapping for bases up to 62 (alphanumeric representation)
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "A": 10,
    "B": 11,
    "C": 12,
    "D": 13,
    "E": 14,
    "F": 15,
    "G": 16,
    "H": 17,
    "I": 18,
    "J": 19,
    "K": 20,
    "L": 21,
    "M": 22,
    "N": 23,
    "O": 24,
    "P": 25,
    "Q": 26,
    "R": 27,
    "S": 28,
    "T": 29,
    "U": 30,
    "V": 31,
    "W": 32,
    "X": 33,
    "Y": 34,
    "Z": 35,
    "a": 36,
    "b": 37,
    "c": 38,
    "d": 39,
    "e": 40,
    "f": 41,
    "g": 42,
    "h": 43,
    "i": 44,
    "j": 45,
    "k": 46,
    "l": 47,
    "m": 48,
    "n": 49,
    "o": 50,
    "p": 51,
    "q": 52,
    "r": 53,
    "s": 54,
    "t": 55,
    "u": 56,
    "v": 57,
    "w": 58,
    "x": 59,
    "y": 60,
    "z": 61,
    }
    #Value-to-character mapping for bases up to 62 (alphanumeric representation)
    dict2={0: "0", 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G', 17: 'H', 18: 'I', 19: 'J', 20: 'K', 21: 'L', 22: 'M', 23: 'N', 24: 'O', 25: 'P', 26: 'Q', 27: 'R', 28: 'S', 29: 'T', 30: 'U', 31: 'V', 32: 'W', 33: 'X', 34: 'Y', 35: 'Z', 36: 'a', 37: 'b', 38: 'c', 39: 'd', 40: 'e', 41: 'f', 42: 'g', 43: 'h', 44: 'i', 45: 'j', 46: 'k', 47: 'l', 48: 'm', 49: 'n', 50: 'o', 51: 'p', 52: 'q', 53: 'r', 54: 's', 55: 't', 56: 'u', 57: 'v', 58: 'w', 59: 'x', 60: 'y', 61: 'z'}
    def __init__(self, n, b=10):
        """
        Initialize with number and its base.

        Args:
            n: Number to convert
            b: Base of the number (default: 10)
        """
        self.n=n
        self.OGn=n #used to return the original value of n if it's changed (useful for the roman system just below)
        self.base=b
        self.OGbase=b

        #if the number given is in roman system (decimal)
        if self.base=="roman":
            values = {
                    'I': 1, 'V': 5, 'X': 10, 'L': 50,
                    'C': 100, 'D': 500, 'M': 1000
                }

            total = 0
            prev_value = 0
            for char in reversed(self.n):
                if char in values.keys():
                    char=char.upper()
                    current_value = values[char]

                    if current_value < prev_value:
                        total -= current_value
                    else:
                        total += current_value

                    prev_value = current_value

                    self.n=total
                    self.base=10
                else:
                    raise TypeError("The number is not in the roman system.")

    def __str__(self): #return parameters of the object
        if self.OGbase != "roman":
            return f"The number contained in the called object is {self.OGn} which is in base {self.OGbase}."
        else:
            return f"The number contained in the called object is {self.OGn} (stocked as {self.n} for calculations) which is in base {self.OGbase} (converted to base {self.base} for operations)."

    # The following bX() methods provide direct conversion to base X (2-61)
    # All use the same algorithm: convert to decimal first, then to target base. For more details on the calcul, please refers the the script of the function convert (line 1 to 84).
    def bn(self, dest):     # dest: target base chosen by the user
        """
        Convert to specified base.

        Args:
            dest: Target base (2-61)

        Returns:
            str: Number representation in target base
        """
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % dest])
            a//=dest

        return ''.join(reversed(r))


    def b2(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 2])
            a//=2

        return ''.join(reversed(r))

    def b3(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 3])
            a//=3

        return ''.join(reversed(r))

    def b4(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 4])
            a//=4

        return ''.join(reversed(r))

    def b5(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 5])
            a//=5

        return ''.join(reversed(r))

    def b6(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 6])
            a//=6

        return ''.join(reversed(r))

    def b7(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 7])
            a//=7

        return ''.join(reversed(r))

    def b8(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 8])
            a//=8

        return ''.join(reversed(r))

    def b9(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 9])
            a//=9

        return ''.join(reversed(r))

    def b10(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 10])
            a//=10

        return ''.join(reversed(r))

    def b11(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 11])
            a//=11

        return ''.join(reversed(r))

    def b12(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 12])
            a//=12

        return ''.join(reversed(r))

    def b13(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 13])
            a//=13

        return ''.join(reversed(r))

    def b14(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 14])
            a//=14

        return ''.join(reversed(r))

    def b15(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 15])
            a//=15

        return ''.join(reversed(r))

    def b16(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 16])
            a//=16

        return ''.join(reversed(r))

    def b17(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 17])
            a//=17

        return ''.join(reversed(r))

    def b18(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 18])
            a//=18

        return ''.join(reversed(r))

    def b19(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 19])
            a//=19

        return ''.join(reversed(r))

    def b20(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 20])
            a//=20

        return ''.join(reversed(r))

    def b21(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 21])
            a//=21

        return ''.join(reversed(r))

    def b22(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 22])
            a//=22

        return ''.join(reversed(r))

    def b23(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 23])
            a//=23

        return ''.join(reversed(r))

    def b24(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 24])
            a//=24

        return ''.join(reversed(r))

    def b25(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 25])
            a//=25

        return ''.join(reversed(r))

    def b26(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 26])
            a//=26

        return ''.join(reversed(r))

    def b27(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 27])
            a//=27

        return ''.join(reversed(r))

    def b28(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 28])
            a//=28

        return ''.join(reversed(r))

    def b29(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 29])
            a//=29

        return ''.join(reversed(r))

    def b30(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 30])
            a//=30

        return ''.join(reversed(r))

    def b31(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 31])
            a//=31

        return ''.join(reversed(r))

    def b32(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 32])
            a//=32

        return ''.join(reversed(r))

    def b33(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 33])
            a//=33

        return ''.join(reversed(r))

    def b34(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 34])
            a//=34

        return ''.join(reversed(r))

    def b35(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 35])
            a//=35

        return ''.join(reversed(r))

    def b36(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 36])
            a//=36

        return ''.join(reversed(r))

    def b37(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 37])
            a//=37

        return ''.join(reversed(r))

    def b38(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 38])
            a//=38

        return ''.join(reversed(r))

    def b39(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 39])
            a//=39

        return ''.join(reversed(r))

    def b40(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 40])
            a//=40

        return ''.join(reversed(r))

    def b41(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 41])
            a//=41

        return ''.join(reversed(r))

    def b42(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 42])
            a//=42

        return ''.join(reversed(r))

    def b43(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 43])
            a//=43

        return ''.join(reversed(r))

    def b44(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 44])
            a//=44

        return ''.join(reversed(r))

    def b45(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 45])
            a//=45

        return ''.join(reversed(r))

    def b46(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 46])
            a//=46

        return ''.join(reversed(r))

    def b47(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 47])
            a//=47

        return ''.join(reversed(r))

    def b48(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 48])
            a//=48

        return ''.join(reversed(r))

    def b49(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 49])
            a//=49

        return ''.join(reversed(r))

    def b50(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 50])
            a//=50

        return ''.join(reversed(r))

    def b51(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 51])
            a//=51

        return ''.join(reversed(r))

    def b52(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 52])
            a//=52

        return ''.join(reversed(r))

    def b53(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 53])
            a//=53

        return ''.join(reversed(r))

    def b54(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 54])
            a//=54

        return ''.join(reversed(r))

    def b55(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 55])
            a//=55

        return ''.join(reversed(r))

    def b56(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 56])
            a//=56

        return ''.join(reversed(r))

    def b57(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 57])
            a//=57

        return ''.join(reversed(r))

    def b58(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 58])
            a//=58

        return ''.join(reversed(r))

    def b59(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 59])
            a//=59

        return ''.join(reversed(r))

    def b60(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 60])
            a//=60

        return ''.join(reversed(r))

    def b61(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 61])
            a//=61

        return ''.join(reversed(r))

    def b62(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        r=[]
        while a>0:
            r.append(EquBase.dict2[a % 62])
            a//=62

        return ''.join(reversed(r))

    #a special function to transform the number into the roman system by converty in decimal first.
    def roman(self):
        a=0
        long=len(str(self.n))-1
        for i in str(self.n):
            a+=EquBase.dict1[str(i)]*self.base**long
            long-=1
        val = [
                1000, 900, 500, 400,
                100, 90, 50, 40,
                10, 9, 5, 4,
                1
            ]
        syms = [
                "M", "CM", "D", "CD",
                "C", "XC", "L", "XL",
                "X", "IX", "V", "IV",
                "I"
            ]

        roman_num = ""
        i = 0
        r=self.n    #using another variable to avoid to change the value of self.n

        while r > 0:
            count = r // val[i]
            for _ in range(count):
                roman_num += syms[i]
                r -= val[i]
            i += 1

        return roman_num