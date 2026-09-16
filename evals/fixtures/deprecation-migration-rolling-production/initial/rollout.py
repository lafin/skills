import hashlib


def use_replacement(account_id, replacement_percent):
    if not 0 <= replacement_percent <= 100:
        raise ValueError("replacement_percent must be between 0 and 100")
    bucket = int.from_bytes(hashlib.sha256(account_id.encode("utf-8")).digest()[:4], "big") % 100
    return bucket < replacement_percent
