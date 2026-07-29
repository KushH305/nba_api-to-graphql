from nba_api.stats.endpoints import commonplayerinfo

lebron_data = commonplayerinfo.CommonPlayerInfo(2544)
print(lebron_data.json())