# Tabular Matrix Problems via Pseudoinverse Estimation

The **Tabular Matrix Problems via Pseudoinverse Estimation (TMPinv)** is a two-stage estimation method that reformulates structured table-based systems — such as allocation problems, transaction matrices, and input–output tables — as structured least-squares problems. Based on the [Convex Least Squares Programming (CLSP)](https://pypi.org/project/pyclsp/ "Convex Least Squares Programming") framework, TMPinv solves systems with row and column constraints, block structure, and optionally reduced dimensionality by (1) constructing a canonical constraint form and applying a pseudoinverse-based projection, followed by (2) a convex-programming refinement stage to improve fit, coherence, and regularization (e.g., via Lasso, Ridge, or Elastic Net). All calculations are performed in numpy.float64 precision.

## Installation

```bash
pip install tmpinv
```

## Quick Example

```python
import numpy as np
from tmpinv import tmpinv

# Define a 10×10 matrix with consistent row and column sums
X_true = np.array([
[ 0,  4,  6,  8,  7, 10,  9,  5,  6, 13],
[ 6,  0,  9,  6,  5,  4, 13, 10,  8,  8],
[ 7, 10,  0, 12, 11,  5,  4,  3, 10, 10],
[11, 12,  5,  0, 12, 13,  4,  2,  4, 10],
[13,  5, 11, 11,  0,  3, 11,  6, 12,  5],
[ 4, 12, 13,  4, 11,  0,  3,  3,  4, 10],
[ 6,  9,  4, 13,  4, 13,  0, 12,  3, 11],
[10,  6, 11,  5, 12,  4, 10,  0, 13,  4],
[12, 13,  5, 14,  4, 11,  4, 13,  0,  9],
[ 5,  6, 12, 12, 10,  3, 13,  4, 11,  0]
], dtype=np.float64)

# Get row and column sums
b_row = X_true.sum(axis=1)
b_col = X_true.sum(axis=0)

# Get known values
M = np.eye(100)[[1, 2, 3, 4, 5]]
b_val = X_true[0, [1, 2, 3, 4, 5]]

# Run bounded tmpinv
result = tmpinv(
    M=M,
    b_row=b_row,
    b_col=b_col,
    b_val=b_val,
    zero_diagonal=True,
    bounds=(0, 15),
    replace_value=0
)

# Reshape result and display checks
print("Estimated matrix:\n", np.round(result.x, 2))
print("\nRow sums:   ", np.round(result.x.sum(axis=1), 2))
print("Column sums:", np.round(result.x.sum(axis=0), 2))
```

## User Reference

For comprehensive information on the estimator’s capabilities, advanced configuration options, and implementation details, please refer to the [pyclsp module](https://pypi.org/project/pyclsp/ "Convex Least Squares Programming"), on which TMPinv is based.

**TMPINV Parameters:**  

`S` : *array_like* of shape *(m + p, m + p)*, optional  
A diagonal sign slack (surplus) matrix with entries in *{0, ±1}*.  
-   *0* enforces equality (== `b_row` or `b_col`),  
-  *1* enforces a lower-than-or-equal (≤) condition,  
- *–1* enforces a greater-than-or-equal (≥) condition.  

The first `m` diagonal entries correspond to row constraints, and the remaining `p` to column constraints. Please note that, in the reduced model, `S` is ignored: slack behavior is derived implicitly from block-wise marginal totals.

`M` : *array_like* of shape *(k, m * p)*, optional  
A model matrix with entries in *{0, 1}*. Each row defines a linear restriction on the flattened solution matrix. The corresponding right-hand side values must be provided in `b_val`. This block is used to encode known cell values. Please note that, in the reduced model, `M` must be a row subset of an identity matrix (i.e., diagonal-only). Arbitrary or non-diagonal model matrices cannot be mapped to reduced blocks, making the model infeasible.

`b_row` : *array_like* of shape *(m,)*  
Right-hand side vector of row totals. Please note that both `b_row` and `b_col` must be provided.

`b_col` : *array_like* of shape *(p,)*  
Right-hand side vector of column totals. Please note that both `b_row` and `b_col` must be provided.

`b_val` : *array_like* of shape *(k,)*  
Right-hand side vector of known cell values.

`i` : *int*, default = *1*  
Number of row groups.

`j` : *int*, default = *1*  
Number of column groups.

`zero_diagonal` : *bool*, default = *False*  
If *True*, enforces the zero diagonal.

`reduced` : *tuple* of *(int, int)*, optional  
Dimensions of the reduced problem. If specified, the problem is estimated as a set of reduced problems constructed from contiguous submatrices of the original table. For example, `reduced` = *(6, 6)* implies *5×5* data blocks with *1* slack row and *1* slack column each (edge blocks may be smaller).

`symmetric` : *bool*, default = *False*
If True, enforces symmetry of the estimated solution matrix as: x = 0.5 * (x + x.T)   
Symmetrization can slightly alter row/column totals. For exact symmetry under all constraints, add explicit symmetry constraints to M in a full-model solve instead of using this flag.

`bounds` : *sequence* of *(low, high)*, optional  
Bounds on cell values. If a single tuple *(low, high)* is given, it is applied to all `m` * `p` cells. Example: *(0, None)*.

`replace_value` : *float* or *None*, default = *np.nan*  
Final replacement value for any cell in the solution matrix that violates the specified bounds by more than the given tolerance.

`tolerance` : *float*, default = *square root of machine epsilon*  
Convergence tolerance for bounds.

`iteration_limit` : *int*, default = *50*  
Maximum number of iterations allowed in the refinement loop.

**CLSP Parameters:**  

`r` : *int*, default = *1*  
Number of refinement iterations for the pseudoinverse-based estimator.

`Z` : *np.ndarray* or *None*  
A symmetric idempotent matrix (projector) defining the subspace for Bott–Duffin pseudoinversion. If *None*, the identity matrix is used, reducing the Bott–Duffin inverse to the Moore–Penrose case.

`final` : *bool*, default = *True*  
If *True*, a convex programming problem is solved to refine `zhat`. The resulting solution `z` minimizes a weighted L1/L2 norm around `zhat` subject to `Az = b`.

`alpha` : *float*, *list[float]* or *None*, default = *None*  
    Regularization parameter (weight) in the final convex program:  
    - `α = 0`: Lasso (L1 norm)  
    - `α = 1`: Tikhonov Regularization/Ridge (L2 norm)  
    - `0 < α < 1`: Elastic Net
    If a scalar float is provided, that value is used after clipping to [0, 1].
    If a list/iterable of floats is provided, each candidate is evaluated via a full solve, and the α with the smallest NRMSE is selected.
    If None, α is chosen, based on an error rule: α = min(1.0, NRMSE_{α = 0} / (NRMSE_{α = 0} + NRMSE_{α = 1} + tolerance))   

`*args`, `**kwargs` : optional  
CVXPY arguments passed to the CVXPY solver.

**Returns:**  
*TMPinvResult*

`TMPinvResult.full` : *bool*  
Indicates if this result comes from the full (non-reduced) model.

`TMPinvResult.model` : *CLSP* or *list* of *CLSP*  
A single CLSP object in the full model, or a list of CLSP objects for each reduced block in the reduced model.

`TMPinvResult.x` : *np.ndarray*  
Final estimated solution matrix of shape *(m, p)*.

## Bibliography

To be added.

## License

MIT License — see the [LICENSE](LICENSE) file.
