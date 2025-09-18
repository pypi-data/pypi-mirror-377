def gcd(a,b):
    """This function returns the greatest common divisor of a and b using the Euclidean algorithm.

    Args:
        a (integer): The first integer
        b (integer): The second integer

    Returns:
        integer: The greatest common divisor of a and b
    """
    a, b = abs(a), abs(b)
    if a > b and b != 0:
        while a%b != 0:
            a = (a//b)*b + a%b
            print(f"{a} = {a//b}*{b} + {a%b}") 
            a, b = b, a%b
        print(f"{a} = {a//b}*{b}")
        return b
    elif a <= b and a != 0:
        while b%a != 0:
            b = (b//a)*a + b%a
            print(f"{b} = {b//a}*{a} + {b%a}")
            a, b = b, a%b
        print(f"{b} = {b//a}*{a}")
        return a
    elif a == 0 or b == 0:
        return a+b

def extended_gcd(a,b):
    """This function returns the coefficients x and y such that ax + by = gcd(a, b).

    Args:
        a (integer): The first integer
        b (integer): The second integer

    Returns:
        tuple: x, y are the coefficients satisfying ax + by = gcd(a, b)
    """
    if a == 0:
        return b,0,1
    elif b == 0:
        return a,1, 0
    else:
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        print(f"{gcd} = {a}*{x} + {b}*{y}")
        return gcd,x,y

if __name__ == "__main__":
    a = 234
    b = 42
    d=gcd(a,b)
    print(f"The gcd of 234 and 42 is {d}")
    c = 7920
    d = 4536
    print(extended_gcd(c,d))