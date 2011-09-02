import re


MULTIPLE_SPACE_RE = re.compile(r"( ){2,}")
MULTIPLE_NEWLINE_RE = re.compile("\n{3,}")


def reduce_whitespace(text):
    ''' Replace multiple space chars with single space char. Do the same with
        multiple newline chars. '''
    text = MULTIPLE_SPACE_RE.sub(u" ", text)
    text = MULTIPLE_NEWLINE_RE.sub(u"\n\n", text)
    return text


def update_item(item, **kwargs):
    item.__class__.objects.filter(pk=item.pk).update(**kwargs)
    for key, value in kwargs.items():
        setattr(item, key, value)
