from abc import ABC, abstractmethod

class ServicePost(ABC):

    @abstractmethod
    def save(post_id:int):
        pass 
    
    @abstractmethod
    def get(post_id:int):
        pass