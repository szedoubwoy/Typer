import pprint
from collections import namedtuple

from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import UserPrediction, Match, Bet, User, Article, UnderdogSelection, TopScorerSelection, \
    TournamentWinnerSelection, Team, ActualResults, UserPoints, TournamentResults, TopScorer
from .forms import UserCreationForm, UserEditForm, ArticleForm, BetForm, UnderdogForm, TopScorerForm, \
    TournamentWinnerForm, MatchForm, MatchScoreForm
from django.contrib import messages
from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max


def results(request):
    all_matches = Match.objects.all().order_by('date')
    tournament_results = TournamentResults.objects.first()

    context = {
        'matches': all_matches,
        'tournament_results': tournament_results,
    }

    return render(request, 'results.html', context)


def home(request):
    matches = Match.objects.all()
    return render(request, 'home.html', {'matches': matches})


def user_predictions(request):
    users = User.objects.filter(is_superuser=False)
    user_data = []

    actual_results = {result.match_id: result for result in ActualResults.objects.all()}

    for user in users:
        bets = Bet.objects.filter(user=user).select_related('match')
        underdog = UnderdogSelection.objects.filter(user=user).first()
        top_scorer = TopScorerSelection.objects.filter(user=user).first()
        tournament_winner = TournamentWinnerSelection.objects.filter(user=user).first()

        user_data.append({
            'user': user,
            'bets': bets,
            'underdog': underdog,
            'top_scorer': top_scorer,
            'tournament_winner': tournament_winner,
        })

    context = {
        'user_data': user_data,
        'actual_results': actual_results,
    }
    return render(request, 'user_predictions.html', context)


LeaderboardEntry = namedtuple('LeaderboardEntry', ['rank', 'user', 'points'])


class LeaderboardEntry:
    def __init__(self, rank, user, points):
        self.rank = rank
        self.user = user
        self.points = points


def leaderboard(request):
    leaderboard_data = UserPoints.objects.select_related('user').filter(user__is_superuser=False).order_by('-points')

    # Calculate ranks
    ranked_leaderboard = []
    current_rank = 1
    previous_points = None
    for i, entry in enumerate(leaderboard_data, start=1):
        if entry.points != previous_points:
            current_rank = i  # Update current rank only if points differ
        ranked_leaderboard.append(LeaderboardEntry(
            rank=current_rank,
            user=entry.user,
            points=entry.points,
        ))
        previous_points = entry.points

    return render(request, 'leaderboard.html', {'leaderboard': ranked_leaderboard})


def redirect_authenticated_user(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')  # Zastąp 'profile' odpowiednią ścieżką
        return view_func(request, *args, **kwargs)

    return wrapped_view


@redirect_authenticated_user
def user_login(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')  # Zastąp 'profile' odpowiednią ścieżką
        else:
            error_message = 'Invalid username or password'
    return render(request, 'login.html', {'error': error_message})


@login_required
def betting(request):
    available_matches = Match.objects.exclude(
        bet__user=request.user
    ).exclude(final_score=True)

    my_bets = Bet.objects.filter(user=request.user)

    try:
        underdog = UnderdogSelection.objects.get(user=request.user)
    except UnderdogSelection.DoesNotExist:
        underdog = None

    try:
        top_scorer = TopScorerSelection.objects.get(user=request.user)
    except TopScorerSelection.DoesNotExist:
        top_scorer = None

    try:
        tournament_winner = TournamentWinnerSelection.objects.get(user=request.user)
    except TournamentWinnerSelection.DoesNotExist:
        tournament_winner = None

    if request.method == 'POST':
        if 'place_bet' in request.POST:
            match_id = request.POST['place_bet']
            home_team_score = request.POST.get(f'home_team_score_{match_id}')
            away_team_score = request.POST.get(f'away_team_score_{match_id}')
            if home_team_score is not None and away_team_score is not None:
                match = Match.objects.get(id=match_id)
                Bet.objects.create(
                    user=request.user,
                    match=match,
                    home_team_score=home_team_score,
                    away_team_score=away_team_score
                )
                messages.success(request, 'Bet placed successfully!')
            else:
                messages.error(request, 'Please provide valid scores.')
            return redirect('betting')

        if 'confirm_underdog' in request.POST:
            underdog_form = UnderdogForm(request.POST)
            if underdog_form.is_valid():
                underdog_selection = underdog_form.save(commit=False)
                underdog_selection.user = request.user
                underdog_selection.save()
                messages.success(request, 'Underdog selected successfully!')
                return redirect('betting')

        if 'confirm_top_scorer' in request.POST:
            top_scorer_form = TopScorerForm(request.POST)
            if top_scorer_form.is_valid():
                top_scorer_selection = top_scorer_form.save(commit=False)
                top_scorer_selection.user = request.user
                top_scorer_selection.save()
                messages.success(request, 'Top scorer selected successfully!')
                return redirect('betting')

        if 'confirm_winner' in request.POST:
            winner_form = TournamentWinnerForm(request.POST)
            if winner_form.is_valid():
                winner_selection = winner_form.save(commit=False)
                winner_selection.user = request.user
                winner_selection.save()
                messages.success(request, 'Tournament winner selected successfully!')
                return redirect('betting')

    else:
        underdog_form = UnderdogForm(instance=underdog)
        top_scorer_form = TopScorerForm(instance=top_scorer)
        winner_form = TournamentWinnerForm(instance=tournament_winner)

    context = {
        'available_matches': available_matches,
        'my_bets': my_bets,
        'underdog_form': underdog_form,
        'top_scorer_form': top_scorer_form,
        'winner_form': winner_form,
        'underdog': underdog,
        'top_scorer': top_scorer,
        'tournament_winner': tournament_winner,
    }

    return render(request, 'betting.html', context)


@login_required
def edit_bet(request, bet_id):
    bet = Bet.objects.get(id=bet_id, user=request.user)
    if request.method == 'POST':
        form = BetForm(request.POST, instance=bet)
        if form.is_valid():
            form.save()
            return redirect('betting')
    else:
        form = BetForm(instance=bet)

    return render(request, 'edit_bet.html', {
        'form': form,
        'bet': bet,
    })


@login_required
def profile(request):
    return render(request, 'profile.html')


def redirect_authenticated_user(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return view_func(request, *args, **kwargs)

    return wrapper


@login_required
def profile(request):
    return render(request, 'profile.html')


# def leaderboard(request):
#     leaderboard_data = UserPoints.objects.select_related('user').filter(user__is_superuser=False).order_by('-points')
#     # Get the maximum points
#     max_points = leaderboard_data.aggregate(max_points=Max('points'))['max_points']
#     return render(request, 'leaderboard.html', {'leaderboard': leaderboard_data, 'max_points': max_points})


def rules(request):
    article = Article.objects.filter(title='Rules').first()
    return render(request, 'rules.html', {'article': article})


# SUPERADMIN VIEWS

# Sprawdzenie, czy użytkownik jest superużytkownikiem
def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func


@superuser_required
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully')
            form = UserCreationForm()  # Reset the form after successful creation
        else:
            messages.error(request, 'There was an error creating the user')
    else:
        form = UserCreationForm()
    return render(request, 'create_user.html', {'form': form})


@superuser_required
def user_list(request):
    users = User.objects.filter(is_superuser=False)
    return render(request, 'user_list.html', {'users': users})


@superuser_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully')
            return redirect('user_list')
        else:
            messages.error(request, 'There was an error updating the user')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'edit_user.html', {'form': form, 'user': user})


def view_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'view_article.html', {'article': article})


@superuser_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully')
        return redirect('user_list')
    return render(request, 'delete_user.html', {'user': user})


# Sprawdzenie, czy użytkownik jest superużytkownikiem
def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func


@superuser_required
def article_list(request):
    articles = Article.objects.all()
    return render(request, 'article_list.html', {'articles': articles})


@superuser_required
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully')
            return redirect('article_list')
        else:
            messages.error(request, 'There was an error creating the article')
    else:
        form = ArticleForm()
    return render(request, 'create_article.html', {'form': form})


@superuser_required
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully')
            return redirect('article_list')
        else:
            messages.error(request, 'There was an error updating the article')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'edit_article.html', {'form': form})


@superuser_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted successfully')
        return redirect('article_list')
    return render(request, 'delete_article.html', {'article': article})


@superuser_required
def actual_results(request):
    matches = Match.objects.all()
    teams = Team.objects.all()
    top_scorers = TopScorer.objects.all()

    # Uzyskaj lub utwórz pojedynczy rekord dla wyników turnieju
    tournament_results, created = TournamentResults.objects.get_or_create(id=1)

    if request.method == 'POST':
        if 'save_match' in request.POST:
            match_id = request.POST.get('save_match')
            match = get_object_or_404(Match, id=match_id)
            home_score = request.POST.get(f'home_team_score_{match_id}')
            away_score = request.POST.get(f'away_team_score_{match_id}')
            final_score = f'final_score_{match_id}' in request.POST

            if home_score and away_score:
                actual_result, created = ActualResults.objects.get_or_create(match=match)
                actual_result.home_team_score = int(home_score)
                actual_result.away_team_score = int(away_score)
                actual_result.final_score = final_score
                actual_result.save()
                match.actual_home_team_score = int(home_score)
                match.actual_away_team_score = int(away_score)
                match.final_score = final_score
                match.save()

        elif 'save_winner' in request.POST:
            winner_team = request.POST.get('winner_team')
            team = Team.objects.filter(name=winner_team).first()
            if team:
                tournament_results.winner_team = team
                tournament_results.save()

        elif 'save_top_scorer' in request.POST:
            top_scorer_id = request.POST.get('top_scorer')
            if top_scorer_id:
                top_scorer = TopScorer.objects.get(id=top_scorer_id)
                # Znajdź lub utwórz instancję TopScorerSelection dla danego zawodnika
                top_scorer_selection, created = TopScorerSelection.objects.get_or_create(
                    player=top_scorer.player_name,
                    defaults={'country': top_scorer.country}
                )
                tournament_results.top_scorer = top_scorer_selection
                tournament_results.save()

        return redirect('actual_results')

    selected_winner = tournament_results.winner_team
    selected_top_scorer = tournament_results.top_scorer

    context = {
        'matches': matches,
        'teams': teams,
        'top_scorers': top_scorers,
        'selected_winner': selected_winner,
        'selected_top_scorer': selected_top_scorer,
    }
    return render(request, 'actual_results.html', context)


@superuser_required
def edit_actual_result(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    if request.method == 'POST':
        form = ActualResultForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            return redirect('actual_results')
    else:
        form = ActualResultForm(instance=match)

    return render(request, 'edit_actual_result.html', {'form': form, 'match': match})


def user_predictions(request):
    users = User.objects.filter(is_superuser=False)
    user_data = []

    for user in users:
        bets = Bet.objects.filter(user=user).select_related('match')
        underdog = UnderdogSelection.objects.filter(user=user).first()
        top_scorer = TopScorerSelection.objects.filter(user=user).first()
        tournament_winner = TournamentWinnerSelection.objects.filter(user=user).first()

        user_data.append({
            'user': user,
            'bets': bets,
            'underdog': underdog,
            'top_scorer': top_scorer,
            'tournament_winner': tournament_winner,
        })

    context = {
        'user_data': user_data,
        'matches': Match.objects.all(),
        'actual_results': ActualResults.objects.all(),
    }
    return render(request, 'user_predictions.html', context)


@superuser_required
def edit_points(request):
    users = User.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        points_to_add = request.POST.get('points_to_add')
        points_to_subtract = request.POST.get('points_to_subtract')

        if user_id:
            user_points = UserPoints.objects.get(user_id=user_id)

            if points_to_add:
                user_points.points += int(points_to_add)
                user_points.save()

            if points_to_subtract:
                user_points.points -= int(points_to_subtract)
                user_points.save()

            return redirect('edit_points')

    return render(request, 'edit_points.html', {'users': users})


@superuser_required
def create_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('actual_results')
    else:
        form = MatchForm()

    return render(request, 'create_match.html', {'form': form})

@superuser_required
def edit_bet_status(request):
    if request.method == "POST":
        # Process form submission
        bet_ids = request.POST.getlist('bet_id')
        statuses = request.POST.getlist('status')

        for bet_id, status in zip(bet_ids, statuses):
            bet = Bet.objects.get(pk=bet_id)
            bet.status = int(status)
            bet.save()

        return redirect('edit_bet_status')  # Redirect to avoid re-posting on refresh

    # Fetch users and their bets
    users_with_bets = User.objects.prefetch_related('bet_set').filter(bet__isnull=False, is_superuser=False)
    user_bets = {user: user.bet_set.all() for user in users_with_bets}

    context = {
        'user_bets': user_bets,
        'status_choices': Bet.STATUS_CHOICES,
    }
    return render(request, 'edit_bet_status.html', context)
