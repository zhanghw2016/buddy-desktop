ALTER TABLE file_share_service ADD COLUMN limit_rate integer DEFAULT 1 NOT NULL;
ALTER TABLE file_share_service ADD COLUMN limit_conn integer DEFAULT 5 NOT NULL;
