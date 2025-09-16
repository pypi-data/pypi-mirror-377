from .config import *
from datetime import timedelta
import json
import numpy as np
import queue as q
import os
import time
import curses


def key_display(keys:list)->str:
    symbols = []
    for k in keys:
        if k == 27:
            symbols.append("Esc")
        elif k == curses.KEY_UP:
            symbols.append("↑")
        elif k == curses.KEY_DOWN:
            symbols.append("↓")
        elif k == curses.KEY_LEFT:
            symbols.append("←")
        elif k == curses.KEY_RIGHT:
            symbols.append("→")
        elif 0 <= k < 256:
            symbols.append(chr(k).upper())
        else:
            symbols.append(str(k))
    str = "'/'".join(symbols)
    return f"'{str}'"

def setup_color(has_color:bool)->None:
    if not(has_color):
        return
    curses.start_color()
    curses.init_pair(1,curses.COLOR_BLACK,curses.COLOR_WHITE)
    curses.init_pair(2,curses.COLOR_GREEN,curses.COLOR_BLACK)
    curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK)
    curses.init_pair(4,curses.COLOR_BLUE,curses.COLOR_BLACK)
    curses.init_pair(5,curses.COLOR_YELLOW,curses.COLOR_BLACK)
    curses.init_pair(6,curses.COLOR_CYAN,curses.COLOR_BLACK)
    curses.init_pair(7,curses.COLOR_BLACK,curses.COLOR_GREEN)
    curses.init_pair(8,curses.COLOR_WHITE,curses.COLOR_RED)
    curses.init_pair(9,curses.COLOR_WHITE,curses.COLOR_BLUE)
    curses.init_pair(10,curses.COLOR_BLACK,curses.COLOR_YELLOW)
    curses.init_pair(11,curses.COLOR_WHITE,curses.COLOR_MAGENTA)

def level_name(level:int)->str:
    return levels[level]

def power_func(power_int:int,mat:np.ndarray,snake_queue:q.Queue,snake_set:set,level:int,frame_duration:list,score:list,highest_score:list)->None:
    if power_int==0:
        frame_duration[0]+=final_frame_duration[level]-initial_frame_duration[level]
    elif power_int==1:
        frame_duration[0]+=initial_frame_duration[level]-final_frame_duration[level]
    elif power_int==2:
        for i in range(powerup_snake_reduce_size):
            if snake_size(snake_set)>min_snake_len:
                snake_tail_loc=snake_queue.get()
                snake_set.discard(snake_tail_loc)
                mat[snake_tail_loc]=land
    elif power_int==3:
        score[0]+=5
        if score[0]>highest_score[0]:
            highest_score[0]=score[0]
    elif power_int==4:
        score[0]-=3

def snake_move(mat:np.ndarray,direction:str,snake_queue:q.Queue,snake_head_loc:tuple,snake_set:set,food_loc:tuple,score:list,highest_score:list,power_spawn_flag:list,power_loc:list,frame_duration:list,level:int,power_int:int,power_start_time:float)->tuple:
    snake_queue.put(snake_head_loc)
    mat[snake_head_loc]=snake
    if(direction=="right"):
        snake_head_loc=(snake_head_loc[0],(snake_head_loc[1]+1)%cols)
    elif(direction=="left"):
        snake_head_loc=(snake_head_loc[0],(snake_head_loc[1]-1)%cols)
    elif(direction=="top"):
        snake_head_loc=((snake_head_loc[0]-1)%rows,snake_head_loc[1])
    else:
        snake_head_loc=((snake_head_loc[0]+1)%rows,snake_head_loc[1])
    mat[snake_head_loc]=snake_head

    snake_set.add(snake_head_loc)

    if (snake_head_loc==food_loc[0]):
        food_loc[0]=food_loc_generate(snake_set,power_loc)
        mat[food_loc[0]]=food
        score[0]+=1
        if score[0]>highest_score[0]:
            highest_score[0]=score[0]
        power_spawn_flag[0]=1
        frame_duration=change_velocity(frame_duration,level,score)
        return snake_head_loc
    elif (snake_head_loc==power_loc[0]):
        power_func(power_int,mat,snake_queue,snake_set,level,frame_duration,score,highest_score)
        power_loc[0]=None
        if power_int in (0,1):
            power_start_time[0]=time.time()
        return snake_head_loc
    else:
        snake_tail_loc=snake_queue.get()
        snake_set.discard(snake_tail_loc)
        mat[snake_tail_loc]=land
        return snake_head_loc

def check_lose(direction:str,snake_head_loc:tuple,snake_set:set)->bool:
    if(direction=="right"):
        if (snake_head_loc[0],(snake_head_loc[1]+1)%cols) in snake_set:
            return 1
        else:
            return 0
    elif(direction=="left"):
        if (snake_head_loc[0],(snake_head_loc[1]-1)%cols) in snake_set:
            return 1
        else:
            return 0
    elif(direction=="top"):
        if ((snake_head_loc[0]-1)%rows,snake_head_loc[1]) in snake_set:
            return 1
        else:
            return 0
    else:
        if ((snake_head_loc[0]+1)%rows,snake_head_loc[1]) in snake_set:
            return 1
        else:
            return 0

def snake_size(snake_set:set)->int:
    return len(snake_set)

def time_elapsed(time:timedelta)->str:
    seconds=time.total_seconds()
    minutes=int(seconds/60)
    hours=int(minutes/60)
    days=int(hours/24)
    hours%=24
    minutes%=60
    seconds%=60
    s=""
    if(days):
        s+=f"{days} Days "
    if(hours):
        s+=f"{hours} Hours "
    if(minutes):
        s+=f"{minutes} Minutes "
    if(seconds):
        s+=f"{seconds:.0f} Seconds"
    return s

def format_cell(content:object)->str:
    return f"{content} "

def color(tile_symbol:object)->int:
    if(tile_symbol==land):
        return 2
    elif(tile_symbol==snake_head):
        return 4
    elif(tile_symbol==food):
        return 3
    elif(tile_symbol==powers_symbol[0]):
        return 7
    elif(tile_symbol==powers_symbol[1]):
        return 8
    elif(tile_symbol==powers_symbol[2]):
        return 11
    elif(tile_symbol==powers_symbol[3]):
        return 9
    elif(tile_symbol==powers_symbol[4]):
        return 10
    else:
        return 6
    
def power_loc_generate(snake_set:set,food_loc:list)->tuple:
    invalid_loc=snake_set.copy()
    invalid_loc.add(food_loc[0])
    loc=np.random.choice(rows*cols,1,replace=False)
    i=int(loc[0])
    while((i//cols,i%cols) in invalid_loc):
        loc=np.random.choice(rows*cols,1,replace=False)
        i=int(loc[0])
    return (i//cols,i%cols)

def food_loc_generate(snake_set:set,power_loc:list)->tuple:
    if (power_loc[0]!=None):
        invalid_loc=snake_set.copy()
        invalid_loc.add(power_loc[0])
        loc=np.random.choice(rows*cols,1,replace=False)
        i=int(loc[0])
        while((i//cols,i%cols) in invalid_loc):
            loc=np.random.choice(rows*cols,1,replace=False)
            i=int(loc[0])
        return (i//cols,i%cols)
    else:
        loc=np.random.choice(rows*cols,1,replace=False)
        i=int(loc[0])
        while((i//cols,i%cols) in snake_set):
            loc=np.random.choice(rows*cols,1,replace=False)
            i=int(loc[0])
        return (i//cols,i%cols)

def change_velocity(frame_duration:list,level:int,score:list)->list:
    # smooth exponential decay
    k = 0.05
    decay = initial_frame_duration[level]*(0.9**(k*score[0]))
    frame_duration[0]=max(final_frame_duration[0],int(decay))

    return frame_duration

def log_game(game_state:dict)->None:
    log_file_path=os.path.join(log_folder,log_file)
    with open(log_file_path,"a") as f:
        json.dump(game_state,f)
        f.write("\n")

def high_score(level:int)->int:
    score_file_path=os.path.join(log_folder,score_file)
    if not(os.path.exists(score_file_path)):
        return 0
    else:
        with open(score_file_path,"r") as f:
            data=json.load(f)
            return data[level]['Score']

def score_update(game_state:dict,level:int)->None:
    score_file_path=os.path.join(log_folder,score_file)
    data=[]
    if not(os.path.exists(score_file_path)):
        for i in range(len(levels)):
            if i!=level:
                game_state_others={
                    'Level': level_name(i),
                    'Starting time': "00/00/0000 00:00:00",
                    'Time taken': "0 seconds",
                    'Score': 0
                }
                data.append(game_state_others)
            else:
                data.append(game_state)
        with open(score_file_path,'w') as f:
            json.dump(data,f,indent=3)
    else:
        with open(score_file_path,"r") as f:
            data_prev=json.load(f)
        for i in range(len(levels)):
            if i==level:
                data.append(game_state)
            else:
                data.append(data_prev[i])
        with open(score_file_path,'w') as f:
            json.dump(data,f,indent=3)
