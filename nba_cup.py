# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 18:25:36 2024

@author: llama
"""

class Team:
    def __init__(self, city, name, nickname):
        self.city = city
        self.name = name
        self.nickname = nickname
        self.played=0
        self.wins=0
        self.losses=0
        self.played_tiebreaker=0
        self.wins_tiebreaker=0
        self.losses_tiebreaker=0
        self.point_difference=0
        self.win_pct=0
        self.win_pct_tiebreaker=0
        self.teams_defeated=set({})
        self.defeated_by=set({})
        self.games_played=[]
    def printer(self):
        return (self.city + " " + self.name).ljust(25) + '   ' + str(self.wins) + "-" +  str(self.losses) + '   '  +  '{0:.2f}'.format(self.win_pct) + ' ' +  str(self.point_difference).rjust(4)
    
    def __lt__(self, other):
        return self.win_pct > other.win_pct
    
    def upload_win(self, opponent, point_difference, game):
        self.played = self.played + 1
        self.wins = self.wins + 1
        self.point_difference = self.point_difference + point_difference
        self.win_pct = self.wins / self.played
        self.games_played.append(game)
        self.teams_defeated.add(opponent)
    def remove_win(self, opponent, point_difference, game):
        self.played = self.played - 1
        self.wins = self.wins - 1
        self.point_difference = self.point_difference - point_difference
        self.win_pct = self.wins / self.played
        self.games_played.remove(game)
        self.teams_defeated.remove(opponent)
        
    def upload_loss(self, opponent, point_difference, game):
        self.played = self.played + 1
        self.losses = self.losses + 1
        self.point_difference = self.point_difference - point_difference
        self.win_pct = self.wins / self.played
        self.games_played.append(game)
        self.defeated_by.add(opponent)
    def remove_loss(self, opponent, point_difference, game):
        self.played = self.played - 1
        self.losses = self.losses - 1
        self.point_difference = self.point_difference + point_difference
        self.win_pct = self.wins / self.played
        self.games_played.remove(game)
        self.defeated_by.remove(opponent)
        
class Game:
    def __init__(self, local, visitant, played, score=[]):
        self.local=local
        self.visitant=visitant
        self.played=played
        if played:
            self.points_local = score[0]
            self.points_visitant = score[1]
    def winner(self):
        if self.points_local > self.points_visitant:
            return self.local
        else:
            return self.visitant
    def loser(self):
        if self.points_local < self.points_visitant:
            return self.local
        else:
            return self.visitant
    def point_difference(self):
        return abs(self.points_local - self.points_visitant)
    
class Group:
    def __init__(self, conference, name, teams, games_played, games_to_play, team_dic):
        self.conference = conference
        self.name = name
        self.teams = teams
        self.num_teams = len(teams)
        self.games_played = games_played
        self.games_to_play = games_to_play        
        self.team_dic = team_dic
        self.update_leaderboard(games_played)
        
    def update_leaderboard(self, new_games):
        for game in new_games:
            team_dic[game.winner()].upload_win(self.team_dic[game.loser()], game.point_difference(), game)
            team_dic[game.loser()].upload_loss(self.team_dic[game.winner()], game.point_difference(), game)
            
    def leaderboard(self, consider_point_diff=True):
        standings = sorted(self.teams, key=lambda x: -x.win_pct)
        final_standings=[]
        final_standings.append([standings[0]])
        for i in range(1, len(standings)):
            if standings[i-1].win_pct==standings[i].win_pct:
                final_standings[-1].append(standings[i])
            else:
                final_standings.append([standings[i]])
        return_value=[]
        for tie in final_standings:
            if len(tie)>1:
                return_value = return_value + tiebreaker(tie,consider_point_diff)
            else:
                return_value.append(tie[0])
        return return_value
    
    def print_leaderboard(self, consider_point_diff=True):
        i=1
        print("\n"+self.conference + " Group " + self.name+"\n")
        print("     Team".ljust(30)+"Record".ljust(7)+"Win %".ljust(7)+"DIFF".ljust(5))
        leaderboard=self.leaderboard(consider_point_diff)
        for team in leaderboard:
            if type(team) is list:
                for t in team:
                    print(str(i) + '.- ' + t.printer())
                i=i+len(team)
            else:
                print(str(i) + '.- ' + team.printer())
                i=i+1
        print("\n\n")
        
    def possibilities(self, games_to_play, previous_assumptions):
        if len(games_to_play)==0:
            print(previous_assumptions)
            self.print_leaderboard(False)
        else:
            game = games_to_play[0]
            
            #Local team wins
            self.team_dic[game.local].upload_win(self.team_dic[game.visitant],1,game)
            self.team_dic[game.visitant].upload_loss(self.team_dic[game.local],1,game)
            if previous_assumptions!="IF    ":
                pa=previous_assumptions + "    AND    " + game.local + " beats " +game.visitant
            else:
                pa = "IF    " + game.local + " beats " +game.visitant
            self.possibilities(games_to_play[1:], pa)
            self.team_dic[game.local].remove_win(self.team_dic[game.visitant],1,game)
            self.team_dic[game.visitant].remove_loss(self.team_dic[game.local],1,game)
            
            #Visitant team wins
            self.team_dic[game.visitant].upload_win(self.team_dic[game.local],1,game)
            self.team_dic[game.local].upload_loss(self.team_dic[game.visitant],1,game)
            if previous_assumptions!="IF    ":
                pa=previous_assumptions + "    AND    " + game.visitant + " beats " +game.local
            else:
                pa = "IF    " + game.visitant + " beats " +game.local
            self.possibilities(games_to_play[1:], pa)
            self.team_dic[game.visitant].remove_win(self.team_dic[game.local],1,game)
            self.team_dic[game.local].remove_loss(self.team_dic[game.visitant],1,game)
            
def tiebreaker(teams, consider_point_diff=True):
    for team in teams:
        team.played_tiebreaker=0
        team.wins_tiebreaker=0
        team.losses_tiebreaker=0
        for opponent in teams:
            if opponent in team.defeated_by:
                 team.played_tiebreaker = team.played_tiebreaker + 1
                 team.losses_tiebreaker = team.losses_tiebreaker + 1
            if opponent in team.teams_defeated:
                 team.played_tiebreaker = team.played_tiebreaker + 1
                 team.wins_tiebreaker = team.wins_tiebreaker + 1
        if team.played_tiebreaker>0:
            team.win_pct_tiebreaker = team.wins_tiebreaker / team.played_tiebreaker
        else:
            team.win_pct_tiebreaker = 0
    standings=sorted(teams, key =lambda x: -x.win_pct_tiebreaker)
    final_standings=[]
    final_standings.append([standings[0]])
    for i in range(1, len(standings)):
        if standings[i-1].win_pct_tiebreaker==standings[i].win_pct_tiebreaker:
            final_standings[-1].append(standings[i])
        else:
            final_standings.append([standings[i]])
    return_value=[]
    for tie in final_standings:
        if len(tie)>1:
            if len(tie)==len(teams):
                # All teams have the same win %
                if consider_point_diff:
                    substandings=sorted(tie, key =lambda x: -x.point_difference)
                    final_substandings=[]
                    final_substandings.append([substandings[0]])
                    for i in range(1, len(substandings)):
                        if substandings[i-1].point_difference==substandings[i].point_difference:
                            final_substandings[-1].append(substandings[i])
                        else:
                            final_substandings.append([substandings[i]])
                    for i in final_substandings:
                        if len(i)==1:
                            return_value.append(i[0])
                        else:
                            return_value.append(i)
                else:
                    return_value.append(teams)
            else:
                return_value = return_value + tiebreaker(tie)
        else:
            return_value.append(tie[0])
    return return_value

team_dic={"ORL": Team("Orlando","Magic","ORL"),
          "NYK": Team("New York","Knicks","NYK"),
          "PHI": Team("Philadelphia","76ers","PHI"),
          "BKN": Team("Brooklyn","Nets","BKN"),
          "CHA": Team("Charlotte","Hornets","CHA"),
          "MIL": Team("Milwaukee","Bucks","MIL"),
          "DET": Team("Detroit","Pistons","DET"),
          "MIA": Team("Miami","Heat","MIA"),
          "TOR": Team("Toronto","Raptors","TOR"),
          "IND": Team("Indiana","Pacers","IND"),
          "ATL": Team("Atlanta","Hawks","ATL"),
          "BOS": Team("Boston","Celtics","BOS"),
          "CLE": Team("Cleveland","Cavaliers","CLE"),
          "CHI": Team("Chicago","Bulls","CHI"),
          "WAS": Team("Washington","Wizards","WAS"),
          "HOU": Team("Houston","Rockets","HOU"),
          "POR": Team("Portland","Trail Blazers","POR"),
          "MIN": Team("Minnesota","Timberwolves","MIN"),
          "LAC": Team("Los Angeles","Clippers","LAC"),
          "SAC": Team("Sacramento","Kings","SAC"),
          "LAL": Team("Los Angeles","Lakers","LAL"),
          "SAS": Team("San Antonio","Spurs","SAS"),
          "OKC": Team("Oklahoma City","Thunder","OKC"),
          "PHX": Team("Phoenix","Suns","PHX"),
          "UTA": Team("Utah","Jazz","UTA"),
          "GSW": Team("Golden State","Warriors","GSW"),
          "DAL": Team("Dallas","Mavericks","DAL"),
          "NOP": Team("New Orleans","Pelicans","NOP"),
          "DEN": Team("Denver","Nuggets","DEN"),
          "MEM": Team("Memphis","Grizzlies","MEM"),
          }


#EAST GROUP A    
teams_A_East=["ORL","NYK","PHI","BKN","CHA"]

games_played_east_A=[Game("ORL","CHA", True, [114,89]),
                      Game("PHI","NYK", True, [99,111]),
                      Game("ORL","PHI", True, [98,86]),
                      Game("NYK","BKN", True, [124,122]),
                      Game("BKN","CHA", True, [116,115]),
                      Game("PHI","BKN", True, [113,98])]

games_to_play_east_A=[Game("CHA","NYK", False),
                      Game("BKN","ORL", False),
                      Game("CHA","PHI", False),
                      Game("NYK","ORL", False)]

group_east_A = Group("East", "A", [team_dic[team] for team in teams_A_East],
                     games_played_east_A, games_to_play_east_A, team_dic)


#EAST GROUP B 
teams_B_East=["MIL","DET","MIA","TOR","IND"]

games_played_east_B=[Game("DET","MIA", True, [123,121]),
                      Game("MIL","TOR", True, [99,85]),
                      Game("IND","MIA", True, [111,124]),
                      Game("TOR","DET", True, [95,99]),
                      Game("MIL","IND", True, [129,117])]

games_to_play_east_B=[Game("MIA","MIL", False),
                      Game("IND","DET", False),
                      Game("MIA","TOR", False),
                      Game("DET","MIL", False),
                      Game("TOR","IND", False)]
group_east_B = Group("East", "B", [team_dic[team] for team in teams_B_East],
                     games_played_east_B, games_to_play_east_B, team_dic)


#EAST GROUP C
teams_C_East=["ATL","BOS","CLE","CHI","WAS"]

games_played_east_C=[Game("BOS","ATL", True, [116,117]),
                      Game("ATL","WAS", True, [129,117]),
                      Game("CLE","CHI", True, [144,126]),
                      Game("BOS","CLE", True, [120,117]),
                      Game("WAS","BOS", True, [96,108]),
                      Game("CHI","ATL", True, [136,122])]

games_to_play_east_C=[Game("WAS","CHI", False),
                      Game("ATL","CLE", False),
                      Game("CHI","BOS", False),
                      Game("CLE","WAS", False)]
group_east_C = Group("East", "C", [team_dic[team] for team in teams_C_East],
                     games_played_east_C, games_to_play_east_C, team_dic)


#WEST GROUP A

teams_A_West=["MIN","POR","LAC","HOU","SAC"]

games_played_A_West=[Game("POR","MIN", True, [122,108]),
                      Game("HOU","LAC", True, [125,104]),
                      Game("SAC","MIN", True, [126,130]),
                      Game("HOU","POR", True, [116,88]),
                      Game("LAC","SAC", True, [104,88])]

games_to_play_A_West=[Game("MIN","HOU", False),
                      Game("MIN","LAC", False),
                      Game("POR","SAC", False),
                      Game("SAC","HOU", False),
                      Game("LAC","POR", False)]
group_A_West = Group("West", "A", [team_dic[team] for team in teams_A_West],
                     games_played_A_West, games_to_play_A_West, team_dic)


#WEST GROUP B

teams_B_West=["LAL","SAS","OKC","PHX","UTA"]

games_played_B_West=[Game("UTA","PHX", True, [112,120]),
                      Game("SAS","LAL", True, [115,120]),
                      Game("OKC","PHX", True, [99,83]),
                      Game("SAS","OKC", True, [110,104]),
                      Game("LAL","UTA", True, [124,118])]

games_to_play_B_West=[Game("UTA","SAS", False),
                      Game("LAL","PHX", False),
                      Game("LAL","OKC", False),
                      Game("OKC","UTA", False),
                      Game("PHX","SAS", False)]
group_B_West = Group("West", "B", [team_dic[team] for team in teams_B_West],
                     games_played_B_West, games_to_play_B_West, team_dic)


#WEST GROUP C

teams_C_West=["DAL","GSW","DEN","NOP","MEM"]

games_played_C_West=[Game("GSW","DAL", True, [120,117]),
                      Game("NOP","DEN", True, [101,94]),
                      Game("GSW","MEM", True, [123,118]),
                      Game("MEM","DEN", True, [110,122]),
                      Game("DAL","NOP", True, [132,91]),
                      Game("NOP","GSW", True, [108,112]),
                      Game("DEN","DAL", True, [120,123])]

games_to_play_C_West=[Game("MEM","NOP", False),
                      Game("DAL","MEM", False),
                      Game("GSW","DEN", False)]
group_C_West = Group("West", "C", [team_dic[team] for team in teams_C_West],
                     games_played_C_West, games_to_play_C_West, team_dic)



#group_east_A.print_leaderboard()
#group_east_A.possibilities(group_east_A.games_to_play, "IF    ")      
#group_east_B.print_leaderboard()
#group_east_B.possibilities(group_east_B.games_to_play, "IF    ")  
#group_east_C.print_leaderboard()
#group_east_C.possibilities(group_east_C.games_to_play, "IF    ") 
#group_A_West.print_leaderboard()
#group_A_West.possibilities(group_A_West.games_to_play, "IF    ")
#group_B_West.print_leaderboard()
#group_B_West.possibilities(group_B_West.games_to_play, "IF    ")
#group_C_West.print_leaderboard()   
#group_C_West.possibilities(group_C_West.games_to_play, "IF    ")        


teamsEast=teams_A_East + teams_B_East + teams_C_East
group_EAST= Group("EAST","",[team_dic[team] for team in teamsEast],[],[],
                  team_dic)
group_EAST.print_leaderboard()  

teamsWest=teams_A_West + teams_B_West + teams_C_West
group_WEST= Group("WEST","",[team_dic[team] for team in teamsWest],[],[],
                  team_dic)
group_WEST.print_leaderboard() 