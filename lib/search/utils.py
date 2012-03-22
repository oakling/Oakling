def change_keys(key_map, old_dict):
    new_dict = {}
    for (new_key, old_key) in key_map.items():
        if old_key in old_dict:
            new_dict[new_key] = old_dict[old_key]
    return new_dict
