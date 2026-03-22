/*rebuild gpu_class_type*/
DROP TABLE gpu_class_type;
CREATE TABLE gpu_class_type
(
    gpu_class_key varchar(255) NOT NULL,
    gpu_class integer DEFAULT 0 NOT NULL,
    zone_id varchar(50) DEFAULT '' NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    PRIMARY KEY(gpu_class_key, zone_id)
);
