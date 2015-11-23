"""Testing the testing tools"""

import os
import random
import unittest

import hypothesis.strategies as st
from hypothesis import given

from . import test

_test_base = os.path.dirname(
    os.path.abspath(__file__)
)

yml_st = st.recursive(
    st.floats(-1, 1) | st.booleans() |
    st.text() | st.none() | st.binary(),
    lambda children: st.lists(children) | st.dictionaries(
        st.text(),
        children
    )
)


class TestTest(unittest.TestCase):
    def test_read_yml(self):
        """Test if reading yml files works without errors."""
        path = os.path.join(
            _test_base,
            "merge.yml"
        )
        yml = test.read_yml(path)
        assert yml['mirrors']['fakerepo01'] is not None

    def test_delete(self):
        """Test if merges can delete fields"""
        path = os.path.join(
            _test_base,
            "delete_merge.yml"
        )
        yml = test.read_yml(path)
        assert 'fakerepo01' not in yml['mirrors']

    @given(yml_st, yml_st)
    def test_merge(self, a, b):
        res  = test.merge(a, b)
        for _ in range(10):
            path, data_b = self.rand_path(b)
            data_res     = self.get_path(path, res)
            assert data_res == data_b
            if isinstance(a, dict) and isinstance(b, dict):
                path, data_a = self.rand_path(a)
                try:
                    data_res     = self.get_path(path, res)
                    if data_a != data_res:
                        data_b = self.get_path(path, b)
                        assert data_res == data_b
                except TypeError:
                    pass

    def get_path(self, path, data):
        for i in path:
            data = data[i]
        if isinstance(data, dict):
            return None
        return data

    def rand_path(self, data):
        path = []
        while True:
            if isinstance(data, dict):
                keys = list(data.keys())
                if keys:
                    k = random.choice(data.keys())
                    path.append(k)
                    data = data[k]
                else:
                    return path, None
            else:
                break
        return path, data
