from ecase.post.ecase_post import UseCase
from domain.post.repository.rpost import RepositoryPost

# Infraestructuree
from infraestructure.http.router import router_infra
from infraestructure.adapters.post.dtb import PostDTB
from infraestructure.adapters.dtb.conn import ConnDTB

r = router_infra(repository=RepositoryPost(
    interface=UseCase(adapterDTB=PostDTB(ConnDTB())) # <- dependency injection
))

print("server: ", r)
