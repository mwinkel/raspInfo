def format_gib(num, suffix='B'):
    num /= 1024.0
    return "%.2f%s%s" % (num, 'Gi', suffix)

def format_common(num, suffix='B'):
    for unit in ['Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
