import cssutils
import os
import logging
import sys


cssutils.log.setLevel(logging.ERROR)


def run():

    selectors = set()

    for styles_dir in ("../media/styles/", "../media/SCSS_CACHE/styles/"):
        styles_dir = os.path.join(os.path.dirname(__file__), styles_dir)
        if not os.path.exists(styles_dir):
            continue

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

    print """%s {
    display: inline;
    zoom: 1;
}""" % ",\n".join(sorted(selectors))
