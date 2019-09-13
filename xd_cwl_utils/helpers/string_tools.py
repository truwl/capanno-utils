
from urllib.parse import urlparse

def uri_name(input_uri):
    # return the part after the '#'
    d = urlparse(input_uri)
    if d.fragment:
        return d.fragment
    return d.path.split("#")[-1]