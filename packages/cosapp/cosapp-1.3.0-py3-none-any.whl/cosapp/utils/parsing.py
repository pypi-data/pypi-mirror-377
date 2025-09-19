from __future__ import annotations
from collections.abc import Collection


def find_selector(expression: str) -> tuple[str, str]:
    """Decompose a string expression into `basename` and `selector`,
    where `selector` is a suitable mask expression for an array.

    Parameters:
    -----------
    expression [str]: the expression to be parsed.
    
    Returns:
    --------
    baseline, selector [str, str]
    """
    expression = expression.strip()
    left_bracket, right_bracket = brackets = tuple("[]")
    nl = nr = il = 0

    basename, selector = expression, ""  # default

    if expression.endswith(right_bracket):
        i = len(expression)
        for char in reversed(expression):
            i -= 1
            if char == right_bracket:
                nr += 1
            elif char == left_bracket:
                nl += 1
                if nl == nr:
                    prev_char = expression[i - 1] if i > 0 else None
                    if prev_char not in brackets:
                        il = i
                        break
    
    elif expression.endswith(left_bracket):
        nl, nr = 1, 0
    
    balanced = (nl == nr)
    if not balanced:
        raise ValueError(f"Bracket mismatch in {expression!s}")
    if il > 0 or expression.startswith(left_bracket):
        basename = expression[:il]
        selector = expression[il:]

    return basename, selector


def multi_split(expression: str, separators: Collection[str]) -> tuple[list[str], list[str]]:
    """Extension of `str.split`, accounting for more than one split separators.
    
    Parameters
    ----------
    - expression [str]:
        Expression to be split.
    - separators [collection[str]]:
        list/tuple/set of separators.
    
    Returns
    -------
    - expressions [list[str]]:
        list of n split expressions.
    - separators [list[str]]:
        Sequence of (n - 1) separators between split expressions.

    Examples
    --------
    >>> multi_split('a+b-c-d*e', list('+-'))
    ['a', 'b', 'c', 'd*e'], ['+', '-', '-']
    >>> multi_split('a+b-c-d*e', list('*+-'))
    ['a', 'b', 'c', 'd', 'e'], ['+', '-', '-'; '*']
    """
    expressions = [expression]
    sep_list = []

    for separator in set(separators):
        new_list = []
        shift = 0
        for i, expression in enumerate(expressions):
            sublist = expression.split(separator)
            n_hits = len(sublist) - 1
            new_list.extend(sublist)
            if n_hits > 0:
                j = i + shift
                shift += n_hits
                sep_list = sep_list[:j] + [separator] * n_hits + sep_list[j:]
        expressions = list(map(str.strip, new_list))

    return expressions, sep_list


def multi_join(expressions: list[str], separators: list[str], add_space=False) -> str:
    """Reciprocal of `multi_split`.
    
    Parameters
    ----------
    - expressions [list[str]]:
        Expression to be split.
    - separators [list[str]]:
        list of separators.
    - add_space [bool, optional]:
        If `True`, a space character is inserted before and after each separator.
        Defaults to `False`.
    
    Returns
    -------
    expression [str]: Joined expression.

    Examples
    --------
    >>> multi_join(['a', 'b', 'c', 'd', 'e'], ['+', '-', '-', '*'])
    'a+b-c-d*e'
    >>> multi_join(['a', 'b', 'c', 'd', 'e'], ['+', '-', '-', '*'], add_space=True)
    'a + b - c - d * e'
    """
    x = " " if add_space else ""

    output = expressions[0]
    for separator, expression in zip(separators, expressions[1:]):
        output += f"{x}{separator}{x}{expression}"
    
    return output
