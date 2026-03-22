-- Table: citrixtool_job

-- DROP TABLE citrixtool_job;

CREATE TABLE citrixtool_job
(
  job_id character varying(20) NOT NULL,
  status character varying(20) NOT NULL,
  action character varying(64) NOT NULL,
  extra character varying(256),
  create_time timestamp without time zone NOT NULL,
  update_time timestamp without time zone NOT NULL,
  CONSTRAINT citrixjobkey PRIMARY KEY (job_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE citrixtool_job
  OWNER TO yunify;
