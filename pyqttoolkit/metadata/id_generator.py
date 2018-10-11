def next_id(root, existing):
    current_ids = sorted(i for i in existing if root in i)
    last_id = int(current_ids[-1].replace(root, '')) if current_ids else 0
    return f'{root}{last_id + 1}'
