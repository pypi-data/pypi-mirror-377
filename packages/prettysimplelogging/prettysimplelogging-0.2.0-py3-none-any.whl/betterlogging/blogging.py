from rich import print

class Message:
    """
    Message class to create CLI logs of different types.
    """
    def __init__(self, _text, _type='INFO'):
        # TODO: custom type
        self.TYPES = ['INFO', 'WARN', 'ERR', 'SUCC']
        self.type = _type
        self.text = _text

    def __rich__(self):
        return str(self)

    def __str__(self):
        return f'[{self._color}][bold][{self.type}][/bold] {self.text}[/]'

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t):
        if t not in self.TYPES:
            raise ValueError("Message type must be", self.TYPES)
        self._type = t
        
        if self._type == 'INFO':
            self._color = 'cyan'
        elif self._type == 'WARN':
            self._color = 'yellow'
        elif self._type == 'ERR':
            self._color = 'red'
        elif self._type == 'SUCC':
            self._color = 'green'

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, t):
        self._text = t

    def print(self):
        print(self)


if __name__ == "__main__":
    print('Testing BetterLogging Messages')
    print(Message('this is an info message'))
    print(Message('this is an error message', 'ERR'))
    print(Message('this is an warning message', 'WARN'))
    Message('testing print func').print()

