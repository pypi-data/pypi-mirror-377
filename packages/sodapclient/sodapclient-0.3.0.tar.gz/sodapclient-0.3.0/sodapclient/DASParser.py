"""
DASParser class definition
"""

from io import TextIOWrapper
from sodapclient.Parser import Parser
from sodapclient.Definitions import Definitions


class DASParser(Parser):

    """
    DASParser class. Extracts and stores the attributes within a DAS string.
    """

    def __init__(self) -> None:

        super().__init__()
        self.dtype = 'Dataset Attribute Structure (DAS)'

    def parse(self, das_str: str) -> None:

        """
        Parse the DAS.
        args...
            das_str: DAS string.
        """

        self.find_start(das_str, Definitions.attributes)

        attr_ind = -1  # Attribute index counter

        # Main loop
        while (not self.finished) & (self.lnum < len(self.data_lines) - 1) & \
              (len(self.indts) > 0):
            do_line = self.check_line()
            if do_line:  # New Attribute
                attr_ind += 1
                attr_name = self.data_lines[self.lnum].split()[0]
                attr_data = []
                while self.check_line():
                    # Remove trailing semicolon
                    attr_data.append(self.data_lines[self.lnum].lstrip()[:-1])
                self.data[attr_name] = attr_data

    def print_das(self, das: dict=None) -> None:

        """
        Print the DAS to the console. DAS can be passed in externally for convenience.
        kwargs...
            das: DAS (dictionary)
        """

        if das is None:
            das = self.data
        self.print_data(self.dtype, das)
        for var in das.keys():
            print('Variable :', var)
            print('Attributes...')
            for l in das[var]:
                print(l)
            print()

    def print_das_to_file(self, file: TextIOWrapper, das: dict=None) -> None:

        """
        Print the DAS to a file. DAS can be passed in externally for convenience.
        args...
            file: file object
        kwargs...
            das: DAS (dictionary)
        """

        if das is None:
            das = self.data
        self.print_data_to_file(self.dtype, das, file)
        for var in das.keys():
            file.write('Variable : ' + var + '\n')
            file.write('Attributes...\n')
            for l in das[var]:
                file.write(l + '\n')
            file.write('\n')
