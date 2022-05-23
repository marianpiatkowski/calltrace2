# -*- python-indent-offset: 4 -*-
"""
Copyright (C) 2022-  Marian Piatkowski

This file is a part of calltrace2.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import time
import platform
import unittest
import calltrace2_binutils

class TestBinUtils(unittest.TestCase) :
    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        self.binutils = \
            calltrace2_binutils.BinUtilsFactory().get_binutilizer(platform.system())
        self.time_start = 0.0

    def setUp(self) :
        self.time_start = time.time()

    def tearDown(self) :
        time_end = time.time()
        print(f"=== Execution time of {self.id()}, {(time_end-self.time_start):.3f}s")

    def test_function_names_hello(self) :
        result = self.binutils.get_function_names('hello', verbose=True)
        self.assertTrue(result)
        function_names = [ name for name, _ in result ]
        self.assertIn('say_hello()', function_names)

    def test_function_names_test(self) :
        result = self.binutils.get_function_names('test', verbose=True)
        self.assertTrue(result)
        function_names = [ name for name, _ in result ]
        expected_names = [
            'func1()',
            'func2()',
            'func2_1()',
            'func3()',
            'func3_1()',
            'func4()',
            'func5()',
            'func5_1()',
            'func6()',
            'func7()',
            'func7_1()',
            'func8()',
            'func9()' ]
        for name in expected_names :
            self.assertIn(name, function_names)

if __name__ == '__main__' :
    unittest.main()
