import os.path
import unittest

from ..package import *

class TestException(Exception): pass

class Test(unittest.TestCase):

    NOT_A_MODULE_DIR_PATH  = 'not_a_module'
    NOT_A_MODULE_FILE_PATH = os.path.join(NOT_A_MODULE_DIR_PATH, 'dummy.txt')

    def test_is_module(self):

        self.assertTrue (is_module(os.path.split(__file__)[0]))
        self.assertTrue (is_module(__file__))
        self.assertFalse(is_module(os.path.join(__file__, Test.NOT_A_MODULE_DIR_PATH)))
        self.assertFalse(is_module(os.path.join(__file__, Test.NOT_A_MODULE_FILE_PATH)))

    def test_Enumerator(self):

        e:Enumerator[str] = Enumerator()
        self.assertNotIn(''   , e)
        self.assertNotIn('abc', e)
        e('abc')
        self.assertIn   ('abc', e)
        e('def')
        e('ghi')
        self.assertIn   ('def', e)
        self.assertIn   ('ghi', e)
        self.assertNotIn(''   , e)
        self.assertTrue (all(a == b for a,b in zip(('abc','def','ghi',), e)))

    def test_joincallables(self):

        a = [1]
        f = lambda: a.append(len(a) + 1)
        joincallables(f, f)()
        self.assertEqual(tuple(a), (1,2,3,))

    def test_joinfunctions(self):

        a = [1, 2, 3]
        r = joinfunctions(len, sum)(a)
        self.assertEqual(next(r), 3)
        self.assertEqual(next(r), 6)

    def test_raiser(self):

        r = raiser(TestException())
        try:
            r()
        except TestException: pass
        else: self.fail()

    def test_selfie(self):

        a = [1,2,3]
        self.assertIs(a, selfie(a))

    def test_constant(self):

        self.assertEqual   ('abc', constant('abc')(123))
        self.assertNotEqual('abc', constant('def')('abc'))
