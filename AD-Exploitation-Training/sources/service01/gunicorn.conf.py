import os

team_count = int(os.getenv('SERVICE_01_TEAM_COUNT', 12))

bind = list([":%d" % (p+11001) for p in range(team_count)])
