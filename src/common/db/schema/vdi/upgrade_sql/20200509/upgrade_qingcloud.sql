/*add InstanceParameter  cpu_model in system_custom_config*/
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','InstanceParameter','cpu_model','Westmere,SandyBridge,IvyBridge,Haswell,Broadwell',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','InstanceParameter','cpu_model','Westmere,SandyBridge,IvyBridge,Haswell,Broadwell',1);

/*add cpu_model in desktop*/
ALTER TABLE desktop ADD COLUMN cpu_model varchar(255) DEFAULT '' NOT NULL;