/*update enable_module where item_key is passwordExpirePeriod in system_custom_config*/
update system_custom_config set enable_module=0 where item_key='passwordExpirePeriod';
update system_custom_config set item_value=0 where item_key='passwordExpirePeriod';
