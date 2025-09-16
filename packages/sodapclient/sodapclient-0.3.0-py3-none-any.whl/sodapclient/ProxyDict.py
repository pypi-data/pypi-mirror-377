"""
ProxyDict class definition
"""


class ProxyDict:

    """
    A class to provide proxy server details.
    Reads in the proxy details from a text file and returns a dictionary of
    proxy strings as required for class urllib.request.ProxyHandler
    Example proxy server text file contained in Examples package.
    """

    def __init__(self, proxy_file_name: str) -> None:

        """
        args...
            proxy_file_name: path to text file containing proxy details
        """

        self.valid_proxy = True
        proxy_config = {}  # This is a convenience dictionary

        with open(proxy_file_name, 'rt') as file:
            for line in file:
                # Assumes newline at end of all lines
                srcdata = line[:-1].split(':')
                if (len(srcdata) > 1) and \
                   ('<' not in srcdata[1]) and ('>' not in srcdata[1]):
                    proxy_config[srcdata[0]] = srcdata[1].strip()  # No spaces

        if ('server' not in proxy_config) or \
           ('port' not in proxy_config) or \
           ('methods' not in proxy_config):
            self.valid_proxy = False
        else:
            # Will read in string so convert to list
            proxy_config['methods'] = proxy_config['methods'].split(',')
            self.proxy_config = proxy_config

    def get_dict(self) -> dict:

        """
        Returns a dictionary containing the proxy data
        as required by urllib.request.ProxyHandler
        """

        proxy_strs = {}

        for method in self.proxy_config['methods']:
            if ('user' in self.proxy_config) and \
               ('password' in self.proxy_config):
                proxy_strs[method] = method + '://' + \
                    self.proxy_config['user'] + ':' + \
                    self.proxy_config['password'] + '@' + \
                    self.proxy_config['server'] + ':' + \
                    str(self.proxy_config['port']) + '/'
            else:
                proxy_strs[method] = method + '://' + \
                    self.proxy_config['server'] + ':' + \
                    str(self.proxy_config['port']) + '/'

        return proxy_strs
