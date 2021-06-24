
from tests.test_base import TestBase
from capanno_utils.helpers.dict_tools import no_clobber_update


test_dict_1 = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
test_dict_2 = {'key4': 'value4', 'key5': 'value5', 'key6': 'value6'}
test_dict_3 = {'key1': 'value1_test3', 'key7': 'value7', 'key4': 'value4_test3'}

class TestDictTools(TestBase):

    def test_no_clobber_update(self):
        updated_dict = no_clobber_update(test_dict_1, test_dict_2)
        self.assertEqual(updated_dict, test_dict_1.update(test_dict_2))
        return

    def test_no_clobber_update_fail(self):
        with self.assertRaises(ValueError):
            no_clobber_update(test_dict_1, test_dict_2)
        return