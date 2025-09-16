# This file is placed in the Public Domain.


"commands"


import unittest


from nixt.command import Commands


class TestCommands(unittest.TestCase):

    def test_construct(self):
        cmds = Commands()
        self.assertEqual(type(cmds), Commands)
