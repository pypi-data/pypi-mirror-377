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

class TestRuSH(unittest.TestCase):

    def setUp(self):
        self.pwd = os.path.dirname(os.path.abspath(__file__))
        self.rush = RuSH(str(os.path.join(self.pwd, 'rush_rules.tsv')), enable_logger=True)

    def test1(self):
        input_str = 'Can Mr. K check it. Look\n good.\n'
        sentences = self.rush.segToSentenceSpans(input_str)
        assert (sentences[0].begin == 0 and sentences[0].end == 19)
        assert (sentences[1].begin == 20 and sentences[1].end == 31)

    def test2(self):
        input_str = 'S/p C6-7 ACDF. No urgent events overnight. Pain control ON. '
        sentences = self.rush.segToSentenceSpans(input_str)
        assert (sentences[0].begin == 0 and sentences[0].end == 14)
        assert (sentences[1].begin == 15 and sentences[1].end == 42)
        assert (sentences[2].begin == 43 and sentences[2].end == 59)

    def test3(self):
        input_str = ''' •  Coagulopathy (HCC)    



 •  Hepatic encephalopathy (HCC)    



 •  Hepatorenal syndrome (HCC)    

'''
        sentences = self.rush.segToSentenceSpans(input_str)
        print([s.begin, s.end] for s in sentences)
        assert (sentences[0].begin == 1 and sentences[0].end == 22)
        assert (sentences[1].begin == 31 and sentences[1].end == 62)
        assert (sentences[2].begin == 71 and sentences[2].end == 100)

    def test4(self):
        input_str = 'Delirium - '
        sentences = self.rush.segToSentenceSpans(input_str)
        self.printDetails(sentences, input_str)
        assert (sentences[0].begin == 0 and sentences[0].end == 10)
        pass

    def test5(self):
        input_str = "The patient complained about the TIA \n\n No memory issues. \"I \n\nOrdered the MRI scan.- "
        sentences = self.rush.segToSentenceSpans(input_str)
        self.printDetails(sentences, input_str)
        assert (sentences[0].begin == 0 and sentences[0].end == 36)
        assert (sentences[1].begin == 40 and sentences[1].end == 57)
        assert (sentences[2].begin == 58 and sentences[2].end == 85)
        pass

    def printDetails(self, sentences, input_str):
        for i in range(0, len(sentences)):
            sentence = sentences[i]
            print('assert (sentences[' + str(i) + '].begin == ' + str(sentence.begin) +
                  ' and sentences[' + str(i) + '].end == ' + str(sentence.end) + ')')
        for i in range(0, len(sentences)):
            sentence = sentences[i]
            print(input_str[sentence.begin:sentence.end])
        # self.printDetails(sentences, input_str)
        pass

    def test6(self):
        input_str = '''The Veterans Aging Cohort Study (VACS) is a large, longitudinal, observational study of a cohort of HIV infected and matched uninfected Veterans receiving care within the VA [2]. This cohort was designed to examine important health outcomes, including cardiovascular diseases like heart failure, among HIV infected and uninfected Veterans.'''
        sentences = self.rush.segToSentenceSpans(input_str)
        self.printDetails(sentences, input_str)

    def test7(self):
        input_str = '''The Veterans Aging Cohort Study (VACS) is a large, longitudinal, observational study of a cohort of HIV infected and matched uninfected Veterans receiving care within the VA [2]. This cohort was designed to examine important health outcomes, including cardiovascular diseases like heart failure, among HIV infected and uninfected Veterans.'''
        rules = []
        rules.append(r'\b(\a	0	stbegin')
        rules.append(r'\a\e	2	stend')
        rules.append(r'. +(This	0	stbegin')
        rules.append(r'](.	2	stend')
        rush = RuSH(rules, enable_logger=True)
        sentences = rush.segToSentenceSpans(input_str)
        self.printDetails(sentences, input_str)

    def test_doc2(self):
        input_str = '''  
9.  Advair b.i.d.
10.  Xopenex q.i.d. and p.r.n.
I will see her in a month to six weeks.  She is to follow up with Dr. X before that.
'''
        self.rush = RuSH(str(os.path.join(self.pwd, 'rush_rules.tsv')), min_sent_chars=2, enable_logger=True)
        sentences = self.rush.segToSentenceSpans(input_str)
        for sent in sentences:
            print('>' + input_str[sent.begin:sent.end] + '<\n')
        assert (len(sentences) == 4)
        sent = sentences[1]
        assert (input_str[sent.begin:sent.end] == '10.  Xopenex q.i.d. and p.r.n.')


    def test_doc11(self):
        input_str='  This is a sentence. This is another sentence.'
        sentences=self.rush.segToSentenceSpans(input_str)
        for sent in sentences:
            print('>' + input_str[sent.begin:sent.end] + '<\n')

if __name__ == '__main__':
    unittest.main()
