from domain.post.repository.rpost import RepositoryPost

def router_infra(repository: RepositoryPost):
    print("1. entramos a la infraestructure")
    res = repository.retrieve_post(123)
    return res
