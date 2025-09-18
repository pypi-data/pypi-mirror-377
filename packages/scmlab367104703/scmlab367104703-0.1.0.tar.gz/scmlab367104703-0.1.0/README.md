# scmlab367104703

`scmlab367104703` This is a basic number theory module consisting of three functions `euclidean()`,`extended()`,`eratosthenes()`

---

## Features
- **Euclidean Algorithm**: Use `euclidean()` to find the greatest common divisor (gcd) of two integers
- **Extended Euclidean Algorithm**: Use `extended()` to find 
- The greatest common divisor (gcd) of two numbers `a` and `b`
- And two numbers `x` and `y` such that:

\[
a \times x + b \times y = \gcd(a, b)
\]
- **Sieve of Eratosthenes**:Use `eratosthenes(n)` to find all prime numbers up to a certain  `n`.
---

## Installation

You can install the package directly from PyPI:

```
pip install scmlab367104703

```
---
## Example1(Euclidean Algorithm)
```
#input
>>>import scmlab367104703 as scm
>>> scm.euclidean(807, 481)

#output
gcd(807, 481)
807 = 481 x 1 + 326
481 = 326 x 1 + 155
326 = 155 x 2 + 16
155 = 16 x 9 + 11
16 = 11 x 1 + 5
11 = 5 x 2 + 1
5 = 1 x 5 + 0
gcd is 1
```
## Example2(Extended Euclidean Algorithm)
```
#input
>>> import scmlab367104703 as scm
>>> scm.extended(120, 23)

#output
120*(-9) + 23*(47) = 1
x = -9, y = 47
```
## Example3(Sieve of Eratosthenes)
```
#input
>>> import scmlab367104703 as scm
>>> scm.eratosthenes(50)

#output
+------+-----+------+----+-----+----+------+----+------+----+
|  1   | *2* | *3*  | 4  | *5* | 6  | *7*  | 8  |  9   | 10 |
| *11* |  12 | *13* | 14 |  15 | 16 | *17* | 18 | *19* | 20 |
|  21  |  22 | *23* | 24 |  25 | 26 |  27  | 28 | *29* | 30 |
| *31* |  32 |  33  | 34 |  35 | 36 | *37* | 38 |  39  | 40 |
| *41* |  42 | *43* | 44 |  45 | 46 | *47* | 48 |  49  | 50 |
+------+-----+------+----+-----+----+------+----+------+----+
```