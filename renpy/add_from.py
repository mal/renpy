# Copyright 2004-2025 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import division, absolute_import, with_statement, print_function, unicode_literals
from renpy.compat import PY2, basestring, bchr, bord, chr, open, pystr, range, round, str, tobytes, unicode  # *


import collections
import renpy
import os

# A map from filename to position, target label pairs.
missing = collections.defaultdict(list)


def report_missing(target, filename, loc):
    """
    Reports that the call statement starting at `loc` in `filename`
    is missing a from clause.
    """

    missing[filename].append((loc, target))


# Labels that we've created while running add_from.
new_labels = set()


def generate_label(target):
    """
    Generate a reasonable and unique new label for a call to `target`.
    """

    target = target.replace(".", "_")

    n = 0

    while True:
        if n:
            label = "_call_{}_{}".format(target, n)
        else:
            label = "_call_{}".format(target)

        if not renpy.exports.has_label(label) and not (label in new_labels):
            break

        n += 1

    new_labels.add(label)
    return label


def process_file(fn):
    """
    Adds missing from clauses to `fn`.
    """

    if not os.path.exists(fn):
        return

    renpy.scriptedit.ensure_loaded(fn)

    edits = missing[fn]
    edits.sort()

    with open(fn, "r", encoding="utf-8") as f:
        data = f.read()

    # How much of the input has been consumed.
    consumed = 0

    # The output.
    output = ""

    for loc, target in edits:
        if loc not in renpy.scriptedit.lines:
            continue

        end = renpy.scriptedit.lines[loc].end

        output += data[consumed:end]
        consumed = end

        output += " from {}".format(generate_label(target))

    output += data[consumed:]

    with open(fn + ".new", "w", encoding="utf-8") as f:
        f.write(output)

    try:
        os.unlink(fn + ".bak")
    except Exception:
        pass

    os.rename(fn, fn + ".bak")
    os.rename(fn + ".new", fn)


def clear():
    """
    Clears the list of missing from clauses.
    """

    missing.clear()


def add_from():
    renpy.arguments.takes_no_arguments("Adds from clauses to call statements that are missing them.")

    for fn in missing:
        if fn.startswith(renpy.config.gamedir):
            process_file(fn)

    return False


renpy.arguments.register_command("add_from", add_from)
