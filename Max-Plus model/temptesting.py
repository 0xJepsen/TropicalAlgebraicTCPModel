from MatrixMath import Matrix

A = Matrix(dims=(2,2), fill=0.0)
M = Matrix(dims=(2,1), fill=0.0)

print(M.rows)

def mergeMatrix(A, B):
    dimA = (A.rows, A.cols)
    dimB = (B.rows, B.cols)
    C = Matrix(dims=(A.rows+B.rows, A.cols+ B.cols), fill=0)
    for i in range(A.rows):
        for j in range(A.cols):
            C[i,j] = A[i,j]
    return C

C = mergeMatrix(A,M)
print(C)


