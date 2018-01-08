-- Database setup script

create database vegamite;
create user 'vegamite'@'localhost' IDENTIFIED BY 'vegamite';
grant ALL PRIVILEGES ON * . * TO 'vegamite'@'localhost';


-- Tables
create table vegamite.markets (
	market_id smallint not null auto_increment primary_key,
	ccxt_market_id varchar(50) not null,
	exchange_code varchar(50) not null,
	symbol varchar(20) not null,
	currency_1 smallint,
	currency_2 smallint,
	last_updated datetime
);

