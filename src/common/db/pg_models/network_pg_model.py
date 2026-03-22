import db.constants as dbconst

class NetworkPGModel():

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm
    
    def get_network(self, router_id, ip_network):

        conditions = dict(
                          ip_network = ip_network,
                          router_id = router_id
                          )
        network_set = self.pg.base_get(dbconst.TB_DESKTOP_NETWORK, conditions)
        if network_set is None or len(network_set) == 0:
            return None

        return network_set

    def get_networks(self, network_ids=None, network_type=None, router_id=None, ip_network=None):
        
        conditions = {}
        if network_ids:
            conditions = {"network_id": network_ids}
        if network_type is not None:
            conditions["network_type"] = network_type
        if router_id:
            conditions["router_id"] = router_id
        if ip_network:
            conditions["ip_network"] = ip_network
        
        network_set = self.pg.base_get(dbconst.TB_DESKTOP_NETWORK, conditions)
        if network_set is None or len(network_set) == 0:
            return None

        networks = {}
        for network in network_set:
            network_id = network["network_id"]
            networks[network_id] = network
        
        return networks

    def get_desktop_networks(self, network_ids=None, network_type=None, zone_id=None):
        
        conditions = {}
        if network_ids:
            conditions = {"network_id": network_ids}
        if network_type is not None:
            conditions["network_type"] = network_type
        
        if zone_id:
            conditions["zone"] = zone_id
        
        network_set = self.pg.base_get(dbconst.TB_DESKTOP_NETWORK, conditions)
        if network_set is None or len(network_set) == 0:
            return None

        networks = {}
        for network in network_set:
            network_id = network["network_id"]
            networks[network_id] = network
        
        return networks