import db.constants as dbconst
from db.data_types import SearchType, RegExpType
from log.logger import logger
import context

class DesktopMaintainerPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_desktop_maintainer_name(self, is_upper=True):

        conditions = {}

        desktop_maintainer_set = self.pg.base_get(dbconst.TB_DESKTOP_MAINTAINER, conditions)
        if desktop_maintainer_set is None or len(desktop_maintainer_set) == 0:
            return None

        desktop_maintainer_names = []
        for desktop_maintainer in desktop_maintainer_set:
            desktop_maintainer_name = desktop_maintainer["desktop_maintainer_name"]
            if is_upper:
                desktop_maintainer_names.append(desktop_maintainer_name.upper())
            else:
                desktop_maintainer_names.append(desktop_maintainer_name)

        return desktop_maintainer_names

    def get_desktop_maintainers(self, zone_id=None,desktop_maintainer_ids=None,desktop_maintainer_name=None):

        conditions = {}
        if zone_id:
            conditions["zone_id"] = zone_id

        if desktop_maintainer_ids:
            conditions["desktop_maintainer_id"] = desktop_maintainer_ids

        if desktop_maintainer_name:
            conditions["desktop_maintainer_name"] = desktop_maintainer_name

        desktop_maintainer_set = self.pg.base_get(dbconst.TB_DESKTOP_MAINTAINER, conditions)
        if desktop_maintainer_set is None or len(desktop_maintainer_set) == 0:
            return None

        desktop_maintainers = {}
        for desktop_maintainer in desktop_maintainer_set:
            desktop_maintainer_id = desktop_maintainer["desktop_maintainer_id"]
            desktop_maintainers[desktop_maintainer_id] = desktop_maintainer

        return desktop_maintainers

    def get_desktop_maintainer_resources(self, desktop_maintainer_id=None, resource_ids=None):

        conditions = {}
        if desktop_maintainer_id:
            conditions["desktop_maintainer_id"] = desktop_maintainer_id

        if resource_ids:
            conditions["resource_id"] = resource_ids

        desktop_maintainer_resource_set = self.pg.base_get(dbconst.TB_DESKTOP_MAINTAINER_RESOURCE, conditions)
        if desktop_maintainer_resource_set is None or len(desktop_maintainer_resource_set) == 0:
            return None

        desktop_maintainer_resources = {}
        for desktop_maintainer_resource in desktop_maintainer_resource_set:
            resource_id = desktop_maintainer_resource["resource_id"]
            desktop_maintainer_resources[resource_id] = desktop_maintainer_resource

        return desktop_maintainer_resources

    def get_guest_shell_commands(self, guest_shell_command_ids=None,command=None):

        conditions = {}
        if guest_shell_command_ids:
            conditions["guest_shell_command_id"] = guest_shell_command_ids

        if command:
            conditions["command"] = command

        guest_shell_command_set = self.pg.base_get(dbconst.TB_GUEST_SHELL_COMMAND, conditions)
        if guest_shell_command_set is None or len(guest_shell_command_set) == 0:
            return None

        guest_shell_commands = {}
        for guest_shell_command in guest_shell_command_set:
            guest_shell_command_id = guest_shell_command["guest_shell_command_id"]
            guest_shell_commands[guest_shell_command_id] = guest_shell_command

        return guest_shell_commands

    def get_guest_shell_command_resources(self, guest_shell_command_id=None):

        conditions = {}
        if guest_shell_command_id:
            conditions["guest_shell_command_id"] = guest_shell_command_id

        guest_shell_command_resource_set = self.pg.base_get(dbconst.TB_GUEST_SHELL_COMMAND_RESOURCE, conditions)
        if guest_shell_command_resource_set is None or len(guest_shell_command_resource_set) == 0:
            return None

        guest_shell_command_resources = {}
        for guest_shell_command_resource in guest_shell_command_resource_set:
            resource_id = guest_shell_command_resource["resource_id"]
            guest_shell_command_resources[resource_id] = guest_shell_command_resource

        return guest_shell_command_resources

    def get_desktop_maintainer_resource_detail(self, desktop_maintainer_id, extras=[dbconst.TB_DESKTOP]):

        ctx = context.instance()

        desktop_maintainer = self.pg.get(dbconst.TB_DESKTOP_MAINTAINER, desktop_maintainer_id)
        if desktop_maintainer is None or len(desktop_maintainer) == 0:
            return None

        ret = self.get_desktop_maintainer_resources(desktop_maintainer_id=desktop_maintainer_id)
        if ret is not None:
            desktop_maintainer_resources = ret
            desktops = {}
            for desktop_resource_id, _ in desktop_maintainer_resources.items():

                conditions = dict(desktop_id=desktop_resource_id)
                if dbconst.TB_DESKTOP in extras:
                    desktop_set = self.pg.base_get(dbconst.TB_DESKTOP, conditions)

                    if desktop_set is not None and len(desktop_set) > 0:
                        for desktop in desktop_set:
                            desktop_id = desktop["desktop_id"]

                            desktop_disks = self.pg.base_get(dbconst.TB_DESKTOP_DISK, {"desktop_id": desktop_id})
                            if desktop_disks is not None and len(desktop_disks) > 0:
                                desktop["disks"] = desktop_disks
                            else:
                                desktop["disks"] = []

                            desktop_nics = self.pg.base_get(dbconst.TB_DESKTOP_NIC, {"resource_id": desktop_id})
                            if desktop_nics is not None and len(desktop_nics) > 0:
                                desktop["nics"] = desktop_nics
                            else:
                                desktop["nics"] = []

                            desktops[desktop_id] = desktop
                    else:
                        # delete resource_id in desktop_maintainer_resource db
                        delete_desktop_maintainer_resource_info = dict(
                            desktop_maintainer_id=desktop_maintainer_id,
                            resource_id=desktop_resource_id
                        )
                        ctx.pg.base_delete(dbconst.TB_DESKTOP_MAINTAINER_RESOURCE, delete_desktop_maintainer_resource_info)

            desktop_maintainer["desktops"] = desktops

        return desktop_maintainer





