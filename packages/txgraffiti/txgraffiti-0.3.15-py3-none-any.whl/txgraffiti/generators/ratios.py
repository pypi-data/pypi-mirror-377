"""
Enumeration generators for ratio-based conjectures.

This module defines functions that generate inequality conjectures of the form
`target >= c * feature` and `target <= c * feature` under Boolean hypotheses,
based on numerical ratios observed in a dataset.
"""


import pandas as pd
from typing import List, Iterator
from fractions import Fraction

from txgraffiti.logic import *
from txgraffiti.generators.registry import register_gen
from txgraffiti.utils.safe_generator import safe_generator

__all__ = [
    'ratios',
]

@safe_generator
@register_gen
def ratios(
    df: pd.DataFrame,
    *,
    features:   List[Property],
    target:     Property,
    hypothesis: Predicate,
) -> Iterator[Conjecture]:
    """
    Generate conjectures comparing the target to scaled versions of the input features
    under a given hypothesis.

    For each feature `f` in `features`, this function computes the minimum and maximum
    values of the ratio `target / f` over the subset of rows where `hypothesis` is true.
    From this, it emits two conjectures:

        hypothesis → (target >= c_min * f)
        hypothesis → (target <= c_max * f)

    where `c_min` and `c_max` are simplified rational approximations of the observed
    minimum and maximum ratios.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataset of known objects and their invariant values.

    features : List[Property]
        A list of feature properties to use in generating ratios with the target.

    target : Property
        The invariant to bound in terms of each feature.

    hypothesis : Predicate
        A Boolean predicate that restricts the rows (objects) over which ratios are computed.

    Yields
    ------
    Conjecture
        An inequality conjecture of the form `target >= c * feature` or
        `target <= c * feature` under the given hypothesis.

    Notes
    -----
    - If the feature column contains zeros under the hypothesis, those entries are skipped.
    - If the hypothesis is not satisfied by any row, nothing is yielded.
    - The resulting bounds are rational approximations using `limit_denominator()`.

    Examples
    --------
    >>> from txgraffiti import KnowledgeTable
    >>> from txgraffiti.generators import ratios
    >>> df = KnowledgeTable({
    ...     'alpha': [1, 2, 3],
    ...     'beta': [3, 1, 1],
    ...     'connected': [True, True, True],
    ...     'tree': [False, False, True],
    ... })
    >>> target = df.alpha
    >>> features = [df.beta]
    >>> hypothesis = df.connected
    >>> for conj in ratios(df, features=features, target=target, hypothesis=hypothesis):
    ...     print(conj)
    <Conj (connected) → (alpha >= (1/3 * beta))>
    <Conj (connected) → (alpha <= (3 * beta))>
    """

    mask = hypothesis(df)
    # if hypothesis never true, nothing to yield
    if not mask.any():
        return

    t_vals = target(df)[mask]
    for f in features:
        f_vals = f(df)[mask]

        # avoid division by zero
        nonzero = f_vals != 0
        if not nonzero.any():
            continue

        ratios = t_vals[nonzero] / f_vals[nonzero]
        cmin, cmax = Fraction(float(ratios.min())).limit_denominator(), Fraction(float(ratios.max())).limit_denominator()

        # build RHS Property-expressions
        low_rhs  = Constant(cmin) * f
        high_rhs = Constant(cmax) * f

        # yield t >= cmin * f
        yield Conjecture(
            hypothesis,
            Inequality(target, ">=", low_rhs)
        )

        # yield t <= cmax * f
        yield Conjecture(
            hypothesis,
            Inequality(target, "<=", high_rhs)
        )
