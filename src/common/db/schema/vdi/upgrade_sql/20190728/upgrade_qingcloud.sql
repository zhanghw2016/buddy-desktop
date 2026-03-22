CREATE TABLE policy_group
(
    policy_group_id varchar(50) PRIMARY KEY NOT NULL,
    policy_group_name text,
    policy_group_type varchar(50) NOT NULL,
    transition_status varchar(50) DEFAULT '' NOT NULL,
    status varchar(50) NOT NULL,
    description text DEFAULT '',

    is_apply integer DEFAULT 0 NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);
CREATE INDEX policy_group_group_type_index ON policy_group (group_type);

CREATE TABLE policy_group_resource
(
    policy_group_id varchar(50) NOT NULL,
    resource_id varchar(50) NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    is_apply integer DEFAULT 0 NOT NULL,
    PRIMARY KEY(policy_group_id, resource_id)
);
CREATE INDEX policy_group_resource_resource_id_index ON policy_group_resource (resource_id);

CREATE TABLE policy_group_policy
(
    policy_group_id varchar(50) NOT NULL,
    policy_id varchar(50) NOT NULL,
    status varchar(50) DEFAULT 'active' NOT NULL,
    is_base integer DEFAULT 0 NOT NULL,
    PRIMARY KEY(policy_group_id, policy_id)
);
CREATE INDEX policy_group_policy_status_index ON policy_group_policy (status);

CREATE TABLE security_policy
(
    security_policy_id varchar(50) PRIMARY KEY NOT NULL,
    security_policy_name text DEFAULT '' NOT NULL,
    security_policy_type varchar(50) DEFAULT 'sgrs' NOT NULL,
    description text,
    status varchar(50) NOT NULL,
    is_default integer DEFAULT 0 NOT NULL,
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    status_time timestamp DEFAULT current_timestamp NOT NULL,
    is_apply integer DEFAULT 0 NOT NULL,
    is_shared integer DEFAULT 0 NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);
CREATE INDEX security_policy_create_time_index ON security_policy (create_time);

CREATE TABLE security_rule
(
    security_rule_id varchar(50) PRIMARY KEY NOT NULL, -- security group rule id
    security_rule_name text DEFAULT '' NOT NULL,		-- security group rule name
    security_policy_id varchar(50) NOT NULL,		    		-- security group id
    security_policy_name text,
    protocol varchar(50) NOT NULL,                  -- "tcp/udp/icmp/gre/<protocol_number>"
    direction integer DEFAULT 0 NOT NULL,         	-- 0 for inbound; 1 for outbound
    val1 varchar(50) DEFAULT '' NOT NULL,         	-- if protocol is tcp/udp, this is starting port; for icmp, this is icmp type; 
                                                        -- (it could be security_group_ipset id)
    val2 varchar(50) DEFAULT '' NOT NULL,         	-- if protocol is tcp/udp, this is ending port; for icmp, this is icmp code
    val3 varchar(50) DEFAULT '' NOT NULL,         	-- if protocol is tcp/udp, this is source ip: <ip> for one ip address or <ip>/<cidr mask> for a range of addresses. 
                                                        -- (it could be security_group_ipset id)
    val4 varchar(50) DEFAULT '' NOT NULL, 
    priority integer NOT NULL,                  	-- rule priority, range is [0 - 100]
    action varchar(16) DEFAULT 'accept' NOT NULL,   -- 'accept' to accept packets if matched; 'drop' to drop packets if matched
    disabled integer DEFAULT 0 NOT NULL,             -- 0 for enabled, 1 for disabled.
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);
CREATE INDEX security_rule_security_policy_id_index ON security_rule (security_policy_id);

CREATE TABLE security_ipset
(
    security_ipset_id varchar(50) PRIMARY KEY NOT NULL,    -- security group ipset id
    security_ipset_name text DEFAULT '' NOT NULL,	        -- security group ipset name
    description text DEFAULT '' NOT NULL,										-- security group ipset description
    ipset_type integer DEFAULT 0 NOT NULL,        -- ipset type: 0 for hash:ip; 1 for bitmap:port 
    val text DEFAULT '' NOT NULL,	                -- value, if type is 0, this is comma separated ip or ip/cidr or fromip-toip
                                                        --        if type is 1, this is comma separated port or <start>-<end> port
    is_apply integer DEFAULT 1 NOT NULL,                  -- whether the ipset changes is applied to sg.
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    zone varchar(255) DEFAULT '' NOT NULL
);

