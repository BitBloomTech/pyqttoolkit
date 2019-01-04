def next_id(root, existing):
    current_ids = sorted(int(i.replace(root, '')) for i in existing if root in i)
    last_id = current_ids[-1] if current_ids else 0
    return f'{root}{last_id + 1}'
