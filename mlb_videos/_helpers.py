import os


def get_file_information(file: str) -> dict:
    return {
        "filename": os.path.basename(file),
        "filepath": file,
        "name": os.path.splitext(os.path.basename(file))[0],
        "path": os.path.dirname(file),
        "ext": os.path.splitext(file)[1],
    }


def update_nested_dict_by_key(in_dict, key, value):
    for k, v in in_dict.items():
        if key == k:
            in_dict[k] = value
        elif isinstance(v, dict):
            update_nested_dict_by_key(v, key, value)
        elif isinstance(v, list):
            for o in v:
                if isinstance(o, dict):
                    update_nested_dict_by_key(o, key, value)


def update_nested_dict_by_val(d: dict, old: str, new: str) -> dict:
    x = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = update_nested_dict_by_val(v, old, new)
        elif isinstance(v, list):
            v = update_nested_dict_by_val_list(v, old, new)
        elif isinstance(v, str):
            v = v.replace(old, new)
        x[k] = v
    return x


def update_nested_dict_by_val_list(l: list, old: str, new: str) -> list:
    x = []
    for e in l:
        if isinstance(e, list):
            e = update_nested_dict_by_val_list(e, old, new)
        elif isinstance(e, dict):
            e = update_nested_dict_by_val(e, old, new)
        elif isinstance(e, str):
            e = e.replace(old, new)
        x.append(e)
    return x


def update_nested_dict_multiple_keys(d: dict, **kwargs) -> dict:
    for k, v in kwargs.items():
        update_nested_dict_by_key(in_dict=d, key=k, value=v)
    return d


def remove_none_values(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_none_values(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)(
            (remove_none_values(k), remove_none_values(v))
            for k, v in obj.items()
            if k is not None and v is not None
        )
    else:
        return obj
