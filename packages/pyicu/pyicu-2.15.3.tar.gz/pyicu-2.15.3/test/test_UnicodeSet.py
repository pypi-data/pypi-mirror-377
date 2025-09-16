# ====================================================================
# Copyright (c) 2024-2024 Open Source Applications Foundation.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# ====================================================================

import sys, os, six

from unittest import TestCase, main
from icu import *


class TestUnicodeSet(TestCase):

    def testIterators(self):

        a = UnicodeSet("[a-d{abc}{de}]")
        self.assertEqual(['a', 'b', 'c', 'd', 'abc', 'de'], list(a))
        self.assertEqual(['a', 'b', 'c', 'd'], list(a.codePoints()))
        self.assertEqual(['abc', 'de'], list(a.strings()))

        a = UnicodeSet("[abcçカ🚴{}{abc}{de}]")
        self.assertEqual([('a', 'c'), ('ç', 'ç'), ('カ', 'カ'), ('🚴', '🚴')],
                         list(a.ranges()))


if __name__ == "__main__":
    main()
