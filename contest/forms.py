from django import forms
from django.contrib.auth.models import User
from .models import Article, Bet, UnderdogSelection, TopScorerSelection, TopScorer, TournamentWinnerSelection, Team, \
    ActualResults, Match


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'slug', 'content']


class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['match', 'home_team_score', 'away_team_score']
        widgets = {
            'match': forms.HiddenInput()
        }


class UnderdogForm(forms.ModelForm):
    TEAM_CHOICES = [
        ('Polska', 'Polska'),
        ('Czechy', 'Czechy'),
        ('Serbia', 'Serbia'),
        ('Szkocja', 'Szkocja'),
        ('Austria', 'Austria'),
        ('Turcja', 'Turcja'),
        ('Szwajcaria', 'Szwajcaria'),
        ('Węgry', 'Węgry'),
        ('Albania', 'Albania'),
        ('Słowenia', 'Słowenia'),
        ('Słowacja', 'Słowacja'),
        ('Rumunia', 'Rumunia'),
        ('Ukraina', 'Ukraina'),
        ('Gruzja', 'Gruzja'),
    ]
    team = forms.ChoiceField(choices=TEAM_CHOICES)
    confirmed = forms.BooleanField(required=True)

    class Meta:
        model = UnderdogSelection
        fields = ['team', 'confirmed']


class TopScorerForm(forms.ModelForm):
    player = forms.ModelChoiceField(
        queryset=TopScorer.objects.all().order_by('country', 'player_name'),
        label="Select Top Scorer",
        widget=forms.Select
    )
    confirmed = forms.BooleanField(required=True)

    class Meta:
        model = TopScorerSelection
        fields = ['player', 'confirmed']


class TournamentWinnerForm(forms.ModelForm):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by('name'),
        label="Select Tournament Winner",
        widget=forms.Select
    )
    confirmed = forms.BooleanField(required=True)  # Add this line

    class Meta:
        model = TournamentWinnerSelection
        fields = ['team', 'confirmed']


class ActualResultsForm(forms.ModelForm):
    winner_team = forms.ModelChoiceField(queryset=Team.objects.all().order_by('name'), required=False)
    top_scorer = forms.ModelChoiceField(queryset=TopScorer.objects.all().order_by('player_name'), required=False)

    class Meta:
        model = ActualResults
        fields = ['winner_team', 'top_scorer']


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['home_team', 'away_team', 'date', 'place']


class MatchScoreForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['actual_home_team_score', 'actual_away_team_score', 'final_score']
