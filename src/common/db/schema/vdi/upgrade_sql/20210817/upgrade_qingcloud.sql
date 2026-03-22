CREATE TABLE citrix_policy
(
  pol_id character varying(50) NOT NULL,
  policy_name character varying(255) NOT NULL DEFAULT ''::character varying,
  description text DEFAULT ''::text,
  pol_priority integer NOT NULL,
  pol_state integer NOT NULL DEFAULT 0,
  create_time timestamp without time zone NOT NULL DEFAULT now(),
  update_time timestamp without time zone NOT NULL DEFAULT now(),
  zone character varying(255) NOT NULL DEFAULT ''::character varying,
  com_priority integer NOT NULL DEFAULT 0,
  user_priority integer NOT NULL DEFAULT 0,
  CONSTRAINT citrix_policy_pkey PRIMARY KEY (pol_id)
);
CREATE TABLE citrix_policy_filter
(
  pol_filter_id character varying(50) NOT NULL,
  pol_id character varying(50) NOT NULL,
  pol_filter_name character varying(255) NOT NULL DEFAULT ''::character varying,
  pol_filter_type character varying(20) NOT NULL DEFAULT ''::character varying,
  pol_filter_state integer NOT NULL DEFAULT 0,
  pol_filter_value text DEFAULT ''::text,
  pol_filter_mode character varying(20) NOT NULL DEFAULT ''::character varying,
  create_time timestamp without time zone NOT NULL DEFAULT now(),
  update_time timestamp without time zone NOT NULL DEFAULT now(),
  zone character varying(255) NOT NULL DEFAULT ''::character varying,
  CONSTRAINT citrix_policy_filter_pkey PRIMARY KEY (pol_filter_id)
);
CREATE TABLE citrix_policy_item
(
  pol_item_id character varying(50) NOT NULL,
  pol_item_name character varying(50) NOT NULL,
  pol_id character varying(50),
  pol_item_type character varying(20) NOT NULL DEFAULT ''::character varying,
  pol_item_state integer NOT NULL DEFAULT 0,
  pol_item_value text DEFAULT ''::text,
  create_time timestamp without time zone NOT NULL DEFAULT now(),
  update_time timestamp without time zone NOT NULL DEFAULT now(),
  zone character varying(255) NOT NULL DEFAULT ''::character varying,
  CONSTRAINT citrix_policy_item_pkey PRIMARY KEY (pol_item_id)
);
CREATE TABLE citrix_policy_item_config
(
  pol_item_name character varying(255) NOT NULL DEFAULT ''::character varying,
  pol_item_type character varying(20) NOT NULL DEFAULT ''::character varying,
  pol_item_state integer NOT NULL DEFAULT 0,
  pol_item_value text DEFAULT ''::text,
  description text DEFAULT ''::text,
  pol_item_path character varying(255) NOT NULL DEFAULT ''::character varying,
  col1 character varying(255) NOT NULL DEFAULT ''::character varying,
  col2 character varying(255) NOT NULL DEFAULT ''::character varying,
  col3 character varying(255) NOT NULL DEFAULT ''::character varying,
  create_time timestamp without time zone NOT NULL DEFAULT now(),
  update_time timestamp without time zone NOT NULL DEFAULT now(),
  pol_item_datatype text DEFAULT ''::text,
  pol_item_name_ch text DEFAULT ''::text,
  pol_item_tip text DEFAULT ''::text,
  pol_item_unit text DEFAULT ''::text,
  pol_item_value_ch text DEFAULT ''::text,
  pol_item_path_ch text DEFAULT ''::text,
  CONSTRAINT citrix_policy_item_config_pkey PRIMARY KEY (pol_item_name)
);