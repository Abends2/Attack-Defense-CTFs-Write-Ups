import os

team_count = int(os.getenv('SERVICE_02_TEAM_COUNT', 12))

bind = list([":%d" % (p+12001) for p in range(team_count)])
