from alerts import build_notice


def render(message):
    notice = build_notice(message)
    return f'{notice["kind"]}: {notice["message"]}'
