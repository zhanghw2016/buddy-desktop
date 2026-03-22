import db.constants as dbconst

class ComponentVersionPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_component_versions(self, component_ids=None):

        conditions = {}
        if component_ids:
            conditions["component_id"] = component_ids

        component_version_set = self.pg.base_get(dbconst.TB_COMPONENT_VERSION, conditions)
        if component_version_set is None or len(component_version_set) == 0:
            return None

        component_versions = {}
        for component_version in component_version_set:
            component_id = component_version["component_id"]
            component_versions[component_id] = component_version

        return component_versions



