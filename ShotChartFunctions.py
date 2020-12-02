import requests
from lxml import html
import re


def go_to_shot_chart(boxScoreLink):
    '''
    return list with path to shot chart.
    '''
    page = requests.get(boxScoreLink)
    tree = html.fromstring(page.content)
    # if empty list has no shot chart
    finds = tree.xpath('//*[@class="filter"]/div/a/@href')
    return [l for l in finds if bool(re.search('shot-chart', l))]


def clean_tip_string(string):
    '''
    takes string from shot chart of tip = "TEXT"
    i.e. TEXT = '1st quarter, 11:25.0 remaining<br>Darrell Armstrong made 2-pointer from 17 ft<br>Orlando now tied 2-2'
    Extract:
    Time remaining
    Distance to hoop
    game score
    player's team
    return them in a list [time, dist, game score, team]
    '''
    time_remain = string.split()[2]
    game_score = string.split()[-1]
    shot_dist = re.search('(?<=from ).*(?=ft)', string)[0].strip()
    players_team = string.split('<br>')[-1].split()[0]
    return [time_remain, shot_dist, game_score, players_team]


def extract_shot_data(shotChartLink):
    '''
    return data pulled from the shot shart list of lists
    [[playerkey,...]]
    '''
    page = requests.get(shotChartLink)
    tree = html.fromstring(page.content)

    # create [player key, qtr, make/miss]
    # ['tooltip', 'q-1', 'p-armstda01', 'make']
    shot_data = []  # player metadata
    for md in tree.xpath('//*[@class="shot-area"]/div/@class'):
        temp = md.split()
        shot_data.append([temp[2][2:], int(temp[1][-1]), temp[3]])

    # ['TOP','LEFT'] px from there
    shoot_pos = [re.findall('\d+', pos) for pos in tree.xpath('//*[@class="shot-area"]/div/@style')]

    # [time(minutes:seconds.0), dist shot (ft), game score]
    game_data = [clean_tip_string(string) for string in tree.xpath('//*[@class="shot-area"]/div/@tip')]

    # Extract year is number that represents the season. so 1968-1969 -> 1969.
    temp = tree.xpath('//*[@class="scorebox"]/div/div/strong/a/@href')
    year = temp[0].split('/')[-1][:4]
    team_1 = temp[0].split('/')[2]
    team_2 = temp[1].split('/')[2]
    # Create output [[features],...,]

    output = []
    for i in range(0, len(shoot_pos)):
        # [player key, qtr, make/miss, TOP_dist, LEFT_dist, time remaining, dist shot,
        # game score, players_team ,team_1=away, team_2=home, year]
        output.append(shot_data[i] + shoot_pos[i] + game_data[i] + [team_1, team_2, year])

    return output


def get_single_shot_chart_data(boxScoreLink):
    '''
    Get all shot chart data for a single game.
    '''
    base_path = "https://www.basketball-reference.com"
    shot_path = go_to_shot_chart(boxScoreLink)

    if len(shot_path) == 1:
        shotChartLink = base_path + shot_path[0]  # link to path
        return (extract_shot_data(shotChartLink))
    else:
        return ([])  # empty list if no shot chart available

