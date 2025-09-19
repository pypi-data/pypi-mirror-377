# Rathureqpy - A Python Utility Library

Rathureqpy is a Python library that provides a set of useful functions for a variety of tasks including list manipulation, mathematical operations, logical operations, statistical measures, and more.

## Installation

You can install Rathureqpy by running:

``bash
pip install rathureqpy
``

## Features

### List Operations

- **zero(number)**: Returns a list of zeros with the specified length.

- **prod(L, a)**: Returns a new list with each element of `L` multiplied by `a`.

- **addl(*args)**: Adds corresponding elements from multiple lists of equal length.

- **linespace(start, end, step)**: Generates a list of evenly spaced values between `start` and `end` with a given `step`.

- **array(start, end, n)**: Generates an array of `n` evenly spaced values between `start` and `end`.

- **uni(*lists)**: Flattens multiple lists into a single list.

- **uniwd(*lists)**: Flattens multiple lists into a single list and removes duplicates.

- **inter(*lists)**: Returns the intersection of multiple lists.

- **uniq(L)**: Returns a list with unique elements from `L`.

- **moy(L)**: Returns the mean of a list `L`.

- **sum_int(start, end)**: Returns the sum of integers between `start` and `end`.

- **randl(min, max, n)**: Generates a list of `n` random integers between `min` and `max`.

- **shuffle_list(L)**: Returns a shuffled version of `L`.

- **filtrer(L, condition)**: Filters `L` based on a condition.

- **chunk(L, n)**: Splits `L` into chunks of size `n`.

- **partition(L, condition)**: Partitions `L` into two lists based on a condition.


### Logical Operations

- **binr(n)**: Converts an integer `n` to its binary representation as a string.

- **change_base(value, inp_base, out_base)**: Converts `value` from `inp_base` to `out_base`.

- **divisor_list(n)**: Returns a list of divisors of `n`.

- **dicho(start, end, f, eps)**: Performs binary search to find the root of the function `f` in the interval `[start, end]` with an error tolerance `eps`.

- **size(point_A, point_B)**: Calculates the distance between two points `A` and `B` in a 2D space.

### Constants

- **pi**: Returns the constant `\u03C0`.

- **e**: Returns the constant `e`.

- **tau**: Returns the constant `\u03C4` (2\u03C0).

### Mathematical Operations

- **abs(x)**: Returns the absolute value of `x`.

- **cos(x)**: Returns the cosine of `x`.

- **sin(x)**: Returns the sine of `x`.

- **log(x, base=e())**: Returns the logarithm of `x` to the specified `base`.

- **exp(x)**: Returns the exponential of `x`.

- **sqrt(x)**: Returns the square root of `x`.

- **facto(n)**: Returns the factorial of `n`.

- **floor(x)**: Returns the largest integer less than or equal to `x`.

- **ceil(x)**: Returns the smallest integer greater than or equal to `x`.

- **rint(x)**: Returns the integer closest to `x` (rounding halfway cases away from zero).

- **gcd(a, b)**: Returns the greatest common divisor of `a` and `b`.

- **lcm(a, b)**: Returns the least common multiple of `a` and `b`.

- **is_prime(n)**: Checks if `n` is a prime number.

- **integ(f, a, b, N)** : Calculates the integral of `f` from `a` to `b` using the trapezoidal rule, with a sign adjustment if `a > b`

### Statistical Measures

- **variance(L)**: Returns the variance of the list `L`.

- **ecart_type(L)**: Returns the standard deviation of the list `L`.

- **mediane(L)**: Returns the median of the list `L`.

- **decomp(n)**: Returns the prime factorization of `n` as a list of tuples.

- **list_prime(n)**: Returns a list of all prime numbers up to `n`.

- **pascal_row(n)**: Returns the `n`-th row of Pascal's Triangle.


### Matrix

- **mat(data)**: Creates a matrix from a list of lists `data`. All rows must have the same length.

    - **__getitem__(idx)**: Returns a row if `idx` is an integer, or a single element if `idx` is a tuple `(i,j)`.

    - **__setitem__(idx, value)**: Sets a row if `idx` is an integer, or a single element if `idx` is a tuple `(i,j)`.

    - **__len__()**: Returns the number of rows of the matrix.

    - **size**: Returns a tuple `(rows, columns)` representing the matrix size.

    - **__add__(other)**: Element-wise addition of two matrices of the same size.

    - **__radd__(other)**: Right-side addition (supports `sum()`).

    - **__sub__(other)**: Element-wise subtraction of two matrices of the same size.

    - **__mul__(other)**: Multiplies the matrix by a scalar or another matrix (matrix multiplication).

    - **__rmul__(other)**: Right-side multiplication.

    - **__truediv__(scalar)**: Divides the matrix by a scalar.

    - **__pow__(n)**: Raises a square matrix to a non-negative integer power.

    - **__neg__()**: Returns the negation of the matrix.

    - **__eq__(other)**: Returns True if two matrices are equal.

    - **__ne__(other)**: Returns True if two matrices are not equal.

    - **T**: Returns the transpose of the matrix.

    - **copy()**: Returns a copy of the matrix.

    - **trace**: Returns the trace of a square matrix.

    - **tolist()**: Returns the matrix as a list of lists.

    - **__iter__()**: Returns an iterator over the rows of the matrix.

    - **flatten(as_tuple=False)**: Returns all elements as a flat generator, or as a tuple if `as_tuple=True`.

    - **diag_mat()**: Returns a diagonal matrix with the same diagonal elements as the current square matrix.

    - **diag_vec(column=True)**: Returns the diagonal elements as a column vector (default) or row vector if `column=False`.

    - **replace(old_value, new_value)**: Replaces all occurrences of `old_value` with `new_value` in-place.

    - **replaced(old_value, new_value)**: Returns a new matrix with `old_value` replaced by `new_value`.

    - **map(f)**: Applies a function `f` to each element of the matrix and returns a new matrix.

    - **det()**: Returns the determinant of a square matrix.

    - **rank()**: Returns the rank of the matrix using Gaussian elimination.

    - **__repr__()**: Returns the official string representation of the matrix.

    - **__str__()**: Returns a readable string representation of the matrix.

- **zero(n, p)**: Returns a zero matrix of size `n x p`.

- **I(n)**: Returns an identity matrix of size `n x n`.

- **diagonal(values)**: Returns a diagonal matrix with the given sequence of `values`.

- **full(n, p=0, value=1)**: Returns a matrix of size `n x p` filled with `value`. If `p` is 0, creates a square matrix `n x n`.

- **random(n, p=0, low=-10, high=10)**: Returns a random integer matrix of size `n x p` (square if `p=0`) with entries in `[low, high]`.


### Mathematical Language LaTeX-like

- **lat(expr)**: Converts a simple LaTeX-like string `expr` into Unicode math characters. Supports: exponents (`^`), indices (`_`), square roots (`sqrt(...)`), sums (`sum{...}^...`), products (`prod{...}^...`), integrals (`int`), and fractions (`frac{...}{...}`).

- **symbol(sym)**: Returns the Unicode math symbol corresponding to the LaTeX command `sym`. If the command is unknown, returns `[unknown: sym]`.

- **dot(text)**: Returns the input string `text` with a dot placed above each character.

- **vec(text)**: Returns the input string `text` with a bar placed above each character.

- **greek(expr)**: Converts the Greek letter name `expr` into its corresponding Unicode symbol. Returns an empty string if the name is not recognized.

- **italic(text)**: Converts the input string `text` to italic Unicode mathematical characters. Only English letters (a-z, A-Z) are transformed.

- **bold(text)**: Converts the input string `text` to bold Unicode mathematical characters. Only English letters (a-z, A-Z) are transformed.

- **mathbb(text)**: Converts the input string `text` to double-struck (blackboard bold) Unicode characters. Only English letters (a-z, A-Z) are transformed.

- **cursive(text)**: Converts the input string `text` to cursive (script) Unicode characters. Only English letters (a-z, A-Z) are transformed.


## Contribute and Bugs

If you encounter any bugs or would like to contribute to the project, feel free to open an issue or submit a pull request. Contributions are always welcome!

**email** : arthur.quersin@gmail.com

Made by Arthur Quersin
