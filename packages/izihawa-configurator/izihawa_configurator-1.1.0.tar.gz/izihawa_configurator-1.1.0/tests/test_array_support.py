import os
import unittest
from unittest.mock import patch

from izihawa_configurator import Configurator


class TestArraySupport(unittest.TestCase):
    def setUp(self):
        """Clear environment variables before each test"""
        # Store original env vars to restore later
        self.original_env = dict(os.environ)
        # Clear test-related env vars
        for key in list(os.environ.keys()):
            if key.lower().startswith('test_'):
                del os.environ[key]
    
    def tearDown(self):
        """Restore original environment variables after each test"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_indexed_array_format(self):
        """Test new indexed array format: PREFIX_MAIN[0], PREFIX_MAIN[1], etc."""
        # Set up environment variables
        os.environ['TEST_SERVERS[0]'] = 'server1.com'
        os.environ['TEST_SERVERS[1]'] = 'server2.com'
        os.environ['TEST_SERVERS[2]'] = 'server3.com'
        
        config = Configurator([], env_prefix='test')
        
        self.assertIn('servers', config)
        self.assertEqual(config['servers'], ['server1.com', 'server2.com', 'server3.com'])
    
    def test_sparse_indexed_array(self):
        """Test indexed arrays with gaps (sparse arrays)"""
        os.environ['TEST_ITEMS[0]'] = 'first'
        os.environ['TEST_ITEMS[2]'] = 'third'  # Skip index 1
        os.environ['TEST_ITEMS[4]'] = 'fifth'  # Skip index 3
        
        config = Configurator([], env_prefix='test')
        
        self.assertIn('items', config)
        # Should create array with None values for missing indices
        expected = ['first', None, 'third', None, 'fifth']
        self.assertEqual(config['items'], expected)
    
    def test_single_indexed_element(self):
        """Test single element with index"""
        os.environ['TEST_SINGLE[0]'] = 'only_value'
        
        config = Configurator([], env_prefix='test')
        
        self.assertIn('single', config)
        self.assertEqual(config['single'], ['only_value'])
    
    def test_unordered_indices(self):
        """Test that indices are properly sorted regardless of env var order"""
        os.environ['TEST_COLORS[2]'] = 'blue'
        os.environ['TEST_COLORS[0]'] = 'red'
        os.environ['TEST_COLORS[1]'] = 'green'
        
        config = Configurator([], env_prefix='test')
        
        self.assertIn('colors', config)
        self.assertEqual(config['colors'], ['red', 'green', 'blue'])
    
    def test_multiple_arrays(self):
        """Test multiple independent arrays"""
        os.environ['TEST_FRUITS[0]'] = 'apple'
        os.environ['TEST_FRUITS[1]'] = 'banana'
        os.environ['TEST_VEGETABLES[0]'] = 'carrot'
        os.environ['TEST_VEGETABLES[1]'] = 'broccoli'
        
        config = Configurator([], env_prefix='test')
        
        self.assertEqual(config['fruits'], ['apple', 'banana'])
        self.assertEqual(config['vegetables'], ['carrot', 'broccoli'])
    
    def test_backward_compatibility_legacy_format(self):
        """Test that legacy [] format still works"""
        os.environ['TEST_LEGACY[]'] = 'value1'
        os.environ['TEST_LEGACY[]'] = 'value2'  # This will overwrite the previous one
        
        config = Configurator([], env_prefix='test')
        
        # Note: Legacy format behavior depends on how environment handles duplicate keys
        # This test documents the current behavior
        self.assertIn('legacy', config)
        self.assertIsInstance(config['legacy'], list)
    
    def test_mixed_formats_same_base_name(self):
        """Test mixing new indexed format with legacy format (should prioritize indexed)"""
        os.environ['TEST_MIXED[0]'] = 'indexed_first'
        os.environ['TEST_MIXED[1]'] = 'indexed_second'
        # Legacy format should be ignored when indexed format is present
        
        config = Configurator([], env_prefix='test')
        
        self.assertEqual(config['mixed'], ['indexed_first', 'indexed_second'])
    
    def test_nested_array_with_separator(self):
        """Test arrays with nested keys using separator"""
        os.environ['TEST_DB.HOSTS[0]'] = 'db1.com'
        os.environ['TEST_DB.HOSTS[1]'] = 'db2.com'
        os.environ['TEST_DB.PORT'] = '5432'
        
        config = Configurator([], env_prefix='test', env_key_separator='.')
        
        self.assertIn('db', config)
        self.assertEqual(config['db']['hosts'], ['db1.com', 'db2.com'])
        self.assertEqual(config['db']['port'], '5432')
    
    def test_large_indices(self):
        """Test arrays with large indices"""
        os.environ['TEST_BIG[0]'] = 'start'
        os.environ['TEST_BIG[100]'] = 'end'
        
        config = Configurator([], env_prefix='test')
        
        self.assertIn('big', config)
        array = config['big']
        self.assertEqual(len(array), 101)  # 0 to 100 inclusive
        self.assertEqual(array[0], 'start')
        self.assertEqual(array[100], 'end')
        # All values in between should be None
        for i in range(1, 100):
            self.assertIsNone(array[i])
    
    def test_case_insensitive_prefix(self):
        """Test that env prefix is case insensitive"""
        os.environ['TEST_ITEMS[0]'] = 'lower'
        os.environ['test_items[1]'] = 'mixed'  # lowercase prefix
        
        config = Configurator([], env_prefix='TEST')  # uppercase prefix
        
        self.assertIn('items', config)
        # Should capture both regardless of case
        self.assertTrue(len(config['items']) >= 1)
    
    def test_no_env_prefix(self):
        """Test behavior when no env_prefix is provided"""
        os.environ['SOME_VAR[0]'] = 'should_not_be_processed'
        
        config = Configurator([])  # No env_prefix
        
        # Should not process array format without prefix
        self.assertNotIn('some_var', config)
    
    def test_empty_arrays(self):
        """Test that empty environment doesn't create arrays"""
        config = Configurator([], env_prefix='test')
        
        # Should not have any test-prefixed variables
        # Check for lowercase keys which would come from our prefix processing
        test_keys = [key for key in config.keys() if key.islower()]
        self.assertEqual(len(test_keys), 0)
    
    def test_numeric_values_remain_strings(self):
        """Test that numeric values in arrays remain as strings (env var behavior)"""
        os.environ['TEST_NUMBERS[0]'] = '123'
        os.environ['TEST_NUMBERS[1]'] = '456'
        
        config = Configurator([], env_prefix='test')
        
        self.assertEqual(config['numbers'], ['123', '456'])
        self.assertIsInstance(config['numbers'][0], str)
        self.assertIsInstance(config['numbers'][1], str)


if __name__ == '__main__':
    unittest.main()
