
from typing import Optional, List, Tuple

# from post.domain.post import Post
from domain.post.interface.Ipost import InterfacePost
import domain.post.domain.post as Post

class RepositoryPost():

    def __init__(self, interface:InterfacePost):
        self.__interface = interface

    def retrieve_post(self, post_id:int) -> Post:
        print("2. Dominio - post id repo: ", post_id)
        return self.__interface.get_post(post_id=post_id)

    def execute(self, start_after:Optional[int], end_before: Optional[int]) -> Tuple[List[Post.Post], int]:
        results = self.__interface.search_post(start_after=start_after, end_before=end_before)
        count = self.__interface.count_post()

        return results, count
