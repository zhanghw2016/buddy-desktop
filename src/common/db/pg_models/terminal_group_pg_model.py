import db.constants as dbconst
import context

class TerminalGroupPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_terminal_groups(self, terminal_group_ids=None,terminal_group_name=None):

        conditions = {}
        if terminal_group_ids:
            conditions["terminal_group_id"] = terminal_group_ids

        if terminal_group_name:
            conditions["terminal_group_name"] = terminal_group_name

        terminal_group_set = self.pg.base_get(dbconst.TB_TERMINAL_GROUP, conditions)
        if terminal_group_set is None or len(terminal_group_set) == 0:
            return None

        terminal_groups = {}
        for terminal_group in terminal_group_set:
            terminal_group_id = terminal_group["terminal_group_id"]
            terminal_groups[terminal_group_id] = terminal_group

        return terminal_groups

    def get_terminal_group_name(self, terminal_group_ids=None, terminal_group_name=None,is_upper=True):

        conditions = {}
        if terminal_group_ids:
            conditions["terminal_group_id"] = terminal_group_ids

        if terminal_group_name:
            conditions["terminal_group_name"] = terminal_group_name

        terminal_group_set = self.pg.base_get(dbconst.TB_TERMINAL_GROUP, conditions)
        if terminal_group_set is None or len(terminal_group_set) == 0:
            return None

        terminal_group_names = []
        for terminal_group in terminal_group_set:
            terminal_group_name = terminal_group["terminal_group_name"]
            if is_upper:
                terminal_group_names.append(terminal_group_name.upper())
            else:
                terminal_group_names.append(terminal_group_name)

        return terminal_group_names

    def get_terminal_group_terminals(self, terminal_group_id=None, terminal_ids=None):

        conditions = {}
        if terminal_group_id is not None:
            conditions["terminal_group_id"] = terminal_group_id

        if terminal_ids:
            conditions["terminal_id"] = terminal_ids

        terminal_group_terminal_set = self.pg.base_get(dbconst.TB_TERMINAL_GROUP_TERMINAL, conditions)
        if terminal_group_terminal_set is None or len(terminal_group_terminal_set) == 0:
            return None

        terminal_group_terminals = {}
        for terminal_group_terminal in terminal_group_terminal_set:
            terminal_id = terminal_group_terminal["terminal_id"]
            terminal_group_terminals[terminal_id] = terminal_group_terminal

        return terminal_group_terminals

    def get_terminal_group_terminal_detail(self, terminal_group_id, extras=[dbconst.TB_TERMINAL_MANAGEMENT]):

        ctx = context.instance()

        terminal_group = self.pg.get(dbconst.TB_TERMINAL_GROUP, terminal_group_id)
        if terminal_group is None or len(terminal_group) == 0:
            return None

        ret = self.get_terminal_group_terminals(terminal_group_id=terminal_group_id)
        if ret is not None:
            terminal_group_terminals = ret
            terminals = {}
            for terminal_id, _ in terminal_group_terminals.items():

                conditions = dict(terminal_id=terminal_id)
                if dbconst.TB_TERMINAL_MANAGEMENT in extras:
                    terminal_set = self.pg.base_get(dbconst.TB_TERMINAL_MANAGEMENT, conditions)

                    if terminal_set is not None and len(terminal_set) > 0:
                        for terminal in terminal_set:
                            terminal_id = terminal["terminal_id"]
                            terminals[terminal_id] = terminal
                    else:
                        # delete terminal in terminal_group_terminal db
                        delete_terminal_group_terminal_info = dict(
                            terminal_group_id=terminal_group_id,
                            terminal_id=terminal_id
                        )
                        ctx.pg.base_delete(dbconst.TB_TERMINAL_GROUP_TERMINAL, delete_terminal_group_terminal_info)

            terminal_group["terminals"] = terminals

        return terminal_group




