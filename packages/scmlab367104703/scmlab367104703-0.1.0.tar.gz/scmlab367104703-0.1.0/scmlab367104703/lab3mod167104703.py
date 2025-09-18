"""
Basic Number Theory Module

Functions:
- euclidean(a, b): Prints the steps of the Euclidean algorithm to find gcd(a, b).
- extended(a, b): Uses Extended Euclidean Algorithm to print integers x, y satisfying a*x + b*y = gcd(a, b).
- eratosthenes(N): Prints a table of numbers from 1 to N with prime numbers highlighted by *p*.
"""
def euclidean(a, b):
    """
    Compute and print the steps of the Euclidean algorithm to find the greatest common divisor (GCD) of two integers.

    Parameters:
    a (int): The first integer.
    b (int): The second integer.

    Prints the division steps in the form:
        a = b * quotient + remainder
    until the remainder is zero, then prints the GCD.
    """
    print(f"gcd({a}, {b})")
    while b != 0:
        q = a // b
        r = a % b
        print(f"{a} = {b} x {q} + {r}")
        a, b = b, r
    print(f"gcd is {a}")

####################
def extended(a, b):
    """
    Compute and print integers x and y such that:
        a*x + b*y = gcd(a, b)
    
    Uses the Extended Euclidean Algorithm to find:
    - gcd: greatest common divisor of a and b
    - x, y: coefficients satisfying the linear combination

    Parameters:
    a (int): The first integer
    b (int): The second integer

    Prints the equation and the values of x and y.
    """

    def helper(a, b):
        if b == 0:
            return a, 1, 0
        gcd, x1, y1 = helper(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return gcd, x, y

    gcd, x, y = helper(a, b)
    print(f"{a}*({x}) + {b}*({y}) = {gcd}")
    print(f"x = {x}, y = {y}")



####################

from prettytable import PrettyTable

def eratosthenes(N):
    """
    Display a table of numbers from 1 to `limit` arranged in 10 columns,
    with prime numbers highlighted by surrounding them with asterisks (*...*).

    Parameters:
    limit (int): The maximum number to display in the table.

    """
    def find_primes(n):
        sieve = [True] * (n + 1)
        sieve[0:2] = [False, False]
        for i in range(2, int(n**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, n+1, i):
                    sieve[j] = False
        return {i for i, is_prime in enumerate(sieve) if is_prime}

    primes = find_primes(N)
    columns = 10

    table = PrettyTable()
    table.header = False
    table.border = True

    for i in range(1, N + 1, columns):
        row = []
        for num in range(i, min(i+columns, N+1)):
            if num in primes:
                row.append(f"*{num}*")  # ใส่ * รอบเลขเฉพาะ
            else:
                row.append(str(num))
        # เติมช่องว่างแถวสุดท้ายถ้ายังไม่ครบ
        if len(row) < columns:
            row.extend([''] * (columns - len(row)))
        table.add_row(row)

    print(table)

if __name__ == '__main__':
    # Test the euclidean function
    euclidean(120, 23)
    print("_________________________")
    # Test the Extended Euclidean Algorithm
    extended(120, 23)
    print("_________________________")
    # Test the eratosthenes function
    eratosthenes(50)