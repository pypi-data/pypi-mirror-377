"""
VariableLoader class definition
"""

import numpy
from sodapclient.Definitions import Definitions


class VariableLoader:

    """
    Variable loader class. Does some checks and returns the requested variable
    as a NumPy array.
    """

    def __init__(self, url: str, dataset_name: str, dds: dict) -> None:

        """
        args...
            url: URL
            dataset_name: dataset name (string)
            dds: DDS (dictionary)
        """

        # Get available DDS definitions
        self.url = url
        self.dataset_name = dataset_name
        self.dds = dds

    def get_request_url(self, var_name: str, dim_sels: numpy.ndarray) -> str:

        """
        Returns the URL for a request.
        args...
            var_name: variable name
            dim_sels: dimension selections variable: a numpy ndarray, type int, size N by 3.
                      Each row corresponds to one variable dimension, with columns containing
                      the min, step and max indexes.
        """

        # Check variable exists and dimensions are not exceeded

        if var_name not in self.dds:
            print('VariableLoader: Requested variable not in DDS, stopping.')
            return ''

        var_dims = self.dds[var_name][1]
        num_dims = len(var_dims)
        if (num_dims > 0) and (dim_sels.shape[0] != num_dims):
            print('VariableLoader: Requested number of dimensions incorrect, stopping.')
            return ''

        dims_ok = self.check_dim_sels(var_dims, dim_sels, num_dims)
        if not dims_ok:
            print('VariableLoader: At least one dimension selection request is not valid, stopping.')
            return ''

        # Construct the request url (replace square brackets with hex codes as needed by some servers)

        requrl = self.url + '.dods?' + var_name
        for idim in range(num_dims):
            dimstr = '%5B' + str(dim_sels[idim, 0]) + ':' + \
                     str(dim_sels[idim, 1]) + ':' + \
                     str(dim_sels[idim, 2]) + '%5D'
            requrl += dimstr

        return requrl

    @staticmethod
    def check_dim_sels(var_dims: list, dim_sels: numpy.ndarray, num_dims: int) -> bool:

        """
        Extract dimension selections and check they're valid.
        args...
            var_dims: variable dimensions
            dim_sels: dimension selections (see get_request_url)
            num_dims: number of dimensions
        """

        dims_ok = True
        for idim in range(num_dims):
            if (dim_sels[idim, 0] < 0) or (dim_sels[idim, 1] < 0) or \
               (dim_sels[idim, 2] < 0):
                dims_ok = False
            if (dim_sels[idim, 0] > var_dims[idim] - 1) or \
               (dim_sels[idim, 2] > var_dims[idim] - 1):
                dims_ok = False
            if dim_sels[idim, 2] < dim_sels[idim, 0]:
                dims_ok = False
            if (dim_sels[idim, 0] != dim_sels[idim, 2]) and \
               (dim_sels[idim, 1] > dim_sels[idim, 2]):
                dims_ok = False

        return dims_ok

    def load_variable(self, var_name: str, var_data: bytes, dim_sels: numpy.ndarray, byte_ord_str: str, check_type: bool=True) -> numpy.ndarray:

        """
        Load the requested variable and return as a NumPy array.
        args...
            var_name: variable name
            var_data: variable data (string of bytes)
            dim_sels: dimension selections (see get_request_url)
            byte_ord_str: byte order string: '<' for little endian, '>' for big endian
        kwargs...
            check_type: check header string contains expected variable type
        """

        dims = False
        if dim_sels.shape[1] == 3:
            dims = True
        #  Otherwise size is [1,1] and contains number of elements in
        #  dimensionless data

        if dims:
            boffs = 8
            #  Byte offset for the two occurrences of the number of
            #  elements (int32)
        else:
            boffs = 4
            #  Offset for dimensionless data

        #  Find the header portion of the byte stream
        # (until the 'Data' identifier)

        data_id = 'Data:\n'.encode('utf-8')
        id_len = len(data_id)
        data_len = len(var_data)

        null_ret = numpy.empty(0)

        i = 0
        while (i < data_len - id_len - 1) and (var_data[i:i + id_len] != data_id):
            i += 1
        if var_data[i:i + id_len] != data_id:
            print('VariableLoader: Data start identifier not found, stopping.')
            return null_ret

        data_start_ind = i + id_len
        data_start_ind += boffs

        # Check the var_data byte stream contains the correct variable type
        hdr_str = var_data[:data_start_ind - boffs].decode('utf-8')
        var_type = self.dds[var_name][0]
        if check_type and (var_type not in hdr_str):
            print('VariableLoader: Variable type in requested data header does not match DDS, stopping.')
            return null_ret

        #  Check the var_data byte stream contains the correct
        # variable dimensions

        dim_str = var_name
        if dims:
            dim_str, num_els = self.get_dim_str(dim_sels, var_name)
        else:
            num_els = dim_sels[0, 0]  # Number of elements to retrieve

        if dim_str not in hdr_str:
            print('VariableLoader: Variable dimensions in requested data header do not match DDS, stopping.')
            return null_ret

        # All OK - load the variable

        np_type = Definitions.atomics[var_type]
        data_type = np_type

        if len(byte_ord_str) > 0:
            data_type = np_type.newbyteorder(byte_ord_str)

        lvar = numpy.frombuffer(var_data, dtype=data_type, count=int(numpy.prod(num_els)), offset=data_start_ind)
        if dims:
            var = lvar.reshape(tuple(num_els))
        else:
            var = lvar

        return var

    def get_dim_str(self, dim_sels: numpy.ndarray, var_name: str) -> tuple:

        """
        Get the dimension selection string and number of elements.
        args...
            dim_sels: dimension selections (see get_request_url)
            var_name: variable name
        """

        assoc_names = self.dds[var_name][2]
        dim_str = var_name
        num_els = []
        for idim in range(dim_sels.shape[0]):
            count = 1
            ind = dim_sels[idim, 0]
            while ind < dim_sels[idim, 2]:
                ind += dim_sels[idim, 1]
                count += 1
            if ind > dim_sels[idim, 2]:
                count -= 1
            num_els.append(count)
            dim_str += '[' + assoc_names[idim] + ' = ' + \
                       str(num_els[idim]) + ']'

        return dim_str, num_els
