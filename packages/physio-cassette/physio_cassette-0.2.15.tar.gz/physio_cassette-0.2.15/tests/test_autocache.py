import numpy as np
import pytest

from physio_cassette.physio_cassette import autocache

class TestAutocache:
    def sample_signal(self, len_x:int=100):
        x = np.linspace(0,10,len_x)
        return x, np.sin(2*np.pi*x)
    
    def test_same_cache(self):
        cache_folder = '.'
        cache_filename = 'testfile'

        x_true, y_true = self.sample_signal()
        x_test, y_test = autocache(self.sample_signal,cache_folder=cache_folder,filename=cache_filename)(100)
        assert np.array_equal(x_true, x_test)
        assert np.array_equal(y_true, y_test)

        x_cached, y_cached = autocache(self.sample_signal,cache_folder=cache_folder,filename=cache_filename)(100)
        assert np.array_equal(x_cached, x_test)
        assert np.array_equal(y_cached, y_test)

    def test_different_cache(self):
        cache_folder = '.'
        cache_filename = 'testfile'

        x_true, y_true = self.sample_signal()
        x_test, y_test = autocache(self.sample_signal,cache_folder=cache_folder,filename=cache_filename)(10)
        assert not np.array_equal(x_true, x_test)
        assert not np.array_equal(y_true, y_test)

        x_cached, y_cached = autocache(self.sample_signal,cache_folder=cache_folder,filename=cache_filename)(100)
        assert not np.array_equal(x_cached, x_test)
        assert not np.array_equal(y_cached, y_test)

        