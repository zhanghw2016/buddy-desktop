import db.constants as dbconst

class TerminalPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    def get_terminals(self, terminal_ids=None, terminal_group_id=None,terminal_serial_number=None, status=None,
                      login_user_name=None,terminal_ip=None,terminal_mac=None,terminal_version_number=None,login_hostname=None,zone_id=None):

        conditions = {}
        if terminal_ids:
            conditions["terminal_id"] = terminal_ids

        if terminal_group_id:
            conditions["terminal_group_id"] = terminal_group_id

        if terminal_serial_number:
            conditions["terminal_serial_number"] = terminal_serial_number

        if status:
            conditions["status"] = status

        if login_user_name:
            conditions["login_user_name"] = login_user_name
        
        if terminal_ip:
            conditions["terminal_ip"] = terminal_ip

        if terminal_mac:
            conditions["terminal_mac"] = terminal_mac

        if terminal_version_number:
            conditions["terminal_version_number"] = terminal_version_number

        if login_hostname:
            conditions["login_hostname"] = login_hostname

        if zone_id:
            conditions["zone_id"] = zone_id

        terminal_set = self.pg.base_get(dbconst.TB_TERMINAL_MANAGEMENT, conditions)
        if terminal_set is None or len(terminal_set) == 0:
            return None

        terminals = {}
        for terminal in terminal_set:
            terminal_id = terminal["terminal_id"]
            terminals[terminal_id] = terminal

        return terminals

    def get_terminal_id(self, terminal_ids=None, terminal_serial_number=None, status=None,
                      login_user_name=None,terminal_ip=None,terminal_mac=None,terminal_version_number=None,login_hostname=None,zone_id=None):

        conditions = {}
        if terminal_ids:
            conditions["terminal_id"] = terminal_ids

        if terminal_serial_number:
            conditions["terminal_serial_number"] = terminal_serial_number

        if status:
            conditions["status"] = status

        if login_user_name:
            conditions["login_user_name"] = login_user_name

        if terminal_ip:
            conditions["terminal_ip"] = terminal_ip

        if terminal_mac:
            conditions["terminal_mac"] = terminal_mac

        if terminal_version_number:
            conditions["terminal_version_number"] = terminal_version_number

        if login_hostname:
            conditions["login_hostname"] = login_hostname

        if zone_id:
            conditions["zone_id"] = zone_id

        terminal_set = self.pg.base_get(dbconst.TB_TERMINAL_MANAGEMENT, conditions)
        if terminal_set is None or len(terminal_set) == 0:
            return None

        terminal_id = None
        for terminal in terminal_set:
            terminal_id = terminal["terminal_id"]

        return terminal_id


