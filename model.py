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

   
    def generate_shots_and_endurance_values(self, luck_values, rounds): #usar los endurance_values y la info del player de cada endurance_value
        endurance_values = [] # calcular los endurance_values: resistencia en jugadores menos 1 o 2 (excepto la primera ronda ya que se usa la resistencia original)
        #si tiene 9 puntos de experiencia mas solo es 1 menos (verificarlo con ganador de rondas anteriores)
        #generar los lanzamientos para todos los jugadores hasta que no tengan reistencia
        # tambien lanzamientos de sorteo con luck_values
        # y lanzamientos de extra para ganador individual si es necesario
        # teniendo en cuanta la matriz montecarlo para cada genero
        # reducir los endurance values de cada jugador en cada tiro
        # verificar otras restricciones
        pass
        #1h
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
        # calcular el jugador con mas suerte para cada juego
        # creo que es con contando game.luckiest_player
        # retornar objeto { player: x, amount_luck: x }
        pass

    def calculate_more_experienced_player(self): #usar self.players
        # calcular el jugador con mas experiencia al final de todos los juegos
        # retornar objeto { player: x, amount_experienced: x }
        pass

    ##

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