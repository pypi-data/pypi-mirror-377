import modelcif
import modelcif.dumper
import modelcif.reader
import os
import unittest


class Tests(unittest.TestCase):
    def test_basic(self):
        """Basic install test"""
        system = modelcif.System(title='test system')

        entity_a = modelcif.Entity('AAA', description='Subunit A')
        entity_b = modelcif.Entity('AAAAAA', description='Subunit B')
        system.entities.extend((entity_a, entity_b))

        # Test output in mmCIF format
        with open('output.cif', 'w') as fh:
            modelcif.dumper.write(fh, [system])

        # Make sure we can read back the file
        with open('output.cif') as fh:
            sys2, = modelcif.reader.read(fh)
        self.assertEqual(sys2.title, 'test system')

        os.unlink('output.cif')


if __name__ == '__main__':
    unittest.main()
