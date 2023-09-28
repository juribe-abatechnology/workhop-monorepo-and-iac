from abc import ABC, abstractmethod
from typing import Optional, List
from domain.post.domain.post import Post

class InterfacePost(ABC):

    @abstractmethod
    def get_post(self, post_id:int) -> Post:
        print("2.entremos al dominio get post")
        pass

    @abstractmethod
    def search_post(self, start_after:Optional[int] = None, end_before: Optional[int] = None) -> List[Post]:
        pass 

    @abstractmethod
    def count_post(self) -> int:
        pass