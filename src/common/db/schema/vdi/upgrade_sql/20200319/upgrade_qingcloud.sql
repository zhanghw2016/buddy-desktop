update system_custom_config set item_value='Copyright © 2020 青云QingCloud' where item_key='copyright';
ALTER TABLE software_info ADD COLUMN transition_status varchar(50) DEFAULT '' NOT NULL;

INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'CreateDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'ApplyDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'CreateDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'ApplyDesktopSnapshots');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-0', 'CreateDesktopSnapshots');
