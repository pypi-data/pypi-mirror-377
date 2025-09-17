"""Helper functions for operating Dynamanager."""

from typing import Union


def resolve_dot_notation_accessor(
    key: str, depth: int = 1
) -> Union[tuple[str, None], tuple[str, ...]]:
    """Split a string on dot characters with variable max splits.

    Used to manage dot notation between Dynamanager and Dynaconf.

    Parameters
    ----------
    key : str
        String key with or without dot characters present for splitting.
    dpeth : int, default 1
        Number of times to split the string on dots, to be passed to the `maxsplit`
        argument of `str.split`.

    Returns
    -------
    tuple
        Tuple of variable length containing the split elements for further operations.
    """
    split = tuple(key.split(".", maxsplit=depth))

    if len(split) == 1 and depth == 1:
        return (key, None)

    return split
