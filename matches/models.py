from django.db import models

from django.db import models

class Match(models.Model):
    match_id = models.CharField(max_length=20, unique=True)
    team_a = models.CharField(max_length=50)
    team_b = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    team_a_squad = models.JSONField(default=list)
    team_b_squad = models.JSONField(default=list)
    live_data = models.JSONField(default=list)
    scorecard_data = models.JSONField(default=list)

    def __str__(self):
        return f"Match {self.match_id}: {self.team_a} vs {self.team_b}"


