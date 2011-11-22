from django.conf import settings
import cssutils
import os
import logging
import sys


cssutils.log.setLevel(logging.ERROR)


def run():

    selectors = set()

    for d in (".", "SCSS_CACHE"):
        styles_dir = os.path.join(settings.STATIC_ROOT, d, "styles")

        for filename in os.listdir(styles_dir):
            if not filename.endswith(".css"):
                continue
            if filename.startswith("ie"):
                continue

            print >> sys.stderr, "Processing", filename

            filename = os.path.join(styles_dir, filename)
            sheet = cssutils.parseFile(filename)

            for rule in sheet:
                if not isinstance(rule, cssutils.css.CSSStyleRule):
                    continue
                if rule.style.getPropertyValue("display") == "inline-block":
                    selectors.add(rule.selectorText)

    selectors = sorted(selectors)
    print """%s {
    display: inline;
    zoom: 1;
}""" % ",\n".join(selectors)
