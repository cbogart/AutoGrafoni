#!/usr/bin/env python3
"""
Unit tests for grafoni_spell function

This module tests the grafoni_spell function which converts English text to Grafoni phonetic script.
"""

import unittest
import sys
import os

# Add the current directory to the path so we can import grafoni
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import grafoni


class TestGrafoniSpell(unittest.TestCase):
    """Test cases for the grafoni_spell function"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def test_basic_vowels(self):
        """Test basic vowel conversions"""
        self.assertEqual(grafoni.grafoni_spell("see"), ["s", "uv1", "uv1"])
        self.assertEqual(grafoni.grafoni_spell("sit"), ["s", "uv1", "t"])
        self.assertEqual(grafoni.grafoni_spell("bed"), ["b", "uv2", "d"])
        self.assertEqual(grafoni.grafoni_spell("cat"), ["k", "uv3", "t"])
        self.assertEqual(grafoni.grafoni_spell("book"), ["b", "mv1", "k"])
        self.assertEqual(grafoni.grafoni_spell("about"), ["mv2", "b", "mv3", "lv1", "t"])
        self.assertEqual(grafoni.grafoni_spell("down"), ["d", "mv3", "lv1", "n"])
        self.assertEqual(grafoni.grafoni_spell("father"), ["f", "mv3", "dh", "mv2", "r"])
        self.assertEqual(grafoni.grafoni_spell("boot"), ["b", "lv1", "t"])
        self.assertEqual(grafoni.grafoni_spell("boat"), ["b", "lv2", "lv1", "t"])
        self.assertEqual(grafoni.grafoni_spell("bought"), ["b", "lv3", "t"])
        self.assertEqual(grafoni.grafoni_spell("know--know"), ["n", "lv2", "lv1", "-", "-", " ", "n", "lv2", "lv1"])
        
    



if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 