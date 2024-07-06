from functools import reduce


def deep_get(dictionary, keys, default=None):
    """
    Gets the deep value in dictionary,
    For instance the line:
    deep_get({'a': {'b': 1}}, 'a.b')
    returns:
    1
    """
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        keys.split("."),
        dictionary,
    )
