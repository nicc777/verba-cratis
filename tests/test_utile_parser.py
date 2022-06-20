import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from acfop.utils.parser import *


class TestFunctionVariableSnippetExtract(unittest.TestCase):

    def test_string_with_no_variables(self):
        line = 'hello world!'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 0)

    def test_string_with_one_variable(self):
        line = 'XXX ${var:var1} XXX'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 1)
        self.assertEqual('var:var1', result[0])

    def test_string_with_two_variables(self):
        line = 'XXX ${var:var1} XXX ${func:print_s()} XXX'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 2)
        self.assertEqual('var:var1', result[0])
        self.assertEqual('func:print_s()', result[1])

    def test_string_with_two_variables_including_nested_variable(self):
        """
            NOTE: Even in the case of nested variables, still only the first level variables are extracted.
        """
        line = 'XXX ${var:var1} XXX ${func:print_s(message="${var:var1}")} XXX'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 2)
        self.assertEqual('var:var1', result[0])
        self.assertEqual('func:print_s(message="${var:var1}")', result[1])
        result2 = variable_snippet_extract(line=result[1])
        self.assertTrue(len(result2) == 1)
        self.assertEqual('var:var1', result2[0])



if __name__ == '__main__':
    unittest.main()
