from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.text import slugify


class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.points} pkt"


class Match(models.Model):
    group = models.CharField(max_length=2)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    date = models.DateTimeField()
    place = models.CharField(max_length=100)
    actual_home_team_score = models.IntegerField(null=True, blank=True, default=0)
    actual_away_team_score = models.IntegerField(null=True, blank=True, default=0)
    final_score = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"


class Bet(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Wrong'),
        (2, 'Good'),
        (3, 'Exact'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_team_score = models.IntegerField()
    away_team_score = models.IntegerField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.match}: {self.home_team_score}-{self.away_team_score}, Status: {self.get_status_display()}"


class Underdog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username}'s underdog team: {self.team}"


class TopScorer(models.Model):
    player_name = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.player_name} ({self.country})"


class UserPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    predicted_score_team1 = models.IntegerField()
    predicted_score_team2 = models.IntegerField()
    points = models.IntegerField(default=0)  # New field for storing points

    def __str__(self):
        return f"{self.user.username}'s prediction for {self.match}"


class LeaderboardEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)

    @classmethod
    def update_leaderboard(cls):
        leaderboard = (
            UserPrediction.objects.values('user')
            .annotate(total_points=Sum('points'))
            .order_by('-total_points')
        )
        for entry in leaderboard:
            user = User.objects.get(id=entry['user'])
            points = entry['total_points']
            leaderboard_entry, created = cls.objects.get_or_create(user=user)
            leaderboard_entry.total_points = points
            leaderboard_entry.save()


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class UnderdogSelection(models.Model):
    team = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team} selected by {self.user}"


class TopScorerSelection(models.Model):
    player = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    confirmed = models.BooleanField(default=False)
    is_top_scorer = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.player} ({self.country})"


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TournamentWinnerSelection(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)  # Add this line

    def __str__(self):
        return f"{self.team} selected by {self.user}"


class ActualResults(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='actualresults')
    home_team_score = models.IntegerField(null=True, blank=True)
    away_team_score = models.IntegerField(null=True, blank=True)
    final_score = models.BooleanField(default=False)

    def __str__(self):
        return f"Actual Results for {self.match}"


class TournamentResults(models.Model):
    winner_team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    top_scorer = models.ForeignKey('TopScorerSelection', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "Tournament Results"
