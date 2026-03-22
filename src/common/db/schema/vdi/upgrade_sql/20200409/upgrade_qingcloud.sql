ALTER TABLE policy_group_resource ADD COLUMN is_lock integer DEFAULT 0 NOT NULL;

INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-2', 'RemoveResourceFromPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('desktop-group-3', 'RemoveResourceFromPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-2', 'RemoveResourceFromPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'AddResourceToPolicyGroup');
INSERT INTO zone_user_scope_action (action_id, action_api) VALUES ('delivery-group-3', 'RemoveResourceFromPolicyGroup');


