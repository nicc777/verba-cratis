# Command Line Arguments

Git URL and Web URL Extensions

For Git URL's the application provides for some extensions to the standard Git URL in order to specify the following optional parameters. Essentially the application supports additional parameters added with a zero-terminated character that is URL encoded in the full URL string.

The following parameters can be added:

* `branch` (Default='main') - specify the branch to checkout after cloning
* `relative_start_directory` (Default='/') - Specify the default relative directory to change into once the repository is clones and the branch is checked out.
* `ssh_private_key_path` (Default=None) - Specify a specific SSH private key when using SSH
* `set_no_verify_ssl` (Default=False) - Specify if SSL/TLS certificates needs to be validated when using HTTPS

Examples:

1) Specify only a branch for an SSH repository: 
    git@github.com:nicc777/verba-cratis-test-infrastructure.git%00branch%3Dtest-branch

2) Example HTTPS with certificate validation skipped and changing into a specific directory of a branch
    https://github.com/nicc777/verba-cratis-test-infrastructure.git%00branch%3Dtest-branch%00relative_start_directory%3D/experiment%00set_no_verify_ssl%3Dtrue

In Python, you can easily construct the final URL with the following (using example 2):

```python
>>> import urllib
>>> from urllib.parse import urlparse
>>> encoded_str = urllib.parse.quote_from_bytes('\0branch=test-branch\0relative_start_directory=/experiment{}set_no_verify_ssl=true'.encode('utf-8'))
>>> url = 'https://github.com/nicc777/verba-cratis-test-infrastructure.git{}'.format(encoded_str)
```