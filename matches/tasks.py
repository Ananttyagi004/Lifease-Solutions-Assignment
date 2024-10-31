import requests
from bs4 import BeautifulSoup
from celery import shared_task
from datetime import datetime, timedelta,time
from django.utils import timezone
from .models import Match


BASE_URL = 'https://crex.live'

from datetime import datetime
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from .models import Match  

BASE_URL = 'https://example.com'  

@shared_task
def scrape_match_list():
    url = f'{BASE_URL}/fixtures/match-list'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    match_cards = soup.select('li.match-card-container')
    
    for card in match_cards:
        match_link = card.find('a', class_='match-card-wrapper')
        match_url = match_link['href'].rsplit('/', 1)[0]
        match_id = match_url
        
        teams = card.select('.team-name')
        team_a_name = teams[0].text.strip()
        team_b_name = teams[1].text.strip()
        
        start_time_text = card.find('div', class_='start-text')
        if start_time_text:
            start_time_str = start_time_text.text.strip()
            start_time = datetime.strptime(start_time_str, '%I:%M %p')
        else:
            start_time = None

        team_a_squad = []
        team_b_squad = []

        url_info = f'{BASE_URL}{match_id}/info'
        response_info = requests.get(url_info)
        soup_info = BeautifulSoup(response_info.content, 'html.parser')

        players = soup_info.select('a[href^="/player-profile/"]')

        for i, player in enumerate(players):
            href = player['href']
            player_name = href.split('/')[-1]
            team_a_squad.append(player_name)

        players = soup_info.select('a[href^="/player-profile/"]')

        for i, player in enumerate(players):
            href = player['href']
            player_name = href.split('/')[-1]
            team_b_squad.append(player_name)

    
        match_obj = Match.objects.create(
            match_id=match_id,
            team_a=team_a_name,
            team_b=team_b_name,
            start_time=start_time,
            team_a_squad=team_a_squad
            team_b_squad=team_b_squad
        )

        
        if start_time:
            scrape_live_and_scorecard.apply_async((match_obj.id,), eta=match_obj.start_time)

def scrape_scorecard(match_id):
    """Scrape  scorecard data for an ongoing match."""
    url_scorecard = f'{BASE_URL}{match_id}/scorecard'
    response_scorecard = requests.get(url_scorecard)
    soup = BeautifulSoup(response_scorecard.content, 'html.parser')

    team_data = []
    teams = soup.find_all("div", class_="team-tab")  
    for team in teams:
        team_name = team.find("span", class_="team-name").get_text(strip=True)
        score = team.find("div", class_="score-over").find_all("span")[0].get_text(strip=True)
        overs = team.find("div", class_="score-over").find_all("span")[1].get_text(strip=True)
        team_data.append({
            'team_name': team_name,
            'score': score,
            'overs': overs
        })


    return team_data



def scrape_live(match_id):
    """Scrape  live data for an ongoing match."""
    url_live = f'{BASE_URL}{match_id}/live'
    response_live = requests.get(url_live)
    soup = BeautifulSoup(response_live.content, 'html.parser')

    batsmen_data = []

    for batsman in soup.select('.playing-batsmen-wrapper .batsmen-partnership'):
    
        name_tag = batsman.select_one('.batsmen-name p')
        name = name_tag.get_text(strip=True) if name_tag else "N/A"

  
        score_tag = batsman.select_one('.batsmen-score')
        runs_tag = score_tag.find('p') if score_tag else None
        runs = runs_tag.get_text(strip=True) if runs_tag else "N/A"

        
        balls_tag = score_tag.find_all('p')[1] if score_tag and len(score_tag.find_all('p')) > 1 else None
        balls = balls_tag.get_text(strip=True) if balls_tag else "N/A"
        
        batsmen_data.append({
            'Name': name,
            'Runs': runs,
            'Balls': balls,
  })

    return batsmen_data


@shared_task
def scrape_live_and_scorecard(match_id):
    """Scrape live and scorecard data for an ongoing match."""
    while True:
        match=Match.objects.get(id=match_id)
        scorecard=scrape_scorecard(match_id)
        live=scrape_live(match_id)
        match.scorecard_data=scorecard
        match.live_data=live
        match.save
     # Check if match is over based on the scorecard
        team1_score = int(scorecard[0]['score'].split('-')[0])
        team1_wickets = int(scorecard[0]['score'].split('-')[1])
        team1_overs = float(scorecard[0]['overs'].strip('()'))

        team2_score = int(scorecard[1]['score'].split('-')[0])
        team2_wickets = int(scorecard[1]['score'].split('-')[1])
        team2_overs = float(scorecard[1]['overs'].strip('()'))

        # End condition: Check if team 1 has completed innings, or team 2 has reached the target
        if team1_wickets >= 10 or team1_overs >= 10:  # Assuming 10 overs per inning
            if team2_score > team1_score or (team2_score == team1_score and team2_overs >= team1_overs):
                print("Match is over")
                break

        time.sleep(60)  # Wait 1 minute before next check
        
       