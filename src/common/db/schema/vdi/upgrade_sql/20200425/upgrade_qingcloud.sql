ALTER TABLE zone_connection ADD COLUMN keypair varchar(50) DEFAULT '' NOT NULL;

ALTER TABLE zone_resource_limit ADD COLUMN gpu_class_key varchar(255) DEFAULT '' NOT NULL;
ALTER TABLE zone_resource_limit ADD COLUMN max_gpu_count integer DEFAULT 2 NOT NULL;
CREATE TABLE gpu_class_type
(
    gpu_class_key varchar(255) PRIMARY KEY NOT NULL,
    gpu_class integer DEFAULT 0 NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL
);
/*init gpu class*/
INSERT INTO gpu_class_type(gpu_class_key,gpu_class) VALUES ('NVIDIA Tesla P100',0);
INSERT INTO gpu_class_type(gpu_class_key,gpu_class) VALUES ('AMD FirePro S7150',1);

/*add login_logo_custom_background_color in system_custom_config*/
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('default_system_custom','ThemeConfiguration','login_logo_custom_background_color','#006b47',1);
INSERT INTO system_custom_config (system_custom_id,module_type,item_key,item_value,enable_module) VALUES ('redefine_system_custom','ThemeConfiguration','login_logo_custom_background_color','#006b47',1);
