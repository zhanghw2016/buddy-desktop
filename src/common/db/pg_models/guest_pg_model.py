import db.constants as dbconst

class GuestPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_guest(self, desktop_id):
        conds = {"desktop_id": desktop_id}
        result = self.pg.base_get(dbconst.TB_GUEST,
                             conds)
        if not result or len(result) == 0:
            return None
        return result[0]

    

    def get_spice_connect_status(self, desktop_id):
        conds = {"desktop_id": desktop_id}
        result = self.pg.base_get(dbconst.TB_GUEST,
                             conds)
        if not result or len(result) == 0:
            return 0
        return result[0]["connect_status"]
