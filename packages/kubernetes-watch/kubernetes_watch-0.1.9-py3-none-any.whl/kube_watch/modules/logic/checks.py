

def dicts_has_diff(dict_a, dict_b):
    return dict_a != dict_b


def remove_keys(d, keys):
    return {k: v for k, v in d.items() if k not in keys}