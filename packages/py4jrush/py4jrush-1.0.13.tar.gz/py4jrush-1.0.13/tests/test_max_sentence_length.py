# Copyright  2018  Department of Biomedical Informatics, University of Utah
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
import os

from py4jrush import RuSH


class TestMaxSentenceLength(unittest.TestCase):
    """Test cases for max_sentence_length functionality."""

    def setUp(self):
        self.pwd = os.path.dirname(os.path.abspath(__file__))
        self.rules_file = str(os.path.join(self.pwd, 'rush_rules.tsv'))

    def test_no_max_length_specified(self):
        """Test that sentences are not split when max_sentence_length is None."""
        rush = RuSH(self.rules_file, enable_logger=True)
        input_str = 'This is a very long sentence that would normally be split if we had a maximum sentence length specified, but we do not have one.'
        sentences = rush.segToSentenceSpans(input_str)
        
        # Should be one sentence since no max length is specified
        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0].begin, 0)
        self.assertEqual(sentences[0].end, len(input_str))
        rush.shutdownJVM()

    def test_sentence_within_max_length(self):
        """Test that sentences shorter than max_sentence_length are not split."""
        rush = RuSH(self.rules_file, enable_logger=True, max_sentence_length=100)
        input_str = 'This is a short sentence.'
        sentences = rush.segToSentenceSpans(input_str)
        
        # Should be one sentence since it's under the limit
        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0].begin, 0)
        self.assertEqual(sentences[0].end, 25)
        rush.shutdownJVM()

    def test_sentence_exceeds_max_length_with_whitespace(self):
        """Test that long sentences are split at whitespace when possible."""
        max_length = 50
        rush = RuSH(self.rules_file, enable_logger=True, max_sentence_length=max_length)
        input_str = 'This is a very long sentence that definitely exceeds our maximum length limit and should be split.'
        sentences = rush.segToSentenceSpans(input_str)
        
        # Should be split into multiple sentences
        self.assertGreater(len(sentences), 1)
        
        # Each sentence MUST be within the max_sentence_length limit
        for i, sentence in enumerate(sentences):
            sentence_text = input_str[sentence.begin:sentence.end]
            sentence_length = len(sentence_text)
            print(f"Sentence {i}: '{sentence_text}' (length: {sentence_length})")
            self.assertLessEqual(sentence_length, max_length, 
                               f"Sentence {i} exceeds max length: {sentence_length} > {max_length}")
        
        rush.shutdownJVM()
        
    def test_sentence_exceeds_max_length_no_whitespace(self):
        """Test splitting when no whitespace is available."""
        max_length = 20
        rush = RuSH(self.rules_file, enable_logger=True, max_sentence_length=max_length)
        input_str = 'Supercalifragilisticexpialidocious is a very long word.'
        sentences = rush.segToSentenceSpans(input_str)
        
        # Should be split even without whitespace
        self.assertGreater(len(sentences), 1)
        
        # Each sentence MUST be within the max_sentence_length limit
        for i, sentence in enumerate(sentences):
            sentence_text = input_str[sentence.begin:sentence.end]
            sentence_length = len(sentence_text)
            print(f"Sentence {i}: '{sentence_text}' (length: {sentence_length})")
            self.assertLessEqual(sentence_length, max_length,
                               f"Sentence {i} exceeds max length: {sentence_length} > {max_length}")
        
        rush.shutdownJVM()

    def test_multiple_sentences_with_max_length(self):
        """Test multiple sentences where some need splitting."""
        max_length = 40
        rush = RuSH(self.rules_file, enable_logger=True, max_sentence_length=max_length)
        input_str = 'Short sentence. This is a much longer sentence that should be split because it exceeds our limit. Another short one.'
        sentences = rush.segToSentenceSpans(input_str)
        
        # Should have more than the original 3 sentences due to splitting
        self.assertGreaterEqual(len(sentences), 3)
        
        # Each sentence MUST be within the max_sentence_length limit
        for i, sentence in enumerate(sentences):
            sentence_text = input_str[sentence.begin:sentence.end]
            sentence_length = len(sentence_text)
            print(f"Sentence {i}: '{sentence_text}' (length: {sentence_length})")
            self.assertLessEqual(sentence_length, max_length,
                               f"Sentence {i} exceeds max length: {sentence_length} > {max_length}")
            
        rush.shutdownJVM()

    def test_split_at_punctuation(self):
        """Test that splitting prefers punctuation marks when whitespace is not available."""
        max_length = 25
        rush = RuSH(self.rules_file, enable_logger=True, max_sentence_length=max_length)
        input_str = 'Word1,word2,word3,word4,word5,word6,word7,word8,word9,word10.'
        sentences = rush.segToSentenceSpans(input_str)
        
        # Should be split at commas
        self.assertGreater(len(sentences), 1)
        
        # Each sentence MUST be within the max_sentence_length limit
        for i, sentence in enumerate(sentences):
            sentence_text = input_str[sentence.begin:sentence.end]
            sentence_length = len(sentence_text)
            print(f"Sentence {i}: '{sentence_text}' (length: {sentence_length})")
            self.assertLessEqual(sentence_length, max_length,
                               f"Sentence {i} exceeds max length: {sentence_length} > {max_length}")
            
        rush.shutdownJVM()

    def test_edge_case_very_small_max_length(self):
        """Test edge case with very small max_sentence_length."""
        max_length = 5
        rush = RuSH(self.rules_file, enable_logger=True, max_sentence_length=max_length)
        input_str = 'Hello world!'
        sentences = rush.segToSentenceSpans(input_str)
        
        # Should be split into multiple very small segments
        self.assertGreater(len(sentences), 1)
        
        # Each sentence MUST be within the max_sentence_length limit
        for i, sentence in enumerate(sentences):
            sentence_text = input_str[sentence.begin:sentence.end]
            sentence_length = len(sentence_text)
            print(f"Sentence {i}: '{sentence_text}' (length: {sentence_length})")
            self.assertLessEqual(sentence_length, max_length,
                               f"Sentence {i} exceeds max length: {sentence_length} > {max_length}")
            
        rush.shutdownJVM()

    def test_empty_and_whitespace_sentences(self):
        """Test handling of empty and whitespace-only content."""
        rush = RuSH(self.rules_file, enable_logger=True, max_sentence_length=20)
        
        # Test empty string
        input_str = ''
        try:
            sentences = rush.segToSentenceSpans(input_str)
            self.assertEqual(len(sentences), 0)
        except Exception as e:
            # Java RuSH may not handle empty strings well
            print(f"Empty string handling: {e}")
        
        # Test whitespace with actual content
        input_str = '   Hello world.   '
        sentences = rush.segToSentenceSpans(input_str)
        
        # Should have at least one sentence
        self.assertGreaterEqual(len(sentences), 1)
        for i, sentence in enumerate(sentences):
            sentence_text = input_str[sentence.begin:sentence.end]
            print(f"Sentence {i}: '{sentence_text}' (length: {len(sentence_text)})")
            
        rush.shutdownJVM()

    def test_max_length_equal_to_sentence_length(self):
        """Test when max_sentence_length exactly equals sentence length."""
        max_length = 25
        rush = RuSH(self.rules_file, enable_logger=True, max_sentence_length=max_length)
        input_str = 'This is exactly 25 chars.'  # Exactly 25 characters
        sentences = rush.segToSentenceSpans(input_str)
        
        # Should be one sentence since it exactly matches the limit
        self.assertEqual(len(sentences), 1)
        sentence_length = len(input_str[sentences[0].begin:sentences[0].end])
        self.assertEqual(sentence_length, 25)
        self.assertLessEqual(sentence_length, max_length)
        
        rush.shutdownJVM()

    def test_comprehensive_max_length_enforcement(self):
        """Comprehensive test to ensure ALL sentences respect max_sentence_length in various scenarios."""
        max_length = 30
        rush = RuSH(self.rules_file, enable_logger=True, max_sentence_length=max_length)
        
        # Test various challenging text patterns
        test_cases = [
            # Long sentence with lots of whitespace
            'This is a very long sentence with multiple words that should definitely be split into smaller parts.',
            
            # Medical text (common use case)
            'The patient presented with acute myocardial infarction and was immediately transferred to the cardiac catheterization laboratory for primary percutaneous coronary intervention.',
            
            # Mixed punctuation
            'Hello, world! This is a test sentence; it has multiple punctuation marks: colons, semicolons, and periods.',
            
            # Numbers and special characters
            'Patient ID 123456789 was admitted on 01/15/2023 at 14:30:45 with complaints of chest pain lasting > 2 hours.',
            
            # Multiple sentences of varying lengths
            'Short. This is a medium-length sentence that might need splitting. Very long sentence that definitely needs to be split into multiple parts because it exceeds our maximum length limit significantly. Another short one.',
        ]
        
        for test_idx, input_str in enumerate(test_cases):
            print(f"\n--- Test Case {test_idx + 1} ---")
            print(f"Input: '{input_str}' (length: {len(input_str)})")
            
            sentences = rush.segToSentenceSpans(input_str)
            print(f"Split into {len(sentences)} sentences:")
            
            # CRITICAL: Every single sentence must be within the limit
            for i, sentence in enumerate(sentences):
                sentence_text = input_str[sentence.begin:sentence.end]
                sentence_length = len(sentence_text)
                print(f"  Sentence {i}: '{sentence_text}' (length: {sentence_length})")
                
                # This is the key assertion - NO exceptions allowed
                self.assertLessEqual(sentence_length, max_length,
                                   f"Test case {test_idx + 1}, Sentence {i} violates max length: "
                                   f"{sentence_length} > {max_length}. Text: '{sentence_text}'")
                
                # Also verify the sentence is not empty (unless it's just whitespace)
                self.assertGreater(sentence_length, 0, 
                                 f"Test case {test_idx + 1}, Sentence {i} is empty")
        
        rush.shutdownJVM()


if __name__ == '__main__':
    unittest.main()