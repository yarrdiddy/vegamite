import pytest

from mocks import MockInfluxDB

@pytest.fixture()
def mock_write_points(monkeypatch):
    monkeypatch.setattr('influxdb.DataFrameClient.write_points', MockInfluxDB.write_points)

@pytest.fixture()
def mock_last_trade(monkeypatch):
    monkeypatch.setattr('influxdb.DataFrameClient.query', MockInfluxDB.query_last_trade)

@pytest.fixture()
def mock_last_trend(monkeypatch):
    monkeypatch.setattr('influxdb.DataFrameClient.query', MockInfluxDB.query_last_trend)