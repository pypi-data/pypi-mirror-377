"""
TestParser class definition
"""

import unittest
from sodapclient.Parser import Parser


class TestParser(unittest.TestCase):

    """
    Test class for Parser class.
    """

    def setUp(self):

        # Create the test string
        self.start_str = 'StartsHere'
        self.data_str = """

blah...
{

    indent stuff...

""" + self.start_str + """{
    DataType1 x[x = 123];
    DataType2 y[y = 456];

    Grid {
     ARRAY:
       DataType3 z[x = 123][y = 456];
     MAPS:
       DataType1 x[x = 123];

       DataType2 y[y = 456];
    } z;

} TestString;

blah...



"""

        self.data_lines = ['blah...',
                           '{', '    indent stuff...',
                           self.start_str + '{',
                           '    DataType1 x[x = 123];',
                           '    DataType2 y[y = 456];',
                           '    Grid {',
                           '     ARRAY:',
                           '       DataType3 z[x = 123][y = 456];',
                           '     MAPS:', '       DataType1 x[x = 123];',
                           '       DataType2 y[y = 456];',
                           '    } z;',
                           '} TestString;', 'blah...']

    def tearDown(self):
        pass

    def test_constructor(self):

        """
        Test the Parser constructor.
        """

        parser = Parser()
        self.assertTrue(type(parser) == Parser)
        return parser

    def test_find_indent_level(self):

        """
        Check that the correct indent level is found.
        """

        parser = self.test_constructor()
        indt = parser.find_indent_level('     abc...  ')
        self.assertEqual(indt, 5)

    def test_find_start(self):

        """
        Check that the correct start line is found.
        """

        parser = self.test_constructor()
        parser.find_start(self.data_str, self.start_str)
        self.assertEqual(parser.data_lines, self.data_lines)
        self.assertEqual(parser.lnum, 3)
        self.assertEqual(parser.indts, [0])
        return parser

    def test_check_line(self):

        """
        Check that lines are handled correctly.
        """

        parser = self.test_find_start()

        do_line = parser.check_line()
        self.assertEqual(do_line, True)
        self.assertEqual(parser.indts, [0, 4])
        self.assertEqual(parser.finished, False)

        do_line = parser.check_line()
        self.assertEqual(do_line, True)
        self.assertEqual(parser.indts, [0, 4])
        self.assertEqual(parser.finished, False)

        parser.lnum = len(parser.data_lines) - 3
        do_line = parser.check_line()
        self.assertEqual(do_line, False)
        self.assertEqual(parser.indts, [0])
        self.assertEqual(parser.finished, True)

if __name__ == "__main__":
    unittest.main()
