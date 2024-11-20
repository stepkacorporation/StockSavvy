def choose_plural(amount: int, declensions: tuple) -> str:
    if str(amount).endswith(('0', '5', '6', '7', '8', '9', '11', '12', '13', '14')):
        return f'{amount} {declensions[2]}'
    if str(amount).endswith('1'):
        return f'{amount} {declensions[0]}'
    return f'{amount} {declensions[1]}'
