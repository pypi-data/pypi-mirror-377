import unittest
from SetupVariableTracker import SetupVariableTracker


class Maintests(unittest.TestCase):
    def setUp(self):
        pass

    def test_hash(self):
        vtrack = SetupVariableTracker(locals())

        ##################################################
        # Define parameters for this script
        setup_variable_1 = "Hello"
        setup_variable_2 = "World!"
        foo = 1
        bar = None
        ##################################################
        locals_tmp = locals()
        self.assertEqual(vtrack.get_hash(locals_tmp, hash_size=1), "3a")
        self.assertEqual(vtrack.get_hash(locals_tmp, hash_size=4), "6df72de9")
        self.assertEqual(vtrack.get_hash(locals_tmp, hash_size=8), "55d468caacfd074d")
        self.assertEqual(vtrack.get_hash(locals_tmp, hash_size=16), "1067e37c87c26b5eb49c23df2a9c75c8")

    def test_content(self):
        vtrack = SetupVariableTracker(locals())

        ##################################################
        # Define parameters for this script
        setup_variable_1 = "Hello"
        setup_variable_2 = "World!"
        foo = 1
        bar = None
        ##################################################
        locals_tmp = locals()
        # Create a summary of all newly defined variables
        self.assertEqual(vtrack.save(locals_tmp, sort=True), """================  =======
Parameter         Value
================  =======
bar
foo               1
setup_variable_1  Hello
setup_variable_2  World!
================  =======""")
        self.assertEqual(vtrack.get_variables(locals_tmp, sort=True),
                         [['bar', None], ['foo', 1], ['setup_variable_1', 'Hello'], ['setup_variable_2', 'World!']])


if __name__ == '__main__':
    unittest.main()
