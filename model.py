from intefaces import IModel
import json
from numbs_aux import generate_numbers, test_numbers
from data_models import *
from intefaces import IPresenter

GAMES_AMOUNT = 10000
PLAYERS_PER_TEAM = 5
ROUNDS_PER_GAME = 10

class Model(IModel):
    def __init__(self):
        self.nums_configurations = []
        self.nums_index = 0
        self.numbers = []
        self.current_number = 0
        self.load_configurations()
        self.load_index()

    def set_presenter(self, presenter):
        self.presenter: IPresenter = presenter

    def start_simulation(self):
        self.generate_sim_numbers()
        self.teams : list[Team] = self.generate_teams()
        self.players : list[Player] = []
        for team in self.teams:
            for i in range(PLAYERS_PER_TEAM):
                self.players.append(self.generate_player(team, f"Jugador {team.name} {i+1}"))
        self.games : list[Game] = []
        for i in range(GAMES_AMOUNT):
            rounds : list[Round] = []
            for j in range(ROUNDS_PER_GAME):
                luck_values = self.generate_players_luck_values(self.players)
                shots, endurance_values = self.generate_shots_and_endurance_values(luck_values, rounds)
                winner_player, winner_team = self.calculate_winner(shots)
                rounds.append(Round(j+1,shots, luck_values, endurance_values, winner_player, winner_team))
            winner_player, winner_team, luckiest_player = self.calculate_game_winner(rounds)
            self.games.append(Game(i+1, rounds, winner_team, winner_player, luckiest_player))
        luckiest_player_per_game = self.calculate_luckiest_player_per_games()
        more_experienced_player = self.calculate_more_experienced_player()
        winner_team_total = self.calculate_team_winner()
        winner_gender_per_game = self.calculate_winner_gender_per_game()
        winner_gender_total = self.calculate_winner_gender_total()
        points_vs_games_per_player = self.calculate_points_vs_games_per_player()
        results = {
            "luckiest_player_per_game": luckiest_player_per_game,
            "more_experienced_player": more_experienced_player,
            "winner_team_total": winner_team_total,
            "winner_gender_per_game": winner_gender_per_game,
            "winner_gender_total": winner_gender_total,
            "points_vs_games_per_player": points_vs_games_per_player
        }
        self.presenter.show_results(results)

    # para sacar un numero pseudorandom lo que hacen es:
    # number = self.get_pseudorandom_number()

    def generate_teams(self): 
        team1 = Team(name="Team A")
        team2 = Team(name="Team B")
        return [team1, team2]

    def generate_player(self, team, name):
       if self.get_pseudorandom_number() < 0.5:
           is_male = True
       else:
           is_male = False    
       original_endurance = round(30 + ( (40 - 30)* self.get_pseudorandom_number()))
       experience = 10
       player = Player(name,team, is_male, original_endurance, experience)
       return  player
    
    def generate_players_luck_values(self): 
      players_luck = []
      for player in self.players:
         luck_value = 1 + ((3 - 1) * self.get_pseudorandom_number())
         players_luck.append({"value": luck_value, "player": player}) 
      team_a_players = [player for player in players_luck if player["player"].team.name == "Team A"]
      team_b_players = [player for player in players_luck if player["player"].team.name == "Team B"]
      team_a_players.sort(key=lambda p: p["value"], reverse=True)
      team_b_players.sort(key=lambda p: p["value"], reverse=True)
      top_lucky_player_team_a = team_a_players[0] 
      top_lucky_player_team_b = team_b_players[0] 
      top_lucky_players = [
          LuckValue(top_lucky_player_team_a["player"], top_lucky_player_team_a["value"]), 
          LuckValue(top_lucky_player_team_b["player"], top_lucky_player_team_b["value"])
        ]
      return top_lucky_players
   
    def generate_shots_and_endurance_values(self, luck_values: list[LuckValue], rounds: list[Round]):
        shots: list[Shot] = []
        endurance_values: list[EnduranceValue] = []
        points_total_rd = []
        for player in self.players:
            endurance = self.generatePlayer_endurance(player, rounds)
            current_endurance = endurance.value
            # normal shots
            pts = { "player": player, "points": 0 }
            while current_endurance >= 5:
                shot = self.do_shot(player, len(shots) + 1)
                shots.append(shot)
                current_endurance -= 5
                player.total_points += shot.score
                pts["points"] += shot.score
            endurance_values.append(endurance)
            points_total_rd.append(pts)
        # luck shots
        luckiest_players = [player for player in self.players if player.name == luck_values[0].player.name 
                            or player.name == luck_values[1].player.name]
        if len(rounds) >= 3:
            names_list = []
            for round in list(filter(lambda value: (len(rounds) + 1) - value.round_number <= 3, rounds)):
                lvs = round.luck_values
                names_list.extend([lv.player.name for lv in lvs])
            for name in set(names_list):
                if len(list(filter(lambda name_l: name_l == name, names_list))) == 3:
                    luckiest_players.append(list(filter(lambda player: player.name == name, self.players))[0])
        for player in luckiest_players:
            shot = self.do_shot(player, len(shots) + 1, "LS")
            shots.append(shot)
            player.total_points += shot.score
        # extra shots
        max_pts = max([pts["points"] for pts in points_total_rd])
        max_pst_list = list(filter(lambda pts: pts["points"] == max_pts, points_total_rd))
        if len(max_pst_list) > 1:
            while len(set([pts["points"] for pts in max_pst_list])) != len(max_pst_list):
                for stl in max_pst_list:
                    player = stl["player"]
                    shot = self.do_shot(player, len(shots) + 1, "ES")
                    shots.append(shot)
                    player.total_points += shot.score
                    stl["points"] += shot.score
        return shots, endurance_values

    def do_shot(self, player: Player, n_shot: int, type = "NS"):
        num = self.get_pseudorandom_number()
        if player.is_male:
            score = self.calculate_score_male(num)
        else:
            score = self.calculate_score_female(num)
        return Shot(player, score, n_shot, type)
    
    def generatePlayer_endurance(self, player: Player, rounds: list[Round]):
        if not rounds:
            endurance = player.original_endurance
        else:
            last_endurance = list(filter(lambda value:value.player.name == player.name, 
                                            rounds[len(rounds) - 1].endurance_values))[0]
            won_list = [round for round in rounds if round.winner_player.name == player.name]
            if len(won_list) < 3:
                endurance = last_endurance.value - (1 if self.get_pseudorandom_number() <= 0.5 else 2)
            else:
                rounds_dif = rounds[len(rounds) - 1].number - won_list[len(won_list) - 1].number
                if rounds_dif <= 2:
                    endurance = last_endurance.value - 1
                else:
                    endurance = last_endurance.value - (1 if self.get_pseudorandom_number() <= 0.5 else 2)
        return EnduranceValue(player, endurance)

    def calculate_score_male(self, score):
        if score <= 0.2:
            return 10
        elif score > 0.2 and score <= 0.53:
            return 9
        elif score > 0.53 and score <= 0.93:
            return 8
        else: return 0
        
    def calculate_score_female(self, score):
        if score <= 0.3:
            return 10
        elif score > 0.3 and score <= 0.68:
            return 9
        elif score > 0.68 and score <= 0.95:
            return 8
        else: return 0

    def calculate_winner(self, shots): #usar los shots
        # no tener en cuenta en jugador ganador los lanzamientos de suerte
        # no tener en cuenta en equipo ganador los lanzamientos de extra indivuales
        #calcular el ganador de la ronda y el equipo ganador
        # acutualizar experiencia de ganador en self.players
        pass

    def calculate_game_winner(self, rounds): #usar los rounds
        #calcular el equipo ganador del juego y el jugador ganador del juego
        #acutualizar experiencia de ganador en self.players
        pass

    def calculate_luckiest_player_per_games(self): #usar self.games *?
        luck_counts = {}
        for game in self.games:
            luckiest_player = game.luckiest_player
            luck_counts[luckiest_player] += 1
        luckiest_player_overall = max(luck_counts, key=luck_counts.get)
        return {
            "player": luckiest_player_overall,
            "amount_luck": luck_counts[luckiest_player_overall]
        }

    def calculate_more_experienced_player(self): #usar self.players
        most_experienced_player = max(self.players, key=lambda player: player.experience)
        return {
            "player": most_experienced_player,
            "amount_experienced": most_experienced_player.experience
        }


    def calculate_team_winner(self): #usar self.games
        count_wins_team_a = 0
        count_wins_team_b = 0
        final_winner_team: Team = None
        final_players_win_points:list = []
        for game in self.games:
            count_wins_team_a += game.winner_team.name == 'Team A'
            count_wins_team_b += game.winner_team.name  == 'Team B'
        if count_wins_team_a > count_wins_team_b:
            final_winner_team = self.teams[0]
        else: 
            final_winner_team = self.teams[1]
        for player in self.players:
            if player.team.name == final_winner_team.name:
                final_players_win_points.append({"player":player.name, "points":player.total_points})
        return {"team":final_winner_team, "player_points": final_players_win_points}

    def calculate_winner_gender_per_game(self): #usar self.games *?
        count_wins_male = 0
        count_wins_female = 0
        count_win = 0
        gender_win = ''
        for game in self.games:
            if game.winner_player.is_male:
                count_wins_male += 1
            else:
                count_wins_female +=1
        if count_wins_male > count_wins_female:
            gender_win = 'Hombres'
            count_win = count_wins_male
        else:
            gender_win = 'Mujeres'
            count_win = count_wins_female
        return {"gender": gender_win  , "amount_wins":count_win }
        
        # calcular el genero ganador por juego
        # creo que es con contando el genero mas victorioso en cada juego, y ver cual es el que se repite mas
        # retornar objeto { gender: x, amount_wins: x }
        

    def calculate_winner_gender_total(self): #usar self.games
        male_wins = 0
        female_wins = 0
        for game in self.games:
            for round_game in game.rounds:
                winner_player = round_game.winner_player
                if winner_player.is_male:
                    male_wins += 1
                else:
                    female_wins += 1
        winner_gender = "Male" if male_wins > female_wins else "Female"
        return {
            "gender": winner_gender,
            "total_rounds_won": {"Male": male_wins, "Female": female_wins}
            }
    

        # calcular el genero ganador en total
        # retornar objeto { gender: x, amount_wins: x }

    def calculate_points_vs_games_per_player(self): #usar self.games
        players_with_points: list = [{"player": player, "points": []} for player in self.players]
        for game in self.games:
            game_points = {player.name: 0 for player in self.players}
            for round_game in game.rounds:
                for shot in round_game.shots:
                    game_points[shot.player.name] += shot.score
            for player_points in players_with_points:
                player_name = player_points["player"].name
                player_points["points"].append(game_points.get(player_name, 0))
        # calcular los puntos de cada jugador por juego
        # retornar objeto [{ player: x, points: [x, x,...]}]
        return players_with_points
    def get_pseudorandom_number(self):
        number = self.numbers[self.current_number]
        self.current_number += 1
        return number

    def generate_sim_numbers(self):
        self.numbers = generate_numbers(self.nums_configurations[self.nums_index]['conf1']).extend(
            generate_numbers(self.nums_configurations[self.nums_index]['conf2']))
        self.change_index()
        while not test_numbers(self.numbers):
            self.numbers = generate_numbers(self.nums_configurations[self.nums_index]['conf1']).extend(
                generate_numbers(self.nums_configurations[self.nums_index]['conf2']))
            self.change_index()

    def load_configurations(self):
        with open('lcg_configurations.json', 'r') as f:
            self.nums_configurations = json.load(f)

    def load_index(self):
        with open('nums_info.json', 'r') as f:
            self.nums_index = json.load(f)["index"]

    def change_index(self):
        self.nums_index = self.nums_index + 1 if self.nums_index < len(self.nums_configurations) - 1 else 0
        with open('nums_info.json', 'w') as f:
            json.dump({"index": self.nums_index}, f)