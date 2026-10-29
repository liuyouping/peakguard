--  城市信息表
DROP TABLE IF EXISTS ams_city;
CREATE TABLE ams_city (
    id int PRIMARY KEY AUTO_INCREMENT,
    cityId varchar(50) not null,
    cityName varchar(50) not null,
    altitude int, 
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 测试数据
insert into ams_city(cityId, cityName, altitude) values('010', '北京', 100);
insert into ams_city(cityId, cityName, altitude) values('022', '天津', 50);
insert into ams_city(cityId, cityName, altitude) values('0891', '拉萨', 3500);


--  城市气温和氧气浓度表
DROP TABLE IF EXISTS ams_city_temp;
CREATE TABLE ams_city_temp (
    id int PRIMARY KEY AUTO_INCREMENT,
    cityId varchar(50) not null,
    measureDate datetime, -- 测量日期
    temp decimal(5,2),    -- 气温
    oxygen decimal(5,2),  -- 氧气浓度 
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


--  用户信息表
DROP TABLE IF EXISTS ams_user;
CREATE TABLE ams_user (
    id int PRIMARY KEY AUTO_INCREMENT,
    userId varchar(50) not null,
    ueerName varchar(50) not null,
    age int,
    gender varchar(10),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


--  用户体征数据表
DROP TABLE IF EXISTS ams_vital_data;
CREATE TABLE ams_vital_data (
    id int PRIMARY KEY AUTO_INCREMENT,
    userId varchar(50) not null,
    measureDate datetime,  -- 测量日期 
    SpO2 decimal(8,2),           -- 血氧饱和度，最近一次测量数值
    SBP decimal(8,2),            -- 收缩压，最近一次测量数值
    DBP decimal(8,2),            -- 舒张压，最近一次测量数值
    sleep_quality decimal(8,2),  -- 睡眠质量评分(0-10)，最近一次测量数值
    heart int,                   -- 日平均心率
    breath int,                  -- 日平均呼吸
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);


--  高反风险表
DROP TABLE IF EXISTS ams_user_risk;
CREATE TABLE ams_user_risk (
    id int PRIMARY KEY AUTO_INCREMENT,
    userId varchar(50) not null,
    reportDate datetime,  -- 测量日期 
    riskLevel int,    -- 高原反应风险等级(0-无风险,1-轻度,2-中度,3-重度)
	riskReport varchar(2000),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);




-- 	2.4 设备表（设备其他信息从产品表关联出来）
drop table if exists busi_device;
create table busi_device(
	id int auto_increment primary key comment '自动增长主键，唯一标识', 
	## merchantNo varchar(50) comment '商户编号',
	appNo varchar(50) comment '商户应用编号，唯一标识：格式：商户编号_***',
	productNo varchar(50) comment '产品编号：base_product表外键', 
	netNo	varchar(50)	comment '网点编号：对应health中的appNo',
	
	deviceNo varchar(50) not null comment '设备编号：全表唯一标识', 
	
	onStatus tinyint(2) default 0 comment '设备在线状态：1在线，0离线',
	onTime datetime comment '上线时间',
	offTime datetime comment '离线时间', 
	appVersion varchar(32) comment 'app版本',
	chipVersion varchar(32) comment '芯片版本', 
	
	status tinyint(2) default 1 comment '设备状态：1使用，0禁用',
	msg varchar(200) comment '备注', 
	createId varchar(50) comment '创建人员',
	createTime datetime comment '创建时间',
	updateId varchar(50) comment '更新人员',
	updateTime datetime comment '更新时间'
)ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '设备表' ROW_FORMAT = Dynamic;
create unique index UQ_deviceNo on busi_device (deviceNo);


-- 	2.5 设备主题表
-- 不再对具体的设备指定主题，限定到 productNo 层面
drop table if exists busi_device_topic;
create table busi_device_topic(
	id int auto_increment primary key comment '自动增长主键',  
	## merchantNo varchar(50) not null comment '商户编号',
	## appNo varchar(50) not null comment '商户应用编号',
	productNo varchar(50) not null comment '产品编号',
	deviceNo varchar(50) not null comment '设备编号',
	
	topicNo varchar(50) not null comment '主题编号',
	topicName varchar(300) not null comment '主题名称',
	topicDesc varchar(200) null comment '主题描述',
	payload varchar(1000) null comment '主题载荷（JSON内容）',
	
	status tinyint(2) not null default 1 comment '设备状态：1使用，0禁用',

	msg varchar(500) comment '备注',
	createId varchar(50) not null comment '创建人员',
	createTime datetime comment '创建时间',
	updateId varchar(50) null comment '更新人员',
	updateTime datetime null comment '更新时间'
)ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '设备主题表' ROW_FORMAT = Dynamic;


-- 	2.6 主题订阅记录表
drop table if exists busi_device_subscribe;
create table busi_device_subscribe(
	id int auto_increment primary key comment '自动增长主键',  
	## merchantNo varchar(50) not null comment '商户编号',
	## appNo varchar(50) not null comment '商户应用编号',
	## productNo varchar(50) not null comment '产品编号',
	deviceNo varchar(50) not null comment '设备编号',
	
	clientId varchar(50) null comment '客户端ID',
	topic varchar(200) not null comment '主题',
	subscribedType tinyint(2) not null default 1 comment '订阅类型：1订阅，0取消订阅',
	topicTimeStamp varchar(50) not null comment '时间戳',

	msg varchar(500) comment '备注',
	createTime datetime comment '创建时间'
)ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '主题订阅记录表' ROW_FORMAT = Dynamic;


-- 	2.7 指令记录表
drop table if exists busi_device_cmd;
create table busi_device_cmd(
	id int auto_increment primary key comment '自动增长主键',  
	## merchantNo varchar(50) not null comment '商户编号',
	## appNo varchar(50) not null comment '商户应用编号',
	## productNo varchar(50) not null comment '产品编号',
	deviceNo varchar(50) not null comment '设备编号',
	
	clientId varchar(50) null comment '客户端ID',
	topic varchar(200) not null comment '主题',
	cmdCode varchar(50) not null comment '指令代码',
	cmdContent varchar(1000) not null comment '指令内容',
	cmdOperator varchar(50) not null comment '指令操作人',
	reqId varchar(50) null comment '请求Id',
	reqTime datetime null comment '请求时间',
	reqResult varchar(50) null comment '请求结果',
	rspTime datetime null comment '响应时间',
	rspResult varchar(200) null comment '响应结果',

	createTime datetime comment '创建时间'
)ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '指令记录表' ROW_FORMAT = Dynamic; 
create index IDX_deviceNo on busi_device_cmd (deviceNo);
create index IDX_deviceNo_clientId on busi_device_cmd (deviceNo, clientId); 
create index IDX_deviceNo_topic on busi_device_cmd (deviceNo, topic);


-- 	2.8 设备报文表（TODO：后期考虑分库分表）
drop table if exists busi_device_report;
create table busi_device_report(
	id int auto_increment primary key comment '自动增长主键',  
	deviceNo varchar(50) not null comment '设备编号',
	
	-- 报文信息
	clientId varchar(50) null comment '客户端ID',
	topic varchar(200) not null comment '主题',
	reportText varchar(1000) not null comment '报文内容',	

	msg varchar(500) comment '备注',
	createTime datetime comment '创建时间'
)ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '设备报文表' ROW_FORMAT = Dynamic;

create index IDX_id on busi_device_report (id);
create index IDX_deviceNo on busi_device_report (deviceNo);
create index IDX_deviceNo_clientId_createTime on busi_device_report (deviceNo,clientId, createTime);
create index IDX_deviceNo_createTime on busi_device_report (deviceNo,createTime); 
create index IDX_createTime on busi_device_report (createTime);

-- 	2.9 设备报文数据表（报文记录解析成数据，目前适用于监控设备）
drop table if exists busi_device_data;
create table busi_device_data(
	id int auto_increment primary key comment '自动增长主键',   
	deviceNo varchar(50) not null comment '设备编号',
	
	-- 报文信息
	serviceId varchar(50) comment '服务编号',
	propertyCmd varchar(50) comment '属性指令',
	propertyValue varchar(50) comment '属性值',
	propertyResult decimal(8,2) null comment '属性解析值',
	propertyAction varchar(100) comment '属性文字说明',
	eventTime datetime null comment '报文时间',

	createTime datetime comment '创建时间'
)ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '设备报文数据表' ROW_FORMAT = Dynamic;

create index IDX_id on busi_device_data (id);
create index IDX_deviceNo on busi_device_data (deviceNo);
create index IDX_deviceNo_propertyCmd_createTime on busi_device_data (deviceNo, propertyCmd, createTime);
create index IDX_id_deviceNo_propertyCmd on busi_device_data (id, deviceNo, propertyCmd);
create index IDX_deviceNo_propertyCmd on busi_device_data (deviceNo, propertyCmd);
create index IDX_deviceNo_createTime on busi_device_data (deviceNo, createTime); 
create index IDX_eventTime on busi_device_data (eventTime);
create index IDX_propertyCmd on busi_device_data (propertyCmd);
create index IDX_propertyCmd_createTime on busi_device_data (propertyCmd, createTime); 
create index IDX_propertyCmd_eventTime on busi_device_data (propertyCmd, eventTime); 
