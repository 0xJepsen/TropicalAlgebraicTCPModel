
from MatrixMath import Matrix

A = Matrix(dims=(1,3), fill=1.0)
B = Matrix(dims=(3,3), fill=2.0)


# Test 01
C = A + B
print('Max-plus addition (Max) (Matrix-Matrix):')
print(C)


# Test 02
C = A + 10.0
print('Max-plus addition (Max) (Matrix-Scalar):')
print(C)

# Test 03
C = 20.0 + A
print('Max-plus addition (Max) (Matrix-Scalar):')
print(C)


# Test 04
C = A @ B
print('Max-plus multiplication (Matrix-Matrix):')
print(C)

# Test 05
C = A * B
# print('point-wise multiplication (Matrix-Matrix):')
# print(C)

# Test 06
# C =  A * 0.5
# print('Left point-wise multiplication (Matrix-scalar):')
# print(C)

# Test 07
# C =   0.5 * A
# print('Right point-wise multiplication (Matrix-scalar):')
# print(C)

# Test 08
print('Element access (Matrix-scalar):')
print(A[0,0])


# Test 09
# print('Element update (Matrix-scalar):')
# print(A)
# A[0,0] = -10.0
# print(A)

# Test 10
# print("Horizontal concatenation")
# print("A: \n", A)
# print("B: \n", B)
#
# C = A.concatenate_h(B)
# print("A|B: \n", C)
# print("C[0,0] \n", C[0,0])
A = Matrix(dims=(1,3), fill=1.0)

print("A before \n", A)
C = A.square_epsilon()
print("A.square_epsilon: \n", C)