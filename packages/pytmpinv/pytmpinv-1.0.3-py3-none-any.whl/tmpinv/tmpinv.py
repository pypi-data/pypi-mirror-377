import warnings
import numpy                           as np
from   math            import ceil
from   typing          import Sequence
from   collections.abc import Sequence as sq
from   clsp            import CLSP

class TMPinvInputError(Exception):
    """
    Exception class for TMPinv-related input errors.

    Represents internal failures in Tabular Matrix Problems via Pseudoinverse
    Estimation routines due to malformed or missing input. Supports structured
    messaging and optional diagnostic augmentation.

    Parameters
    ----------
    message : str, optional
        Description of the error. Defaults to a generic TMPinv message.

    code : int or str, optional
        Optional error code or identifier for downstream handling.

    Attributes
    ----------
    message : str
        Human-readable error message.

    code : int or str
        Optional error code for custom handling or debugging.

    Usage
    -----
    raise TMPinvInputError("Both b_row and b_col must be provided", code=201)
    """
    def __init__(self, message: str = "An error occurred in TMPinv",
                 code: int | str | None = None):
        self.message = message
        self.code    = code
        full_message = f"{message} (Code: {code})" if code is not None         \
                                                   else message
        super().__init__(full_message)
        
    def __str__(self) -> str:
        return self.message if self.code is None \
                            else f"{self.message} [Code: {self.code}]"
    
    def as_dict(self) -> dict:
        """
        Return the error as a dictionary for structured logging or JSON output.
        """
        return {"error": self.message, "code": self.code}

class TMPinvResult:
    """
    Result container for TMPinv estimation.

    Attributes
    ----------
    full : bool
        Indicates if this result comes from the full (non-reduced) model.

    model : CLSP or list of CLSP
        A single CLSP object in the full model, or a list of CLSP objects
        for each reduced block in the reduced model.

    x : np.ndarray
        Final estimated solution matrix of shape (m, p).
    """
    def __init__(self, full: bool, model, x: np.ndarray):
        self.full  = full
        self.model = model
        self.x     = x

def TMPinvSolve(
    S:             Sequence[Sequence[float]] | None = None,
    M:             Sequence[Sequence[float]] | None = None,
    b_row:         Sequence[float]           | None = None,
    b_col:         Sequence[float]           | None = None,
    b_val:         Sequence[float]           | None = None,
    i:             int                              = 1,
    j:             int                              = 1,
    zero_diagonal: bool                             = False,
    reduced:       tuple[int, int]           | None = None,
    *args, **kwargs
) -> TMPinvResult:
    """
    Solve a tabular matrix estimation problem via Convex Least Squares
    Programming (CLSP).

    Parameters
    ----------
    S : array_like of shape (m + p, m + p), optional
        A diagonal sign slack (surplus) matrix with entries in {0, ±1}.
        -  0 enforces equality (== b_row or b_col),
        -  1 enforces a lower-than-or-equal (≤) condition,
        - –1 enforces a greater-than-or-equal (≥) condition.
        The first `m` diagonal entries correspond to row constraints,
        and the remaining `p` to column constraints.
    M : array_like of shape (k, m * p), optional
        A model matrix, for example, with entries in {0, 1}. Each row defines a
        linear restriction on the flattened solution matrix. The corresponding
        right-hand side values must be provided in `b_val`. This block is
        used to encode known cell values.
    b_row : array_like of shape (m,)
        Right-hand side vector of row totals.
    b_col : array_like of shape (p,)
        Right-hand side vector of column totals.
    b_val : array_like of shape (k,)
        Right-hand side vector of known cell values.
    i : int, default = 1
        Number of row groups.
    j : int, default = 1
        Number of column groups.
    zero_diagonal : bool, default = False
        If True, enforces the zero diagonal.
    reduced : tuple of (int, int), optional
        Dimensions of the reduced problem.
        If specified, the problem is estimated as a set of reduced problems
        constructed from contiguous submatrices of the original table.
        For example, reduced = (6, 6) implies 5×5 data blocks with 1 slack
        row and 1 slack column each (edge blocks may be smaller).

    Returns
    -------
    TMPinvResult
        An object containing the fitted CLSP model(s) and the solution
        matrix `x`.

    Notes
    ----
    In the reduced model, `S` is ignored. Slack behavior is derived implicitly
    from block-wise marginal totals. Likewise, `M` must be a row subset of an
    identity matrix (i.e., diagonal-only). Arbitrary or non-diagonal model
    matrices cannot be mapped to reduced blocks, making the model infeasible.
    """
    # (m), (p) Process the parameters, assert conformity, and get dimensions
    if  b_row is None or b_col is None:
        raise TMPinvInputError("Both b_row and b_col must be provided.")
    if  len(b_row) < 2 or len(b_col) < 2:
        raise TMPinvInputError("Minimum length for b_row and b_col is 2.")
    if  not np.isfinite(b_row).all() or not np.isfinite(b_col).all():
        raise TMPinvInputError("b_row and b_col must not contain inf or NaN.")
    b_row = np.asarray(b_row, dtype=np.float64).reshape(-1, 1)
    b_col = np.asarray(b_col, dtype=np.float64).reshape(-1, 1)
    m     = b_row.shape[0]
    p     = b_col.shape[0]
    if  S     is not None:
        S = np.asarray(S, dtype=np.float64)
        if (not np.all((S == -1) | (S == 0) | (S == 1)) or
                np.abs(S).sum(axis=0).max() > 1         or
                np.abs(S).sum(axis=1).max() > 1):
            raise TMPinvInputError("S must be a zero-padded subset of ±I.")
    if  M     is not None:
        if  b_val is None:
            raise TMPinvInputError("Both M and b_val must be defined.")
        M = np.asarray(M, dtype=np.float64)
        if  M.ndim == 1:
            M = M.reshape(1, -1)
        if  M.shape[1] != m * p:
            raise TMPinvInputError(f"M must have exactly {m * p} columns.")
    if  b_val is not None:
        if  M     is None:
            raise TMPinvInputError("Both M and b_val must be defined.")
        if not np.isfinite(b_val).all():
            raise TMPinvInputError("b_val must not contain inf or NaN.")
        b_val = np.asarray(b_val, dtype=np.float64).reshape(-1, 1)
    if  M is not None and b_val is not None:
        if  M.shape[0] != b_val.shape[0]:
            raise TMPinvInputError(f"M and b_val must have the same number "
                                   f"of rows: "
                                   f"{M.shape[0]} vs {b_val.shape[0]}")
    kw = {k: v for k, v in kwargs.items() if k not in {"b", "S", "M",
                                                       "m", "p",
                                                       "i", "j",
                                                       "zero_diagonal"}}

    # perform full estimation and return the result
    if  reduced is None:
        result   = TMPinvResult(True,  None, np.empty((m, p), dtype=float))
        b_blocks = [b_row, b_col]
        if b_val is not None:
            b_blocks.append(b_val)
        b = np.vstack(b_blocks)
        result.model = CLSP().solve(*args,
                                    problem='ap', b=b, S=S, M=M,
                                    m=m,
                                    p=p,
                                    i=i,
                                    j=j,
                                    zero_diagonal=zero_diagonal,
                                    **kw)
        result.x = result.model.x

    # perform reduced estimation and return the result
    else:
        if  reduced[0] < 3 or reduced[1] < 3:
            raise TMPinvInputError("Each reduced block must be at least "
                                   "(3, 3) to allow a solvable CLSP submatrix "
                                   "with a slack (surplus) structure.")
        result   = TMPinvResult(False, [], np.empty((m, p), dtype=float))
        m_subset = reduced[0] - 1
        p_subset = reduced[1] - 1
        if  zero_diagonal:                             # not processed by CLSP
            M_diag = np.zeros((min(m, p), m * p))
            b_diag = np.zeros((min(m, p),     1))
            for k in range(min(m, p)):
                M_diag[k, k * p + k] = 1
            M, idx = np.unique(M_diag.copy() if M     is None or M.size     == 0
                                             else np.vstack([M,     M_diag]),
                               axis=0,       return_index=True)
            b_val = (b_diag.copy()           if b_val is None or b_val.size == 0
                                             else np.vstack([b_val, b_diag])
                    )[idx.reshape(-1)]
            del M_diag, b_diag, idx
        if  M is not None:
            if not all(np.count_nonzero(row) == 1 and
                       np.all((row == 0) | (row == 1)) for row in M):
                raise TMPinvInputError("M must be a row subset of the identity "
                                       "matrix in the reduced model.")
            M = (np.abs(np.sign(M)) * b_val).sum(axis=0).reshape(m, p)
        if  S is not None:
            warnings.warn("User-provided S is ignored in the reduced model.",
                          UserWarning)
        for row_block in range(ceil(m / m_subset)):
            for col_block in range(ceil(p / p_subset)):
                m_start  = row_block * m_subset
                m_end    = min(m_start + m_subset, m)
                p_start  = col_block * p_subset
                p_end    = min(p_start + p_subset, p)
                S        = np.ones(((m_end - m_start) + (p_end - p_start), 1))
                b_blocks = [b_row[m_start:m_end].reshape(-1, 1),
                            b_col[p_start:p_end].reshape(-1, 1)]
                M_subset, b_val_subset = None, None
                if  M is not None:
                    M_subset     = np.diag(np.sign(M[m_start:m_end,
                                                     p_start:p_end]).flatten())
                    b_val_subset = M[m_start:m_end,
                                     p_start:p_end].reshape(-1, 1)
                    if np.any(M_subset):               # drop zero rows
                        nonzero_rows = np.diag(M_subset) != 0
                        M_subset     = M_subset[nonzero_rows]
                        b_val_subset = b_val_subset[nonzero_rows].reshape(-1, 1)
                        b_blocks.append(b_val_subset)
                    else:
                        M_subset, b_val_subset = None, None
                b        = np.vstack(b_blocks)
                tmp      = CLSP().solve(*args,
                                        problem='ap', b=b, S=S, M=M_subset,
                                        m=m_end - m_start,
                                        p=p_end - p_start,
                                        i=i,
                                        j=j,
                                        zero_diagonal=False,
                                        **kw)
                result.model.append(tmp)
                result.x[m_start:m_end, p_start:p_end] = tmp.x

    return result

def tmpinv(
    bounds:          list[tuple[float | None, float | None]] | \
                          tuple[float | None, float | None]  | None = None,
    replace_value:   float                                   | None = np.nan,
    tolerance:       float = np.sqrt(np.finfo(float).eps),
    iteration_limit: int                                   = 50,
    *args, **kwargs
) -> TMPinvResult:
    """
    Solve a tabular matrix estimation problem via Convex Least Squares
    Programming (CLSP) with bound-constrained iterative refinement.

    Parameters
    ----------
    bounds : sequence of (low, high), optional
        Bounds on cell values. If a single tuple (low, high) is given, it
        is applied to all m * p cells. Example: (0, None).
    replace_value : float or None, default = np.nan
        Final replacement value for any cell in the solution matrix that
        violates the specified bounds by more than the given tolerance.
    tolerance : float, optional
        Convergence tolerance for bounds. Default is the square root of
        machine epsilon.
    iteration_limit : int, default = 50
        Maximum number of iterations allowed in the refinement loop.
    *args, **kwargs : additional arguments
        Passed directly to TMPinvSolve().

    Returns
    -------
    TMPinvResult
        An object containing the fitted CLSP model(s) and the solution
        matrix `x`.
    """
    # (n_cells) Perform initial estimation and get cell count
    result  = TMPinvSolve(*args, **kwargs)
    n_cells = result.x.shape[0] * result.x.shape[1]
    if  bounds is None:
        bounds = (None, None)
    if  isinstance(bounds, tuple):
        bounds = [bounds] * n_cells                    # replicate (low, high)
    elif   isinstance(bounds, sq):                     # normalize bounds
        if len(bounds) > 1 and len(bounds) != n_cells:
            raise TMPinvInputError(f"Bounds length {len(bounds)} does not "
                                   f"match number of variables {n_cells}.")
        elif len(bounds) == 1:
            bounds = bounds * n_cells                  # replicate (low, high)
    if  all(l is None and h is None for l, h in bounds):
        return result                                  # finish if unbounded
    if  any((l is not None and l < 0) or
            (h is not None and h < 0) for l, h in bounds):
        raise TMPinvInputError("Negative lower or upper bounds are not "
                               "allowed in tabular matrix programs.")
    kw = {k: v for k, v in kwargs.items() if k not in {"M", "b_val"}}

    # (result) Perform bound-constrained iterative refinement
    for _ in range(iteration_limit):
        M_idx, b_val = [], []
        x = result.x.reshape(-1, 1)
        for i, (v, (l, h)) in enumerate(zip(x, bounds)):
            v = float(v.item())
            if ((l is not None and v < l - tolerance) or                       \
                (h is not None and v > h + tolerance)):
                continue                               # skip out-of-bounds
            M_idx.append(i)
            b_val.append(v)
        if len(M_idx) < n_cells:
            M      = np.eye(n_cells, dtype=np.float64)[M_idx]
            result = TMPinvSolve(*args, M=M, b_val=b_val, **kw)
        else:
            break

    # (result) Replace out-of-bound values with `replace_value`
    x        = result.x.reshape(-1, 1)
    x_lb     = np.array([l if l is not None else -np.inf
                         for  l, _ in bounds]).reshape(-1, 1)
    x_ub     = np.array([h if h is not None else  np.inf
                         for  _, h in bounds]).reshape(-1, 1)
    x[(x < x_lb - tolerance) | (x > x_ub + tolerance)] = replace_value
    result.x = x.reshape(result.x.shape)

    return result
