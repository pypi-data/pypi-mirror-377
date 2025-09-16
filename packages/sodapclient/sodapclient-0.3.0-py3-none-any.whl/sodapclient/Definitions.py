"""
Variable definitions
"""

import numpy


class Definitions:

    """
    Simple 'static' class to provide OpenDAP variable definitions.
    Includes mapping to NumPy variable types where available.
    """

    atomics = {'Byte': numpy.dtype(numpy.byte),
               'Int16': numpy.dtype(numpy.int32),  # Int16->int32 in practice?
               'UInt16': numpy.dtype(numpy.uint32),  # Same assumed for UInt16
               'Int32': numpy.dtype(numpy.int32),
               'UInt32': numpy.dtype(numpy.uint32),
               'Float32': numpy.dtype(numpy.float32),
               'Float64': numpy.dtype(numpy.float64),
               'String': numpy.dtype(numpy.byte),  # Retrieve as byte sequence
               'URL': numpy.dtype(numpy.byte)  # Same as String
               }

    constructors = ['Dataset', 'Array', 'Structure',
                    'Grid', 'Sequence', 'Maps']
    # NB can be in all upper case as well

    dataset = 'Dataset'

    attributes = 'Attributes'
