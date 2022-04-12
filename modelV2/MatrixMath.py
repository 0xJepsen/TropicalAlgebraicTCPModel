class Matrix:
    def __init__(self, dims, fill):

        self.rows = dims[0]
        self.cols = dims[1]

        self.A = [[fill] * self.cols for i in range(self.rows)]

    def __str__(self):
        m = len(self.A)  # Get the first dimension
        mtxStr = ""

        mtxStr += "------------- output -------------\n"

        for i in range(m):
            mtxStr += (
                "|" + ", ".join(map(lambda x: "{0:8.3f}".format(x), self.A[i])) + "| \n"
            )

        mtxStr += "----------------------------------"

        return mtxStr

    def __add__(self, other):

        # Create a new matrix
        C = Matrix(dims=(self.rows, self.cols), fill=0)

        # Check if the other object is of type Matrix
        if isinstance(other, Matrix):
            # Add the corresponding element of 1 matrices to another
            for i in range(self.rows):
                for j in range(self.cols):
                    C.A[i][j] = max(self.A[i][j], other.A[i][j])  # changed for max plus

        # If the other object is a scaler
        elif isinstance(other, (int, float)):
            # Add that constant to every element of A
            for i in range(self.rows):
                for j in range(self.cols):
                    C.A[i][j] = max(self.A[i][j], other)

        return C

    # Right addition can be done by calling left addition
    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):  # pointwise multiplication

        C = Matrix(dims=(self.rows, self.cols), fill=0)
        if isinstance(other, Matrix):

            for i in range(self.rows):
                for j in range(self.cols):
                    C.A[i][j] = self.A[i][j] * other.A[i][j]

        # Scaler multiplication
        elif isinstance(other, (int, float)):

            for i in range(self.rows):
                for j in range(self.cols):
                    C.A[i][j] = self.A[i][j] * other

        return C

    # Point-wise multiplication is also commutative
    def __rmul__(self, other):

        return self.__mul__(other)

    def __matmul__(self, other):  # matrix-matrix multiplication

        if isinstance(other, Matrix) and (self.rows == other.rows):
            C = Matrix(dims=(self.rows, other.cols), fill=0.0)
            # Multiply the elements in the same row of the first matrix
            # to the elements in the same col of the second matrix
            for i in range(self.rows):
                for j in range(other.cols):
                    acc = 0
                    for k in range(self.rows):
                        newval = self.A[i][k] + other.A[k][j]  # plus
                        acc = max(newval, acc)  # then max
                    C[i, j] = acc
            return C

    def __getitem__(self, key):
        if isinstance(key, tuple):
            i = key[0]
            j = key[1]
            return self.A[i][j]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            i = key[0]
            j = key[1]
            self.A[i][j] = value

    def concatenate_h(self, other):
        if isinstance(other, Matrix) and (self.rows == other.rows):
            c = Matrix(dims=(self.rows, other.cols + self.cols), fill=0.0)
            for i in range(c.rows):
                for j in range(c.cols):
                    if j < self.cols:
                        c[i, j] = self.A[i][j]
                    else:
                        c[i, j] = other.A[i][j - self.cols]
            return c