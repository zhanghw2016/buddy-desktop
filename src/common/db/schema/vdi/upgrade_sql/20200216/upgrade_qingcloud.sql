CREATE TABLE instance_class_disk_type
(
    instance_class_key varchar(50) DEFAULT '' NOT NULL,
    instance_class integer DEFAULT 0 NOT NULL,
    disk_type integer DEFAULT 0 NOT NULL,
    zone_deploy varchar(50) DEFAULT 'standard' NOT NULL,
    current_zone_deploy integer DEFAULT 0 NOT NULL,-- 1 for is current_zone_deploy, 0 for is not current_zone_deploy.
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(instance_class_key, zone_deploy)
);

/*init instance class*/
/*性能型主机*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy,current_zone_deploy) VALUES ('high_performance',0,0,'standard',1);
/*超高性能主机*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy,current_zone_deploy) VALUES ('high_performance_plus',1,3,'standard',1);
/*SANC型主机 全闪存*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy,current_zone_deploy) VALUES ('san_container_all_flash',6,5,'standard',1);
/*SANC型主机 混插*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy,current_zone_deploy) VALUES ('san_container_mixed_flash',7,6,'standard',1);

/*性能型主机*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy,current_zone_deploy) VALUES ('high_performance',0,5,'express',0);
/*超高性能主机*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy,current_zone_deploy) VALUES ('high_performance_plus',1,3,'express',0);
/*SANC型主机 全闪存*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy,current_zone_deploy) VALUES ('san_container_all_flash',6,5,'express',0);
/*SANC型主机 混插*/
INSERT INTO instance_class_disk_type(instance_class_key,instance_class,disk_type,zone_deploy,current_zone_deploy) VALUES ('san_container_mixed_flash',7,6,'express',0);

