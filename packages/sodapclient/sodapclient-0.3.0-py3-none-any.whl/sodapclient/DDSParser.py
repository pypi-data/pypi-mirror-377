"""
DDSParser class definition
"""

from io import TextIOWrapper
from sodapclient.Parser import Parser
from sodapclient.Definitions import Definitions


class DDSParser(Parser):

    """
    Dataset Descriptor Response (dds) parser class.

    Given a DDS string read from a URL, it parses the string to set up
    a DDS dictionary. The dictionary is of form:
    {name : [type, [dims], [assoc_names]]}
    where name is the variable name,
    dims is a list of dimensions,
    assoc_names is a list of associated names.

    See Handler class for comments on constructor handling.

    A single data set is included, i.e. if the URL describes more than one,
    only the first will be included.
    """

    def __init__(self) -> None:

        super().__init__()
        self.dtype = 'Dataset Descriptor Structure (DDS)'

        self.atomic_defs = list(Definitions.atomics.keys())
        self.constructor_defs = Definitions.constructors

        self.dataset_name = 'Undefined'

    def parse(self, dds_str: str) -> None:

        """
        Parse the DDS.
        args...
            dds_str: DDS string
        """

        self.find_start(dds_str, Definitions.dataset)

        # Main loop
        while (not self.finished) and \
              (self.lnum < len(self.data_lines) - 1) and (len(self.indts) > 0):
            do_line = self.check_line()
            if do_line:
                self.process_line()

        if self.finished:
            # Exclude trailing semicolon...
            self.dataset_name = self.data_lines[self.lnum].split()[-1][:-1]

    def process_line(self) -> None:

        """
        Process a line.
        """

        var_type = None
        next_line = self.data_lines[self.lnum]
        segs = next_line.split()
        for adef in self.atomic_defs:
            if segs[0] == adef:
                var_type = adef
                self.read_atomic(next_line, var_type)
                break
        if var_type is None:  # Not an atomic type
            for adef in self.constructor_defs:
                if segs[0] == adef:
                    var_type = adef
                    self.read_constructor(next_line, var_type)
                    break

    def read_atomic(self, line: str, var_type: str) -> None:

        """
        Read an atomic variable.
        args...
            line: line
            var_type: variable type
        """

        # Will still work even if dimensionless...
        var_name = line.split()[1].split('[')[0]
        segs = line.split('=')
        num_dims = len(segs) - 1
        # Remove trailing semicolon...
        if num_dims == 0:
            var_name = var_name[:-1]
        dims = [None] * num_dims
        assoc_names = [None] * num_dims
        for idim in range(num_dims):
            # Remove trailing space...
            assoc_names[idim] = segs[idim].split('[')[-1][:-1]
            dims[idim] = int(segs[idim + 1].split(']')[0])
        self.data[var_name] = [var_type, dims, assoc_names]

    def read_constructor(self, line: str, var_type: str) -> None:

        """
        Reading constructor variables not implemented
        (all variables handled as atomics).
        """

        pass

    def print_dds(self, dataset_name: str=None, dds: dict=None) -> None:

        """
        Print the DDS to the console. Dataset name and DDS
        can be passed in externally for convenience.
        kwargs...
            dataset_name: dataset name (string)
            dds: DDS (dictionary)
        """

        if dataset_name is None:
            dataset_name = self.dataset_name
        if dds is None:
            dds = self.data
        self.print_data(self.dtype, dds)
        print('Dataset name :', dataset_name, '\n')
        for var in dds.keys():
            print('Variable name :', var)
            print('dtype :', dds[var][0])
            print('Dimensions :', dds[var][1])
            print('Associated names :', dds[var][2], '\n')

    def print_dds_to_file(self, file: TextIOWrapper, dataset_name: str=None, dds: dict=None) -> None:

        """
        Print the DDS to a file. Dataset name and DDS
        can be passed in externally for convenience.
        args...
            file_name: file name (string)
        kwargs...
            dataset_name: dataset name (string)
            dds: DDS (dictionary)
        """

        if dataset_name is None:
            dataset_name = self.dataset_name
        if dds is None:
            dds = self.data
        self.print_data_to_file(self.dtype, dds, file)
        file.write('Dataset name : ' + dataset_name + '\n\n')
        for var in dds.keys():
            file.write('Variable name : ' + var + '\n')
            file.write('dtype : ' + dds[var][0] + '\n')
            file.write('Dimensions : ' + str(dds[var][1]) + '\n')
            file.write('Associated names : ' + str(dds[var][2]) + '\n\n')
