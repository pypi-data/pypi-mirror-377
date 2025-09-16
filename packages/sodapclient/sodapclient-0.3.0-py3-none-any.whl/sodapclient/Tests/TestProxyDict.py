"""
TestProxyDict class definition
"""

import unittest
from os import remove
from sodapclient.ProxyDict import ProxyDict


class TestProxyDict(unittest.TestCase):

    """
    Test class for ProxyDict class.
    """

    def setUp(self):

        # Define the text proxy details
        self.proxy_config = {'user': 'Me',
                             'password': 'abracadabra',
                             'server': 'magic.co.uk',
                             'port': '1234',
                             'methods': ['http', 'https', 'ftp', 'socks']}

        # Write the test proxy details to the file
        self.proxy_file_name = 'ProxyDictTests.txt'
        file = open(self.proxy_file_name, 'wt')
        file.write('user' + ':' + self.proxy_config['user'] + '\n')
        file.write('password' + ':' + self.proxy_config['password'] + '\n')
        file.write('server' + ':' + self.proxy_config['server'] + '\n')
        file.write('port' + ':' + str(self.proxy_config['port']) + '\n')
        file.write('methods' + ':')
        # Loop is a bit clunky but needed to avoid trailing comma...
        for method in range(len(self.proxy_config['methods'])):
            if method < len(self.proxy_config['methods']) - 1:
                file.write(self.proxy_config['methods'][method] + ',')
            else:
                file.write(self.proxy_config['methods'][method] + '\n')
        file.close()

    def tearDown(self):
        remove(self.proxy_file_name)

    def test_constructor(self):

        """
        Test the ProxyDict constructor.
        """

        pdict = ProxyDict(self.proxy_file_name)
        self.assertEqual(self.proxy_config, pdict.proxy_config)

    def test_get_dict(self):

        """
        Define the dictionary which should be returned and test for it.
        """

        proxy_test_dict = {'http': 'http://Me:abracadabra@magic.co.uk:1234/',
                           'https': 'https://Me:abracadabra@magic.co.uk:1234/',
                           'ftp': 'ftp://Me:abracadabra@magic.co.uk:1234/',
                           'socks': 'socks://Me:abracadabra@magic.co.uk:1234/'}
        pdict = ProxyDict(self.proxy_file_name)
        tdict = pdict.get_dict()
        self.assertEqual(proxy_test_dict, tdict)


if __name__ == "__main__":
    unittest.main()
