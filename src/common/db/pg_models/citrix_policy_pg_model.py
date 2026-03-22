
import db.constants as dbconst
from utils.id_tool import(
    UUID_TYPE_DESKTOP_USER,
    UUID_TYPE_DESKTOP_USER_GROUP
)
from log.logger import logger
class CitrixPolicyPGModel():
    ''' VDI model for complicated requests '''

    def __init__(self, pg, pgm):
        self.pg = pg
        self.pgm = pgm

    def get_citrix_policies(self, citrix_policy_ids=None, citrix_policy_names=None, columns=None, zone_id=None):

        conditions = {}        
        if citrix_policy_ids:
            conditions["pol_id"] = citrix_policy_ids        
        if citrix_policy_names:
            conditions["policy_name"] = citrix_policy_names        
        if zone_id:
            conditions["zone"] = zone_id               
        citrix_policy_set = self.pg.base_get(dbconst.TB_CITRIX_POLICY, conditions, columns=columns,sort_key="pol_priority")
        if citrix_policy_set is None or len(citrix_policy_set) == 0:
            return None
        citrix_policies = {}
        for citrix_policy in citrix_policy_set:
            citrix_policy_id = citrix_policy["policy_name"]            
            citrix_policies[citrix_policy_id] = citrix_policy            
        return citrix_policies

    def get_citrix_policy(self, citrix_policy_id, zone_id=None):

        conditions = {"pol_id": citrix_policy_id}     
        if zone_id:
            conditions["zone"] = zone_id           
        citrix_policy_set = self.pg.base_get(dbconst.TB_CITRIX_POLICY, conditions)
        if not citrix_policy_set:
            return None
        return citrix_policy_set[0]

    def get_citrix_policy_name(self, citrix_policy_ids=None, zone_id=None):

        conditions = {}
        if citrix_policy_ids:
            conditions["pol_id"] = citrix_policy_ids   
        if zone_id:
            conditions["zone"] = zone_id                
        citrix_policy_set = self.pg.base_get(dbconst.TB_CITRIX_POLICY, conditions)
        if citrix_policy_set is None or len(citrix_policy_set) == 0:
            return None
        citrix_policy_names = {}
        for citrix_policy in citrix_policy_set:
            citrix_policy_name = citrix_policy["policy_name"]
            citrix_policy_id = citrix_policy["pol_id"]
            citrix_policy_names[citrix_policy_id] = citrix_policy_name           
        return citrix_policy_names
    
    def get_citrix_policy_items(self, citrix_policy_id=None, citrix_policy_name=None, citrix_policy_item_name=None, zone_id=None,columns=None):

        conditions = {}
        if citrix_policy_name:
            conditions["policy_name"] = citrix_policy_name        
        if zone_id:
            conditions["zone"] = zone_id              
        if citrix_policy_item_name:
            conditions["pol_item_name"] = citrix_policy_item_name                         
        if citrix_policy_id:
            conditions["pol_id"] = citrix_policy_id                              
        citrix_policy_item_set = self.pg.base_get(dbconst.TB_CITRIX_POLICY_ITEM,conditions,columns=columns,sort_key="pol_item_id" )
        if citrix_policy_item_set is None or len(citrix_policy_item_set) == 0:
            return None
        citrix_policy_items = {}
        for citrix_policy_item in citrix_policy_item_set:
            citrix_policy_item_name = citrix_policy_item["pol_item_name"]            
            citrix_policy_items[citrix_policy_item_name] = citrix_policy_item                        
        return citrix_policy_items   

    def get_citrix_policy_item(self, citrix_policy_item_name, citrix_policy_id,zone_id=None):

        conditions = {}
        if zone_id:
            conditions["zone"] = zone_id      
        if citrix_policy_item_name:
            conditions["pol_item_name"] = citrix_policy_item_name             
        if citrix_policy_id:
            conditions["pol_id"] = citrix_policy_id                  
        citrix_policy_set = self.pg.base_get(dbconst.TB_CITRIX_POLICY_ITEM, conditions,sort_key="pol_item_id" )
        if not citrix_policy_set:
            return None
        return citrix_policy_set[0]    

    def get_citrix_policy_items_info(self, citrix_policy_id,zone_id):
        sql = "select a.*,b.pol_item_datatype,b.pol_item_name_ch,b.pol_item_path_ch,b.pol_item_tip,b.pol_item_unit,b.pol_item_value default_value,b.pol_item_value_ch default_value_ch"\
          " from citrix_policy_item a,citrix_policy_item_config b  " \
          "where a.pol_id ='%s' and a.pol_item_name=b.pol_item_name and a.zone='%s' order by a.pol_item_id" % (citrix_policy_id,zone_id)
        item_set = self.pg.execute_sql(sql)
        if not item_set:
            return None
        return item_set

    def get_citrix_policy_filters(self, citrix_policy_id=None, citrix_policy_name=None, citrix_policy_filter_name=None, zone_id=None):

        conditions = {}
        if citrix_policy_name:
            conditions["policy_name"] = citrix_policy_name        
        if zone_id:
            conditions["zone"] = zone_id               
        if citrix_policy_filter_name:
            conditions["pol_filter_name"] = citrix_policy_filter_name                         
        if citrix_policy_id:
            conditions["pol_id"] = citrix_policy_id                             
        citrix_policy_filter_set = self.pg.base_get(dbconst.TB_CITRIX_POLICY_FILTER, conditions,sort_key="pol_filter_id" )
        if citrix_policy_filter_set is None or len(citrix_policy_filter_set) == 0:
            return None
        citrix_policy_filters = {}
        for citrix_policy_filter in citrix_policy_filter_set:
            citrix_policy_filter_name = citrix_policy_filter["pol_filter_name"]            
            citrix_policy_filters[citrix_policy_filter_name] = citrix_policy_filter            
        return citrix_policy_filters   

