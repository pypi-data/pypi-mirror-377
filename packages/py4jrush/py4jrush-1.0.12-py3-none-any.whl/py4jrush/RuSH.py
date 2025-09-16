# ******************************************************************************
#  MIT License
#
#  Copyright (c) 2020 Jianlin Shi
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
#  files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
#  modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ******************************************************************************
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
import os
import os.path
import sys
from pathlib import Path
from typing import Union, List, Optional

from loguru import logger
from py4j.java_gateway import JavaGateway

from .Span import Span



class RuSH:
    """Rule-based sentence Segmenter using Hashing (RuSH).
    
    A Python wrapper for the Java-based RuSH sentence segmentation library.
    """

    def __init__(self, rules: Union[str, List] = '', min_sent_chars: int = 5,
                 enable_logger: bool = False, py4jar: Optional[str] = None,
                 rushjar: Optional[str] = None,
                 java_path: str = 'java', max_sentence_length: Optional[int] = None) -> None:
        """Initialize RuSH sentence segmenter.
        
        Args:
            rules: Segmentation rules as string or list of strings. If empty, uses default rules from conf/rush_rules.tsv
            min_sent_chars: Minimum sentence length in characters
            enable_logger: Whether to enable logging
            py4jar: Path to py4j JAR file (optional)
            rushjar: Path to RuSH JAR file (optional)
            java_path: Path to Java executable
            max_sentence_length: Maximum sentence length in characters (optional)
        
        Raises:
            FileNotFoundError: If required JAR files are not found
        """

        # Determine the path to the JARs inside the package
        package_dir = os.path.dirname(os.path.abspath(__file__))
        default_py4jar = os.path.join(package_dir, 'lib', 'py4j0.10.9.7.jar')
        default_rushjar = os.path.join(package_dir, 'lib', 'rush-2.0.0.0-jdk1.8-jar-with-dependencies.jar')
        py4jar = py4jar if py4jar is not None else default_py4jar
        rushjar = rushjar if rushjar is not None else default_rushjar
        if not Path(py4jar).exists():
            raise FileNotFoundError(f"py4j jar not found at {py4jar}")
        if not Path(rushjar).exists():
            raise FileNotFoundError(f"RuSH jar not found at {rushjar}")
        self.gateway = JavaGateway.launch_gateway(jarpath=py4jar,
                                                 classpath=rushjar,
                                                 java_path=java_path, die_on_exit=True, use_shell=False)
        
        # Load default rules if none provided
        if not rules or (isinstance(rules, list) and len(rules) == 0):
            default_rules_path = os.path.join(package_dir, 'conf', 'rush_rules.tsv')
            if Path(default_rules_path).exists():
                with open(default_rules_path, 'r', encoding='utf-8') as f:
                    rules = f.read()
            else:
                raise FileNotFoundError(f"Default rules file not found at {default_rules_path}")
        
        if isinstance(rules, List):
            rules = '\n'.join(rules)
        self.jrush = self.gateway.jvm.edu.utah.bmi.nlp.rush.core.RuSH(rules)
        if enable_logger:
            logger.remove()
            logger.add(sys.stdout, level="WARNING", format="{time} - {name} - {level} - {message}")
            self.gateway.jvm.py4j.GatewayServer.turnLoggingOn()
            self.logger = logger
        else:
            self.logger = None
        self.min_sent_chars = min_sent_chars
        self.max_sentence_length = max_sentence_length

    def segToSentenceSpans(self, text: str) -> List[Span]:
        """Segment text into sentence spans.
        
        Args:
            text: Input text to segment
            
        Returns:
            List of Span objects representing sentence boundaries
            
        Raises:
            ValueError: If text is not a string
        """
        if not isinstance(text, str):
            raise ValueError("Input text must be a string")
            
        output = [Span(s.getBegin(), s.getEnd()) for s in self.jrush.segToSentenceSpans(text)]

        # log important message for debugging use
        if self.logger is not None:
            modified_text = text.replace('\n', ' ')
            self.logger.debug(modified_text)
            
        if len(output) > 0:
            for i, span in enumerate(output):
                if i == 0:
                    span = RuSH.trim_gap(text, 0, span.begin)
                else:
                    previous = output[i-1]
                    span = RuSH.trim_gap(text, previous.end, span.begin)
                if span is not None:
                    output[i] = span
        
        # Apply max_sentence_length splitting if specified
        if self.max_sentence_length is not None and self.max_sentence_length > 0:
            output = self._split_long_sentences(text, output)
        
        return output

    def _split_long_sentences(self, text: str, spans: List[Span]) -> List[Span]:
        """Split sentences that exceed max_sentence_length.
        
        Args:
            text: Original text being processed
            spans: List of sentence spans to potentially split
            
        Returns:
            List of spans with long sentences split appropriately
        """
        if not spans:
            return spans
            
        result = []
        
        for span in spans:
            sentence_text = text[span.begin:span.end]
            sentence_length = len(sentence_text)
            
            if self.max_sentence_length is None or sentence_length <= self.max_sentence_length:
                result.append(span)
                continue
                
            # Need to split this sentence
            if self.logger is not None:
                self.logger.debug(f"Splitting long sentence of length {sentence_length}: '{sentence_text[:50]}...'")
            
            split_spans = self._split_sentence_at_length(text, span)
            result.extend(split_spans)
            
        return result
    
    def _split_sentence_at_length(self, text: str, span: Span) -> List[Span]:
        """Split a single sentence at appropriate points to respect max_sentence_length.
        
        Args:
            text: Original text being processed
            span: Sentence span to split
            
        Returns:
            List of split spans
        """
        sentence_text = text[span.begin:span.end]
        result = []
        current_start = span.begin
        
        while current_start < span.end:
            remaining_length = span.end - current_start
            
            if self.max_sentence_length is None or remaining_length <= self.max_sentence_length:
                # Remaining text fits within limit
                result.append(Span(current_start, span.end))
                break
                
            # Find best split point within max_sentence_length
            max_length = self.max_sentence_length if self.max_sentence_length is not None else span.end - current_start
            split_point = self._find_split_point(text, current_start, 
                                               min(current_start + max_length, span.end))
            
            if split_point <= current_start:
                # No good split point found, force split at max length
                max_length = self.max_sentence_length if self.max_sentence_length is not None else span.end - current_start
                split_point = min(current_start + max_length, span.end)
                
            result.append(Span(current_start, split_point))
            
            if self.logger is not None:
                split_text = text[current_start:split_point]
                self.logger.debug(f"Split sentence part: '{split_text}' (length: {len(split_text)})")
                
            current_start = split_point
            
        return result
    
    def _find_split_point(self, text: str, start: int, max_end: int) -> int:
        """Find the best point to split a sentence, preferring whitespace.
        
        Args:
            text: Original text
            start: Start position to search from
            max_end: Maximum end position (inclusive)
            
        Returns:
            Best split position
        """
        # Look for whitespace working backwards from max_end
        for i in range(max_end - 1, start, -1):
            if text[i].isspace():
                # Found whitespace, split after it
                return i + 1
                
        # Look for punctuation working backwards
        sentence_end_chars = {'.', '!', '?', ';', ','}
        for i in range(max_end - 1, start, -1):
            if text[i] in sentence_end_chars:
                # Found punctuation, split after it
                return i + 1
                
        # No good split point found
        return max_end

    def shutdownJVM(self) -> None:
        """Shutdown the Java Virtual Machine gateway."""
        self.gateway.shutdown()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures JVM is properly shutdown."""
        self.shutdownJVM()

    @staticmethod
    def trim_gap(text: str, previous_end: int, this_begin: int) -> Optional[Span]:
        """Trim gaps between sentences and create spans for non-whitespace content.
        
        Args:
            text: Full text being processed
            previous_end: End position of previous sentence
            this_begin: Begin position of current sentence
            
        Returns:
            Span object for the gap content, or None if no valid content found
        """
        begin = -1
        end = 0
        gap_chars = list(text[previous_end:this_begin])
        
        # Find first non-whitespace character (trim left)
        for i in range(0, this_begin - previous_end):
            this_char = gap_chars[i]
            if not this_char.isspace():
                begin = i
                break
                
        # Find last meaningful character (trim right)
        sentence_end_chars = {'.', '!', '?', ')', ']', '"'}
        for i in range(this_begin - previous_end - 1, begin, -1):
            this_char = gap_chars[i]
            if this_char.isalnum() or this_char in sentence_end_chars:
                end = i
                break
                
        if begin != -1 and end > begin:
            return Span(begin + previous_end, end + previous_end + 1)
        else:
            return None
