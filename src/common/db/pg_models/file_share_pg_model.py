import db.constants as dbconst
from db.data_types import SearchType, RegExpType
from log.logger import logger

class FileSharePGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_file_share_group_name(self, is_upper=True):

        conditions = {}

        file_share_group_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP, conditions)
        if file_share_group_set is None or len(file_share_group_set) == 0:
            return None

        file_share_group_names = []
        for file_share_group in file_share_group_set:
            file_share_group_name = file_share_group["file_share_group_name"]
            if is_upper:
                file_share_group_names.append(file_share_group_name.upper())
            else:
                file_share_group_names.append(file_share_group_name)

        return file_share_group_names

    def get_file_share_group(self, file_share_group_id):

        conditions = {}
        conditions["file_share_group_id"] = file_share_group_id

        file_share_group_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP, conditions)
        if file_share_group_set is None or len(file_share_group_set) == 0:
            return None

        return file_share_group_set[0]

    def get_file_share_group_zone(self, file_share_group_ids=None, zone_id=None,user_scope=None):

        conditions = {}

        if file_share_group_ids:
            conditions["file_share_group_id"] = file_share_group_ids

        if zone_id:
            conditions["zone_id"] = zone_id

        if user_scope:
            conditions["user_scope"] = user_scope

        file_share_group_zone_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP_ZONE, conditions)
        if file_share_group_zone_set is None or len(file_share_group_zone_set) == 0:
            return None

        file_share_group_zones = {}
        for file_share_group_zone in file_share_group_zone_set:
            zone_id = file_share_group_zone["zone_id"]
            file_share_group_zones[zone_id] = file_share_group_zone

        return file_share_group_zones

    def get_file_share_group_user(self, file_share_group_ids=None, zone_id=None, user_ids=None):

        conditions = {}

        if file_share_group_ids:
            conditions["file_share_group_id"] = file_share_group_ids

        if zone_id:
            conditions["zone_id"] = zone_id

        if user_ids:
            conditions["user_id"] = user_ids

        file_share_group_user_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP_USER, conditions)
        if file_share_group_user_set is None or len(file_share_group_user_set) == 0:
            return None

        file_share_group_users = {}
        for file_share_group_user in file_share_group_user_set:
            user_id = file_share_group_user["user_id"]
            file_share_group_users[user_id] = file_share_group_user

        return file_share_group_users

    def get_file_share_groups(self, file_share_service_ids=None,file_share_group_ids=None,file_share_group_dn=None,file_share_group_names=None,scope=None,trashed_status=None,base_dn=None):

        conditions = {}

        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        if file_share_group_ids:
            conditions["file_share_group_id"] = file_share_group_ids

        if file_share_group_dn:
            conditions["file_share_group_dn"] = file_share_group_dn

        if file_share_group_names:
            conditions["file_share_group_name"] = file_share_group_names

        if scope:
            conditions["scope"] = scope

        if trashed_status:
            conditions["trashed_status"] = trashed_status

        if base_dn:
            conditions["base_dn"] = base_dn

        file_share_group_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP, conditions)
        if file_share_group_set is None or len(file_share_group_set) == 0:
            return None

        file_share_groups = {}
        for file_share_group in file_share_group_set:
            file_share_group_id = file_share_group["file_share_group_id"]
            file_share_groups[file_share_group_id] = file_share_group

        return file_share_groups

    def get_file_share_group_users(self, file_share_group_ids=None,user_ids=None):

        conditions = {}
        if file_share_group_ids:
            conditions["file_share_group_id"] = file_share_group_ids

        if user_ids:
            conditions["user_id"] = user_ids

        file_share_group_user_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP_USER, conditions)
        if file_share_group_user_set is None or len(file_share_group_user_set) == 0:
            return None

        file_share_group_users = {}
        for file_share_group_user in file_share_group_user_set:
            file_share_group_id = file_share_group_user["file_share_group_id"]
            file_share_group_users[file_share_group_id] = file_share_group_user

        return file_share_group_users

    def get_file_share_group_zones(self, file_share_group_ids=None,zone_ids=None,user_ids=None,user_scope=None):

        conditions = {}
        if file_share_group_ids:
            conditions["file_share_group_id"] = file_share_group_ids

        if zone_ids:
            conditions["zone_id"] = zone_ids

        if user_ids:
            conditions["user_id"] = user_ids

        if user_scope:
            conditions["user_scope"] = user_scope

        file_share_group_zone_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP_ZONE, conditions)
        if file_share_group_zone_set is None or len(file_share_group_zone_set) == 0:
            return None

        file_share_group_zones = {}
        for file_share_group_zone in file_share_group_zone_set:
            file_share_group_id = file_share_group_zone["file_share_group_id"]
            file_share_group_zones[file_share_group_id] = file_share_group_zone

        return file_share_group_zones

    def get_file_share_group_files(self, file_share_group_ids=None,file_share_group_file_name=None,file_share_group_file_ids=None,file_share_group_dn=None,file_share_group_file_dn=None,trashed_status=None):

        conditions = {}
        if file_share_group_ids:
            conditions["file_share_group_id"] = file_share_group_ids

        if file_share_group_file_name:
            conditions["file_share_group_file_name"] = file_share_group_file_name

        if file_share_group_file_ids:
            conditions["file_share_group_file_id"] = file_share_group_file_ids

        if file_share_group_dn:
            conditions["file_share_group_dn"] = file_share_group_dn

        if file_share_group_file_dn:
            conditions["file_share_group_file_dn"] = file_share_group_file_dn

        if trashed_status:
            conditions["trashed_status"] = trashed_status

        file_share_group_file_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP_FILE, conditions)
        if file_share_group_file_set is None or len(file_share_group_file_set) == 0:
            return None

        file_share_group_files = {}
        for file_share_group_file in file_share_group_file_set:
            file_share_group_file_id = file_share_group_file["file_share_group_file_id"]
            file_share_group_files[file_share_group_file_id] = file_share_group_file

        return file_share_group_files

    def get_file_share_group_dns(self, file_share_group_dn=None,file_share_group_names=None,trashed_status=None):

        conditions = {}
        if file_share_group_dn:
            conditions["file_share_group_dn"] = file_share_group_dn

        if file_share_group_names:
            conditions["file_share_group_name"] = file_share_group_names

        if trashed_status:
            conditions["trashed_status"] = trashed_status

        file_share_group_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP, conditions)
        if file_share_group_set is None or len(file_share_group_set) == 0:
            return None

        file_share_groups = {}
        for file_share_group in file_share_group_set:
            file_share_group_id = file_share_group["file_share_group_id"]
            file_share_groups[file_share_group_id] = file_share_group

        return file_share_groups

    def file_share_unicode_to_string(self,file_share, unicode_keys=[]):

        if not file_share:
            return file_share

        check_keys = ["file_share_group_dn", "file_share_group_name", "base_dn"]
        if unicode_keys:
            if isinstance(unicode_keys, list):
                check_keys.extend(unicode_keys)
            else:
                check_keys.append(unicode_keys)

        if isinstance(file_share, dict):
            for key, value in file_share.items():

                if key not in check_keys:
                    continue

                if isinstance(value, unicode):
                    file_share[key] = str(value).decode("string_escape").encode("utf-8")

        elif isinstance(file_share, list):
            new_values = []
            for value in file_share:
                if isinstance(value, unicode):
                    value = str(value).decode("string_escape").encode("utf-8")
                    new_values.append(value)
                    continue
                new_values.append(value)

            return new_values

        elif isinstance(file_share, unicode):
            return str(file_share).decode("string_escape").encode("utf-8")

        return file_share

    def search_file_share_group_users(self, user_id=None,file_share_group_dn=None,exclude_file_share_groups=[]):

        conditions = {}

        if user_id:
            conditions["user_id"] = user_id

        if file_share_group_dn:
            file_share_group_dn = self.pgm.file_share_unicode_to_string(file_share_group_dn)
            conditions["file_share_group_dn"] = SearchType(file_share_group_dn)

        file_share_group_user_set = self.pg.get_all(dbconst.TB_FILE_SHARE_GROUP_USER, conditions)
        if file_share_group_user_set is None or len(file_share_group_user_set) == 0:
            return None

        file_share_group_users = {}
        for file_share_group_user in file_share_group_user_set:
            self.pgm.file_share_unicode_to_string(file_share_group_user)
            file_share_group_dn = file_share_group_user["file_share_group_dn"]
            file_share_group_id = file_share_group_user["file_share_group_id"]

            if file_share_group_dn in exclude_file_share_groups:
                continue

            file_share_group_users[file_share_group_id] = file_share_group_user

        return file_share_group_users

    def search_file_share_groups(self, file_share_group_dn=None,trashed_status=None,exclude_file_share_groups=[]):

        conditions = {}

        if file_share_group_dn:
            file_share_group_dn = self.pgm.file_share_unicode_to_string(file_share_group_dn)
            conditions["file_share_group_dn"] = SearchType(file_share_group_dn)

        if trashed_status:
            conditions["trashed_status"] = trashed_status

        file_share_group_set = self.pg.get_all(dbconst.TB_FILE_SHARE_GROUP, conditions)
        if file_share_group_set is None or len(file_share_group_set) == 0:
            return None

        file_share_groups = {}
        for file_share_group in file_share_group_set:
            self.pgm.file_share_unicode_to_string(file_share_group)
            file_share_group_dn = file_share_group["file_share_group_dn"]
            file_share_group_id = file_share_group["file_share_group_id"]

            if file_share_group_dn in exclude_file_share_groups:
                continue

            file_share_groups[file_share_group_id] = file_share_group

        return file_share_groups

    def search_file_share_group_files(self, file_share_group_dn=None,trashed_status=None,exclude_file_share_groups=[]):

        conditions = {}

        if file_share_group_dn:
            file_share_group_dn = self.pgm.file_share_unicode_to_string(file_share_group_dn)
            conditions["file_share_group_dn"] = SearchType(file_share_group_dn)

        if trashed_status:
            conditions["trashed_status"] = trashed_status

        file_share_group_file_set = self.pg.get_all(dbconst.TB_FILE_SHARE_GROUP_FILE, conditions)
        if file_share_group_file_set is None or len(file_share_group_file_set) == 0:
            return None

        file_share_group_files = {}
        for file_share_group_file in file_share_group_file_set:
            self.pgm.file_share_unicode_to_string(file_share_group_file)
            file_share_group_dn = file_share_group_file["file_share_group_dn"]
            file_share_group_file_id = file_share_group_file["file_share_group_file_id"]

            if file_share_group_dn in exclude_file_share_groups:
                continue

            file_share_group_files[file_share_group_file_id] = file_share_group_file

        return file_share_group_files

    def get_file_share_group_resource(self, file_share_group_dn=None,trashed_status=None):

        file_share_group_resources = {}

        file_share_group_dn = self.pgm.file_share_unicode_to_string(file_share_group_dn)

        ret = self.search_file_share_groups(file_share_group_dn=file_share_group_dn,trashed_status=trashed_status,exclude_file_share_groups=[file_share_group_dn])
        if ret:
            file_share_group_resources.update(ret)

        ret = self.search_file_share_group_files(file_share_group_dn=file_share_group_dn,trashed_status=trashed_status,exclude_file_share_groups=[])
        if ret:
            file_share_group_resources.update(ret)

        return file_share_group_resources

    def get_file_share_group_file_id(self, file_share_group_file_name=None,file_share_group_dn=None,trashed_status=None):

        conditions = {}
        if file_share_group_file_name:
            conditions["file_share_group_file_name"] = file_share_group_file_name

        if file_share_group_dn:
            conditions["file_share_group_dn"] = file_share_group_dn

        if trashed_status:
            conditions["trashed_status"] = trashed_status

        file_share_group_file_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP_FILE, conditions)
        if file_share_group_file_set is None or len(file_share_group_file_set) == 0:
            return None

        file_share_group_file_id = None
        for file_share_group_file in file_share_group_file_set:
            file_share_group_file_id = file_share_group_file["file_share_group_file_id"]

        return file_share_group_file_id

    def get_file_share_group_id(self,file_share_group_dn=None,trashed_status=None):

        conditions = {}
        if file_share_group_dn:
            conditions["file_share_group_dn"] = file_share_group_dn

        if trashed_status:
            conditions["trashed_status"] = trashed_status

        file_share_group_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP, conditions)
        if file_share_group_set is None or len(file_share_group_set) == 0:
            return None

        file_share_group_id = None
        for file_share_group in file_share_group_set:
            file_share_group_id = file_share_group["file_share_group_id"]

        return file_share_group_id

    def get_file_share_services(self, file_share_service_ids=None,status=None,transition_status=None):

        conditions = {}
        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        if status:
            conditions["status"] = status

        if transition_status:
            conditions["transition_status"] = transition_status

        file_share_service_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE, conditions)
        if file_share_service_set is None or len(file_share_service_set) == 0:
            return None

        file_share_services = {}
        for file_share_service in file_share_service_set:
            file_share_service_id = file_share_service["file_share_service_id"]
            file_share_services[file_share_service_id] = file_share_service

        return file_share_services

    def get_file_share_service_private_ip(self, file_share_service_ids=None):

        conditions = {}
        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        file_share_service_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE, conditions)
        if file_share_service_set is None or len(file_share_service_set) == 0:
            return None

        private_ip = ''
        for file_share_service in file_share_service_set:
            private_ip = file_share_service["private_ip"]

        return private_ip

    def get_file_share_service_loaded_clone_instance_ip(self, file_share_service_ids=None):

        conditions = {}
        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        file_share_service_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE, conditions)
        if file_share_service_set is None or len(file_share_service_set) == 0:
            return None

        loaded_clone_instance_ip = ''
        for file_share_service in file_share_service_set:
            loaded_clone_instance_ip = file_share_service["loaded_clone_instance_ip"]

        return loaded_clone_instance_ip

    def get_file_share_service_eip_addr(self, file_share_service_ids=None):

        conditions = {}
        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        file_share_service_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE, conditions)
        if file_share_service_set is None or len(file_share_service_set) == 0:
            return None

        eip_addr = ''
        for file_share_service in file_share_service_set:
            eip_addr = file_share_service["eip_addr"]

        return eip_addr

    def get_file_share_service_max_download_file_size(self, file_share_service_ids=None):

        conditions = {}
        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        file_share_service_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE, conditions)
        if file_share_service_set is None or len(file_share_service_set) == 0:
            return None

        max_download_file_size = 100
        for file_share_service in file_share_service_set:
            max_download_file_size = file_share_service["max_download_file_size"]

        return max_download_file_size

    def get_file_share_service_vnass(self, vnas_ids=None):

        conditions = {}
        if vnas_ids:
            conditions["vnas_id"] = vnas_ids

        file_share_service_vnas_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE_VNAS, conditions)
        if file_share_service_vnas_set is None or len(file_share_service_vnas_set) == 0:
            return None

        file_share_service_vnass = {}
        for file_share_service_vnas in file_share_service_vnas_set:
            vnas_id = file_share_service_vnas["vnas_id"]
            file_share_service_vnass[vnas_id] = file_share_service_vnas

        return file_share_service_vnass

    def get_file_share_group_dn_by_file_share_group_id(self, file_share_group_ids=None):

        conditions = {}
        if file_share_group_ids:
            conditions["file_share_group_id"] = file_share_group_ids

        file_share_group_set = self.pg.base_get(dbconst.TB_FILE_SHARE_GROUP, conditions)
        if file_share_group_set is None or len(file_share_group_set) == 0:
            return None

        file_share_group_dn = None
        for file_share_group in file_share_group_set:
            file_share_group_dn = file_share_group["file_share_group_dn"]

        return file_share_group_dn

    def get_file_share_service_fuser(self, file_share_service_ids=None):

        conditions = {}
        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        file_share_service_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE, conditions)
        if file_share_service_set is None or len(file_share_service_set) == 0:
            return None

        fuser = ''
        for file_share_service in file_share_service_set:
            fuser = file_share_service["fuser"]

        return fuser

    def get_file_share_service_fpw(self, file_share_service_ids=None):

        conditions = {}
        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        file_share_service_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE, conditions)
        if file_share_service_set is None or len(file_share_service_set) == 0:
            return None

        fpw = ''
        for file_share_service in file_share_service_set:
            fpw = file_share_service["fpw"]

        return fpw

    def get_file_share_service_ftp_chinese_encoding_rules(self, file_share_service_ids=None):

        conditions = {}
        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        file_share_service_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE, conditions)
        if file_share_service_set is None or len(file_share_service_set) == 0:
            return None

        ftp_chinese_encoding_rules = 'utf-8'
        for file_share_service in file_share_service_set:
            ftp_chinese_encoding_rules = file_share_service["ftp_chinese_encoding_rules"]

        return ftp_chinese_encoding_rules

    def get_file_share_service_id(self, file_share_service_ids=None):

        conditions = {}
        if file_share_service_ids:
            conditions["file_share_service_id"] = file_share_service_ids

        file_share_service_set = self.pg.base_get(dbconst.TB_FILE_SHARE_SERVICE, conditions)
        if file_share_service_set is None or len(file_share_service_set) == 0:
            return None

        file_share_service_id = ''
        for file_share_service in file_share_service_set:
            file_share_service_id = file_share_service["file_share_service_id"]

        return file_share_service_id




