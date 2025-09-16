import os
import appdirs

user_data_dir = appdirs.user_data_dir("SnakeGame",appauthor="Snake")
os.makedirs(user_data_dir, exist_ok=True)

#game config
# change number of rows and columns here note try not to make them greater than 20 and less than 10
rows=15
cols=30

#note 
# level==0 ==>easy
# level==1 ==>medium
# level==2 ==>hard

#in ms
initial_frame_duration=[300,250,200]
final_frame_duration=[180,160,140]
power_time_up=[10,8,5] #in seconds

#game matrix config 
Cell_Width=2

#gamesymbols
food = '◉'        # Food circle
snake =  '●'       # Snake body block
snake_head = '■'   # Snake head
land = '·'         # Empty land cell

#powers
powers=['Speed_Up','Speed_Down','Snake_reduce','Score_Up','Score_Down']
powers_symbol=['▲','▼','×','+','-']
powerup_speed_change_time=10 #in seconds
powerup_snake_reduce_size=10
min_snake_len=3

#levels
levels=['Easy','Medium','Hard']

#log config
log_folder=os.path.join(user_data_dir,"logs")
log_file="app.jsonl" #stores app logs
score_file="score.json" #stores high score

#key config
key_config_path=os.path.join(user_data_dir,"key_config.json")