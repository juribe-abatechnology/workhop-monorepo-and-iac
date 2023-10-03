from typing import Optional, List
from domain.post.interface.Ipost import InterfacePost
from domain.post.domain.post import Post
from domain.post.service.post import ServicePost

class UseCase(InterfacePost):

    def __init__(self, adapterDTB:ServicePost): # -> data base adapter
        self.__adapterDTB = adapterDTB

    def get_post(self, post_id:int) -> Post:
        print("3.entramos a la use case get_post: ", post_id)
        post = self.__adapterDTB.get(post_id)
        return post
    
    def search_post(self, start_after:Optional[int] = None, end_before: Optional[int] = None) -> List[Post]:
        row = self.__adapterDTB.get(123)
        return [Post(**row) for row in row]
    
    def count_post(self) -> int:
        return 1223
    


