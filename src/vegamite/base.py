from abc import ABCMeta, abstractmethod

class BaseAnalytic(metaclass=ABCMeta):
    @property
    @abstractmethod
    def data(self):
        pass

    @data.setter
    @abstractmethod
    def data(self, data):
        pass

    @property
    @abstractmethod
    def result(self):
        pass

    @result.setter
    @abstractmethod
    def result(self, result):
        pass

    @abstractmethod
    def configure(self, *args, **kwargs):
        pass

    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def save(self):
        pass