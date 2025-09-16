class Span:
    def __init__(self, begin=-1, end=-1, text='', rule_id=-1, score=1.0):
        self.begin = begin
        self.end = end
        self.width = end - begin
        self.text = text
        self.rule_id = rule_id
        self.score = score

    def __str__(self):
        return "Span: \n\tbegin:\t{0}\n\tend:\t{1}\n\twidth:\t{2}\n\ttext:\t{3}\n\trule_id:\t{4}\n\tscore:\t{5}".format(
            self.begin, self.end, self.width, self.text, self.rule_id, self.score
        )