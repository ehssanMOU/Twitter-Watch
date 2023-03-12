
from Person import Person




class TwitterAccount(Person):

    def __init__(self, name, conversation):

        super().__init__(name)

        self.audience = []

        self.score = 0

        self.conversation = {self.name: conversation}

    def get_score(self):

        return self.score

    def set_score(self, score):

        self.score = score

    def get_audiences(self):

        return self.audience

    def set_audience(self, audience):

        self.audience.append(audience)

    def get_conversation(self):

        return self.conversation[self.name]












