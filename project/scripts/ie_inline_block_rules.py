import cssutils
import os
import logging
import sys


cssutils.log.setLevel(logging.ERROR)


def run():

    selectors = []

    styles_dir = os.path.join(os.path.dirname(__file__), "../media/styles/")

    for dirpath, dirnames, filenames in os.walk(styles_dir):
        for filename in filenames:
            if not filename.endswith(".css") or filename.startswith("ie") or filename.startswith("_"):
                continue

            filename = os.path.join(dirpath, filename)

            print >> sys.stderr, "Processing", os.path.relpath(filename, styles_dir)

            sheet = cssutils.parseFile(filename)

            for rule in sheet:
                if not isinstance(rule, cssutils.css.CSSStyleRule):
                    continue
                if rule.style.getPropertyValue("display") == "inline-block":
                    selectors.append(rule.selectorText)

    selectors.sort()
    print """%s {
    display: inline;
    zoom: 1;
}""" % ",\n".join(selectors)
