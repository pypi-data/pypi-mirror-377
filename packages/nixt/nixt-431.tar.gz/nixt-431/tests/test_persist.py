# This file is placed in the Public Domain.


"engine"


import unittest


from nixt.persist import Cache


class TestPersist(unittest.TestCase):

    def testcache(self):
        cache = Cache()
        self.assertEqual(type(cache), Cache)
