import db.constants as dbconst
from log.logger import logger

class ResourceUserPGModel():
    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_resource_user_maps(self, resource_type="desktop"):
        conditions = {
            "resource_type": resource_type
            }

        total_count = self.pg.get_count(dbconst.TB_RESOURCE_USER, conditions)
        if total_count <= 0:
            return None

        offset = 0
        resource_users = None
        while offset < total_count:
            resource_user_set = self.pg.base_get(dbconst.TB_RESOURCE_USER, 
                                                 conditions, 
                                                 offset=offset, 
                                                 limit=dbconst.DEFAULT_LIMIT)
            if resource_user_set is None or len(resource_user_set) == 0:
                return resource_users

            offset = offset + len(resource_user_set)

            if resource_users is None:
                resource_users = resource_user_set
            else:
                resource_users = resource_users + resource_user_set

        return resource_users

