import time, os, json
from riotwatcher import LolWatcher, ApiError
import champs_id
import main

def get_JSON_api_key(file_name):
    with open(file_name, 'r+') as f:
        data = json.load(f)
    return data['API_key']

def set_JSON_api_key(file_name, api_key):
    with open(file_name, 'w') as f:
        json.dump({'API_key': api_key}, f)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

class Player(LolWatcher):
    def __init__(self, api_key, region, summoner_name):
        super().__init__(api_key=api_key)
        self.region = region
        self.summoner_name = summoner_name
        self.api_key = api_key
        
        
    def get_observer(self):
        return self.spectator.by_summoner(self.region, self.get_summoner(self.summoner_name, 'id'))


    def get_summoner(self, name, w=None):
        try:
            return self.summoner.by_name(self.region, name)[w if w != None else self.summoner.by_name(self.region, name)]
        except Exception as err:
            if err == err.response.status_code == 404:
                print('Summoner not found, you will be redirected to the main page')
                print(err)
                main.main()
            elif err == err.response.status_code == 429:
                api_key=input('The API Key is expired, please enter a new one')
                self.api_key = api_key
                set_JSON_api_key('data.json', api_key)



    def get_stats(self, summoner):
        return 'unranked' if self.league.by_summoner(self.region, summoner) == [] else self.league.by_summoner(self.region, summoner)


    def get_champ_info(self, summoner):
        return self.champion_mastery.by_summoner(self.region, summoner)


    def get_match(self, count=10):
        return self.match.matchlist_by_puuid(self.region, self.get_summoner(self.summoner_name, 'puuid'), count=count)


    def get_game(self, match_id):
        return self.match.by_id(self.region, match_id)
    
    def confirm_game_exist(self):
        try:
            self.get_observer()
            return True
        except:
            return False


    def show_game_info(self):
        n=1
        for player in self.get_observer()['participants']:
            player_name = player['summonerName']
            player_id = player['summonerId']
            player_level = self.get_summoner(player['summonerName'], 'summonerLevel')
            player_champ_id = player['championId']
            player_current_champ = champs_id.get_champ_name(player_champ_id)
            champs = self.get_champ_info(player_id)
            player_current_champ_mastery = str([champ['championPoints'] for champ in champs if champ['championId'] == player_champ_id])
            player_main_champ = champs_id.get_champ_name(self.get_champ_info(player_id)[0]['championId'])
            player_main_champ_mastery = self.get_champ_info(player_id)[0]['championPoints']
            player_stats = self.get_stats(player_id)
            rank = 'Unranked' if player_stats == 'unranked' else f"'{player_stats[0]['tier']} {player_stats[0]['rank']}"
            print(
f'''
{n}. {player_name}
Level: {player_level}
Current champ: {player_current_champ} Mastery points {player_current_champ_mastery}
Main champ: {player_main_champ} Mastery points {player_main_champ_mastery}
Rank: {'unranked' if rank == 'Unranked' else rank}
''')
            n+= 1

    
    def show_history(self):
        option = input('Do you want to see the history of the last 10 games? (y/n) ')
        if option == 'y':
            clear()
            matchs = self.get_match()
            for match in matchs:
                #takes all data from the match
                player_puuid = self.get_summoner(self.summoner_name, 'puuid')
                game = self.get_game(match)
                game_info = game['info']
                player_target = [i for i in game_info['participants'] if i['puuid'] == player_puuid][0]
                player_id = player_target['summonerId']
                champs = self.get_champ_info(player_id)
                player_champ_id = player_target['championId']
                #variables for the print
                game_type = game_info['gameType']
                game_map = game_info['mapId']
                player_champ = champs_id.get_champ_name(player_champ_id)
                player_name = player_target['summonerName']
                player_champ_mastery_points = [champ for champ in champs if champ['championId'] == player_champ_id][0]['championPoints']
                player_champ_mastery = [champ for champ in champs if champ['championId'] == player_champ_id][0]['championLevel']
                win = player_target['win']
                player_role = player_target['role']
                player_rache = player_target['kills']
                player_death = player_target['deaths']
                player_assist = player_target['assists']
                player_farm = player_target['totalMinionsKilled']
                print(match)
                print(
f'''
Game type: {game_type}
Game map: {game_map}
Player: {player_name}
Champion: {player_champ} Mastery points {player_champ_mastery_points} Mastery level {player_champ_mastery}
Role: {player_role}
Kills: {player_rache}
Deaths: {player_death}
Assists: {player_assist}
Farm: {player_farm}
The game was: {'win' if win else 'lose'}
''')
            print('You gonna be redirected to your main page')
            self.show_info_ofline()
                
        elif option == 'n':
            clear()
            print('You will be redirected to your personal info')
            self.show_info_ofline()
        else:
            print("No valid option")
            self.show_history()

        
    def show_info_ofline(self):
        summoner_id=self.get_summoner(self.summoner_name, 'id')
        summoner_level=self.get_summoner(self.summoner_name, 'summonerLevel')
        stats=self.get_stats(summoner_id)
        champ = self.get_champ_info(summoner_id)
        main_champ_id=champ[0]['championId']
        main_champ = champs_id.get_champ_name(main_champ_id)
        main_champ_mastery = champ[0]['championPoints']
        main_champ_level = champ[0]['championLevel']
        tier = stats[0]['tier'] if stats != 'unranked' else 'Unranked'
        rank = stats[0]['rank'] if stats != 'unranked' else 'Unranked'
        print(
f'''
Name: {self.summoner_name}
Level: {summoner_level}
Main: {main_champ} Mastery points {main_champ_mastery} Mastery {main_champ_level}
Rank: {'Unrank' if stats == 'unranked' else f'{"" if tier == "Unranked" and rank == "Unranked" else f"{tier} {rank}"} '}
''')
        its_on_game = self.confirm_game_exist()
        print('What do you want to do?')
        i = input(
f'''
1. {"Show current game stats" if its_on_game else "Show info ofline (not on game)"}
2. Show history
3. Show personal info
4. Exit
''')
        if i.isdigit():
            if int(i) ==1 and its_on_game:
                self.show_game_info()
            elif int(i) == 2:
                self.show_history()
            elif int(i) == 3:
                self.show_info_ofline()
            elif int(i) == 4:
                print('Bye')
                exit()
            else:
                print('No valid option')
                self.show_info_ofline()
        else:
            print(f'{i} is not a valid option, please try again')
            self.show_info_ofline()
