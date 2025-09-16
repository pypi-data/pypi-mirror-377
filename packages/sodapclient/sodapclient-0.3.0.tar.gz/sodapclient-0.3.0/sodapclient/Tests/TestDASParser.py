"""
TestDASParser class definition
"""

import os
import unittest
from sodapclient.DASParser import DASParser


class TestDASParser(unittest.TestCase):

    """
    Test class for DASParser class.
    """

    def setUp(self):

        # Create the test das string
        self.das_str = """
Attributes {
    lat {
        String name "Latitude";
        String units "deg";
        Float32 minval -90;
        Float32 maxval 90;
    }
    long {
        String name "Longitude";
        String units "deg";
        Float32 minval 0;
        Float32 maxval 360;
    }
    depth {
        String name "Water Depth";
        String units "m";
        Int32 posup -1;
    }
}
"""

        self.das = {'lat': ['String name "Latitude"', 'String units "deg"',
                            'Float32 minval -90', 'Float32 maxval 90'],
                    'long': ['String name "Longitude"', 'String units "deg"',
                             'Float32 minval 0', 'Float32 maxval 360'],
                    'depth': ['String name "Water Depth"', 'String units "m"',
                              'Int32 posup -1']
                    }

        self.test_file_name = 'dasparser_out.txt'

    def tearDown(self):
        if os.path.exists(self.test_file_name):
            os.remove(self.test_file_name)

    def test_constructor(self):

        """
        Test the DASParser constructor.
        """

        parser = DASParser()
        self.assertTrue(type(parser) == DASParser)

    def test_parse(self):

        """
        Test the parse method.
        """

        das_parser = DASParser()
        das_parser.parse(self.das_str)
        self.assertEqual(self.das, das_parser.data)

    def test_print(self):

        """
        Test the print method.
        """

        das_parser = DASParser()
        das_parser.parse(self.das_str)
        das_parser.print_das()

    def test_print_to_file(self):

        """
        Test the print to file method.
        """

        das_parser = DASParser()
        das_parser.parse(self.das_str)
        with open(self.test_file_name, 'wt') as test_file:
            das_parser.print_das_to_file(test_file)
        self.assertEqual(os.path.exists(self.test_file_name), True)


if __name__ == "__main__":
    unittest.main()
