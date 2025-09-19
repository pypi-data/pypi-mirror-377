from collections.abc import Iterator, Iterable
from typing import Union
import random

class mat:
    def __init__(self, data:list[list[int|float]]):
        """Initialize a matrix from a list of lists."""
        if any(len(row)!=len(data[0]) for row in data):
            raise ValueError('All rows must have the same number of columns')
        self.data=[row[:] for row in data]
        self.n=len(data)
        self.p=len(data[0])
    def __getitem__(self, idx:Union[int, tuple[int,int]])->Union[list[int|float], int|float]:
        """Return the row at index `idx`."""
        if isinstance(idx, int):
            return self.data[idx]
        elif isinstance(idx, tuple) and len(idx)==2:
            i,j=idx
            return self.data[i][j]
        else:
            raise TypeError('Index must be int or tuple (i,j)')
    def __setitem__(self, idx:Union[int, tuple[int,int]], value:int|float|list[int|float])->None:
        """Set the row at index `idx`."""
        if isinstance(idx,int):
            if len(value)!=self.p: raise ValueError('Row length must match number of columns')
            self.data[idx]=value
        elif isinstance(idx,tuple):
            i,j=idx
            self.data[i][j]=value
    def __len__(self)->int:
        """Return the number of rows in the matrix."""
        return self.n
    @property
    def size(self)->tuple[int, int]:
        """Return the size of the matrix as (rows, columns)."""
        return self.n, self.p
    @staticmethod
    def zero(n:int, p:int)->'mat':
        """Return a zero matrix of size n x p."""
        if not isinstance(n, int) or not isinstance(p, int): 
            raise TypeError('n and p must be positive integers')
        return mat([[0 for _ in range(p)] for __ in range(n)])
    @staticmethod
    def I(n:int)->'mat':
        """Return an identity matrix of size n x n."""
        if not isinstance(n, int):
            raise TypeError('n must be an positive integer')
        return mat([[1 if i==j else 0 for j in range(n)] for i in range(n)])
    @staticmethod
    def diagonal(values:Iterable[int|float])->'mat':
        """Return a diagonal matrix built from a sequence of values."""
        values=list(values)
        if not values:
            raise ValueError('values cannot be empty')
        if not all(isinstance(v, (int, float)) for v in values):
            raise TypeError('All elements of values must be int or float')
        return mat([[values[i] if i==j else 0 for j in range(len(values))] for i in range(len(values))])
    @staticmethod
    def full(n:int, p:int=0, value:int|float=1)->'mat':
        """Return a matrix of shape n x p filled with a constant value."""
        if not isinstance(n, int) or n<=0:
            raise TypeError('n must be a positive integer')
        if p==0:
            p=n
        if not isinstance(p, int) or p<=0:
            raise TypeError('p must be a positive integer')
        if not isinstance(value, (int, float)):
            raise TypeError('value must be an integer or a float')
        return mat([[value for _ in range(p)] for _ in range(n)])
    @staticmethod
    def random(n:int, p:int=0, low:int=-10, high:int=10)->'mat':
        """Return a random matrix with integer entries."""
        if not isinstance(n, int) or not isinstance(p, int):
            raise TypeError('n and p must be positive integers')
        if p==0:
            p=n
        return mat([[random.randint(low, high) for _ in range(p)] for _ in range(n)])
    def __add__(self, other:'mat')->'mat':
        """Add two matrices element-wise."""
        if not isinstance(other, mat):
            raise TypeError('Matrix can only be added to another matrix')
        if self.size!=other.size:
            raise ValueError('Both matrices must have the same size')
        S=mat.zero(self.n, self.p)
        for i in range(self.n):
            for j in range(self.p):
                S.data[i][j]=self.data[i][j]+other.data[i][j]
        return S
    def __radd__(self, other:'mat')->'mat':
        """Right-side addition."""
        if other==0:
            return self.copy()
        return self+other
    def __sub__(self, other:'mat')->'mat':
        """Subtract two matrices element-wise."""
        if not isinstance(other, mat):
            raise TypeError('Matrix can only be subtracted by another matrix')
        if self.size!=other.size:
            raise ValueError('Both matrices must have the same size')
        S=mat.zero(self.n, self.p)
        for i in range(self.n):
            for j in range(self.p):
                S.data[i][j]=self.data[i][j]-other.data[i][j]
        return S
    def __mul__(self, other:Union[int, float, 'mat'])->'mat':
        """Multiply a matrix by a scalar or another matrix."""
        if isinstance(other, (int, float)):
            return mat([[other*self.data[i][j] for j in range(self.p)] for i in range(self.n)])
        if isinstance(other, mat):
            if self.p!=other.n:
                raise ValueError('The first matrix must have the same number of columns as the number of rows of the second')
            P=mat.zero(self.n, other.p)
            for i in range(self.n):
                for j in range(other.p):
                    for k in range(self.p):
                        P.data[i][j]+=self.data[i][k]*other.data[k][j]
            return P
        raise TypeError('Matrix can only be multiplied by int, float, or another matrix')
    def __rmul__(self, other:Union[int, float, 'mat'])->'mat':
        """Right-side multiplication."""
        return self*other
    def __truediv__(self, scalar:int|float)->'mat':
        """Divide a matrix by a scalar."""
        if not isinstance(scalar, (int, float)):
            raise TypeError('Matrix can only be divided by int or float')
        if scalar==0:
            raise ZeroDivisionError('Division of a matrix by zero is not defined')
        return (1/scalar)*self
    def __pow__(self, n:int)->'mat':
        """Raise a square matrix to a non-negative integer power."""
        if not isinstance(n, int) or n<0:
            raise TypeError('n must be a non-negative integer')
        if self.n!=self.p:
            raise ValueError('The matrix must be square')
        result=mat.I(self.n)
        base=self.copy()
        while n>0:
            if n%2==1:
                result=result*base
            base=base*base
            n//=2
        return result
    def __neg__(self)->'mat':
        """Negate the matrix."""
        return mat([[-x for x in row] for row in self.data])
    def __eq__(self, other:'mat')->bool:
        """Check if two matrices are equal."""
        if not isinstance(other, mat):
            return False
        if self.size!=other.size:
            return False
        return self.data==other.data
    def __ne__(self, other:'mat')->bool:
        """Check if two matrices are not equal."""
        return not self==other
    @property
    def T(self)->'mat':
        """Return the transpose of the matrix."""
        return mat([[self.data[j][i] for j in range(self.n)] for i in range(self.p)])
    def copy(self)->'mat':
        """Return a copy of the matrix."""
        return mat([row[:] for row in self.data])
    @property
    def trace(self)->int|float:
        """Return the trace of a square matrix."""
        if self.n!=self.p:
            raise ValueError('Trace is only defined for square matrices')
        return sum(self.data[i][i] for i in range(self.n))
    def tolist(self)->list[list[int|float]]:
        """Return the matrix as a list of lists."""
        return [row[:] for row in self.data]
    def __iter__(self)->Iterator[list[int|float]]:
        """Return an iterator over the rows of the matrix."""
        return iter(self.data)
    def flatten(self, as_tuple:bool=False)->Union[Iterator[int|float], tuple[int|float]]:
        """Return all elements of the matrix in row-major order as a flat generator or tuple."""
        flat_gen=(x for row in self.data for x in row)
        if as_tuple:
            return tuple(flat_gen)
        return flat_gen
    def diag_mat(self)->'mat':
        """Return a diagonal matrix with the same diagonal elements as the current matrix."""
        if self.n != self.p:
            raise ValueError('Matrix must be square')
        return mat([[self.data[i][j] if i==j else 0 for j in range(self.n)] for i in range(self.n)])
    def diag_vec(self, column:bool=True)->'mat':
        """Return the diagonal elements as a column or row vector (column by default, row if column=False)."""
        if self.n!=self.p:
            raise ValueError('Matrix must be square')
        if column:
            return mat([[self.data[i][i]] for i in range(self.n)])
        else:
            return mat([[self.data[i][i] for i in range(self.n)]])
    def replace(self, old_value:int|float, new_value:int|float)->None:
        """Replace all occurrences of old_value with new_value in the matrix (in place)."""
        for i in range(self.n):
            for j in range(self.p):
                if self.data[i][j]==old_value:
                    self.data[i][j]=new_value
    def replaced(self, old_value:int|float, new_value:int|float)->'mat':
        """Return a new matrix with old_value replaced by new_value."""
        return mat([[new_value if self.data[i][j]==old_value else self.data[i][j] for j in range(self.p)] for i in range(self.n)])
    def map(self, f:callable)->'mat':
        """Apply a function to each element of the matrix and return a new matrix."""
        if not callable(f):
            raise TypeError('f must be a callable function')
        return mat([[f(self[i][j]) for j in range(self.p)] for i in range(self.n)])
    def det(self)->int|float:
        """Compute the determinant of a square matrix using Gaussian elimination."""
        if self.n!=self.p:
            raise ValueError('Determinant is only defined for square matrices')
        mat_copy=self.copy().data
        n=self.n
        det=1
        for i in range(n):
            if mat_copy[i][i]==0:
                for j in range(i+1, n):
                    if mat_copy[j][i]!=0:
                        mat_copy[i], mat_copy[j]=mat_copy[j], mat_copy[i]
                        det*=-1
                        break
                else:
                    return 0
            for j in range(i+1, n):
                factor=mat_copy[j][i]/mat_copy[i][i]
                for k in range(i, n):
                    mat_copy[j][k]-=factor*mat_copy[i][k]
        for i in range(n):
            det*=mat_copy[i][i]
        return det
    def rank(self)->int:
        """Return the rank of the matrix using Gaussian elimination."""
        mat_copy=self.copy().data
        n,p=self.size
        rank=0
        for col in range(p):
            pivot=None
            for row in range(rank,n):
                if mat_copy[row][col]!=0:
                    pivot=row
                    break
            if pivot is None:
                continue
            mat_copy[rank],mat_copy[pivot]=mat_copy[pivot],mat_copy[rank]
            pivot_val=mat_copy[rank][col]
            mat_copy[rank]=[x/pivot_val for x in mat_copy[rank]]
            for row in range(rank+1,n):
                factor=mat_copy[row][col]
                mat_copy[row]=[x-factor*y for x,y in zip(mat_copy[row],mat_copy[rank])]
            rank+=1
        return rank
    def __repr__(self)->str:
        """Return the official string representation of the matrix."""
        return f'mat({self.data})'
    def __str__(self)->str:
        """Return a readable string representation of the matrix."""
        return '\n'.join('[' + ' '.join(str(x) for x in row) + ']' for row in self.data)