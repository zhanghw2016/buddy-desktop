ALTER TABLE desktop_image ADD is_default  integer DEFAULT 0 NOT NULL;

/* init image*/
INSERT INTO desktop_image(desktop_image_id,image_id,image_name,description,platform,os_version,os_family,image_type, session_type) VALUES ('default_win7','desktop_win7prox64cn','Windows7基础镜像', 'Windows7基础镜像(未安装桌面Tools)','windows','Windows7','windows','model','SingleSession');
INSERT INTO desktop_image (desktop_image_id,image_id,image_name,description,platform,os_version,os_family,image_type, session_type) VALUES ('default_win10','desktop_win10prox64cn','Windows10基础镜像', 'Windows10基础镜像(未安装桌面Tools)','windows','Windows10','windows','model','SingleSession');

