from datetime import date
import unittest
from src.mask import transform, mask

test_data = {'user_id': 'test_id', 'app_version': '1.2.3',
             'ip': 'test_ip', 'device_id': 'test_device_id'}

class TestMask(unittest.TestCase):
    def test_masking(self):
        transformed = transform(test_data)
        assert transformed['app_version'] == 123
        assert transformed['ip'] == 'd8fdcad8790002f1d283ff564a0fa3f77cfcd9ac07fdbfca0363d2699f2cef4e'
        assert transformed['device_id'] == 'a9d489e3ee9ca2ea7e8ca2657156cb53d8e6a97698c8b87ed414fabc9abb0ce7'
        assert transformed['create_date'] == date.today().strftime("%Y-%m-%d")
        
    def test_hash(self):
        assert mask('testing hash', salt='with salt') == mask('testing hash'+'with salt')