from gen_epix.commondb.domain.repository.system import BaseSystemRepository
from gen_epix.fastapp.repositories import SARepository


class SystemSARepository(SARepository, BaseSystemRepository):
    pass
