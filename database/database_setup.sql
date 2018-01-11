-- TODO: Delete this file

-- Database setup script

create database vegamite;
create user 'vegamite'@'localhost' IDENTIFIED BY 'vegamite';
grant ALL PRIVILEGES ON * . * TO 'vegamite'@'localhost';


-- Tables
create table vegamite.markets (
	market_id smallint not null auto_increment,
	ccxt_market_id varchar(50) not null,
	exchange_code varchar(50) not null,
	symbol varchar(20) not null,
	currency_1 smallint,
	currency_2 smallint,
	last_updated datetime,
	primary key market_id
);


create table vegamite.tracking_type (
	tracking_type_id smallint not null auto_increment,
	tracking_descripion varchar(200) not null,
	primary key tracking_type_id
);


create table vegamite.market_tracking (
	market_tracking_id smallint not null auto_increment, 
	exchange, 
MARKET, 
TRACKING_TYPE_ID
);