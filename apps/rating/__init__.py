

def get_rating_stars_class(rating):
    if not rating:
        return u"s00"
    parts = list(divmod(rating, 1))
    parts[0] = int(parts[0])
    if parts[1] < 0.2:
        parts[1] = 0
    elif parts[1] > 0.8:
        parts[0] += 1
        parts[1] = 0
    else:
        parts[1] = 5
    return "s%i%i" % tuple(parts)


