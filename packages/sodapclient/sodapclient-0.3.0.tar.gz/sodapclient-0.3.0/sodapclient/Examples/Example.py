"""
Example use of sodapclient.
To run this example at the command line enter: python3 Example.py
"""

import numpy

from sodapclient.Handler import Handler

def run_example():

    # Define the URL (one of the datasets available at the official
    # OpenDAP test server):
    url = 'http://test.opendap.org/opendap/hyrax/data/nc/sst.mnmean.nc.gz.html'

    # Initialise handler, which will also get the DDS & DAS
    handler = Handler(url, proxy_file_name='proxyserver.txt')

    # We'll access the SST data over the last 2 times, the last 3 lats and the
    # last 4 longs available...

    # Set up the arrays for the required dimensions, shape 1x3 for map variables
    # and nx3 for data variables with n dimensions
    time_dims = numpy.array([[1800, 10, 1810]])  # Time indices 1800 and 1810
    lat_dims = numpy.array([[70, 2, 74]])  # Latitude indices 70, 72 and 74
    lon_dims = numpy.array([[80, 1, 83]])  # Longitude indices 80 to 83
    sst_dims = numpy.array([time_dims[0], lat_dims[0], lon_dims[0]])

    byte_order = '>'  # Big Endian

    # Get the data and the dimension variables

    handler.get_variable('time', time_dims, byte_order)
    handler.get_variable('lat', lat_dims, byte_order)
    handler.get_variable('lon', lon_dims, byte_order)
    handler.get_variable('sst', sst_dims, byte_order)

    handler.print()  # Print the DDS, DAS and data to screen

    # Then get access to any variable from the handler's variables dictionary, e.g.

    sst = handler.variables['sst']
    print('\nSST...\n', sst)


if __name__ == '__main__':
    run_example()
