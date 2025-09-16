"""
TestVariableLoader class definition
"""

import unittest
from sodapclient.VariableLoader import VariableLoader
import numpy


class TestVariableLoader(unittest.TestCase):

    """
    Test class for VariableLoader class.
    """

    def setUp(self):

        self.url = 'http://myserver.org/mydata'
        # NB: Handler would have removed .html if present
        self.dataset_name = 'TestDataset'
        self.dds = {'lat': ['Float32', [10], ['lat']],
                    'long': ['Float32', [20], ['long']],
                    'depth': ['Int16', [10, 20], ['lat', 'long']]
                    }
        self.depth = numpy.ndarray(shape=[10, 20], dtype='int32')
        # Using int32 for DDS Int16 (see Definitions.py)
        cind = [icl for icl in range(self.depth.shape[1])]
        for rind in range(self.depth.shape[0]):
            self.depth[rind] = cind
            self.depth[rind] *= rind

        self.dim_sels = numpy.ndarray(shape=(2, 3), dtype='int')
        self.dim_sels[0, :] = [0, 4, 9]
        self.dim_sels[1, :] = [0, 2, 19]

        self.depth_sel = self.depth[self.dim_sels[0, 0]: self.dim_sels[0, 2]:
                                    self.dim_sels[0, 1],
                                    self.dim_sels[1, 0]: self.dim_sels[1, 2]:
                                    self.dim_sels[1, 1]]

        self.var_data = '...blah ... xx Int16 depth[lat = 3][long = 10] xx \
        ..Data:\nxxxxyyyy'.encode('utf-8') + self.depth_sel.tobytes()

        self.byte_ord_str = '<'

    def tearDown(self):
        pass

    def test_constructor(self):

        """
        Test the VariableLoader constructor.
        """

        var_loader = VariableLoader(self.url, self.dataset_name, self.dds)
        return var_loader

    def test_variable_name_validity(self):

        """
        Test variable name.
        """

        var_loader = self.test_constructor()
        requrl = var_loader.get_request_url('height', [])
        self.assertEqual(requrl, '')

    def test_number_of_dims(self):

        """
        Test number of dimensions.
        """

        var_loader = self.test_constructor()
        dim_sels = numpy.ndarray(shape=(1, 3), dtype='int32')
        requrl = var_loader.get_request_url('depth', dim_sels)
        self.assertEqual(requrl, '')

    def test_dim_selection(self):

        """
        Test dimension selection.
        """

        var_loader = self.test_constructor()
        dim_sels = self.dim_sels
        dim_sels[1, 2] = 20
        requrl = var_loader.get_request_url('depth', dim_sels)
        self.assertEqual(requrl, '')

    def test_url_construction(self):

        """
        Test URL construction.
        """

        var_loader = self.test_constructor()
        requrl = var_loader.get_request_url('depth', self.dim_sels)
        self.assertEqual(requrl, self.url + '.dods?depth%5B0:4:9%5D%5B0:2:19%5D')

    def test_load_variable(self):

        """
        Test variable loading.
        """

        var_loader = self.test_constructor()
        var = var_loader.load_variable('depth', self.var_data, self.dim_sels,
                                       self.byte_ord_str)
        self.assertTrue(numpy.array_equal(var, self.depth_sel))


if __name__ == "__main__":
    unittest.main()
