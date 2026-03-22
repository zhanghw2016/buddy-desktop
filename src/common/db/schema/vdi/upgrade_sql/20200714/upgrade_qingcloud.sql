drop table desktop_share;
CREATE TABLE resource_user
(
   resource_id varchar(50) NOT NULL,
   resource_type varchar(50) DEFAULT 'desktop' NOT NULL,
   user_id varchar(255) NOT NULL,
   user_name text,
   is_sync integer DEFAULT 0 NOT NULL,
   PRIMARY KEY(resource_id, user_id)
);
