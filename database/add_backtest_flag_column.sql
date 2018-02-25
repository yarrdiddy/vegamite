alter table market add column backtest_market varchar(1) after trade_market;

update market set backtest_market = 'F' where 1=1;
