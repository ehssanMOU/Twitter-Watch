
class Person:

    def __init__(self, name):

        self.name = name

        self.account_positivity = 0

    def get_name(self):

        return self.name

    def get_account_positivity(self):

        return self.account_positivity

    def set_positivity_score(self, score):

        self.account_positivity = score


