import numpy as np
import curses
import sys
from datetime import datetime,timedelta
import time
import pyfiglet
import os
from .config import *
from .utils import snake_size, time_elapsed, format_cell, color, food_loc_generate, log_game, high_score, score_update, check_lose, snake_move, level_name, power_loc_generate, power_func, setup_color, key_display
import queue as q 
from .key_config import load_key_config, KEY_BINDINGS
import traceback
import argparse


def draw_pause(stdscr:any,duration:timedelta,score:list, has_color:bool, level:int)->None:
    stdscr.clear()

    figlet_text=pyfiglet.figlet_format("Snake")
    stdscr.addstr(0,0,figlet_text,curses.color_pair(4) if has_color else 0)
    stdscr.addstr(9,0,f"Time taken: {time_elapsed(duration)}")
    stdscr.addstr(10,0,f"Score: {score[0]}    Level: {level_name(level)}")
    stdscr.addstr(12,0,f"Press {key_display(KEY_BINDINGS['pause'])} to play",curses.color_pair(3) if has_color else 0)
    stdscr.addstr(13,0,f"Press {key_display(KEY_BINDINGS['instructions'])} for instructions and {key_display(KEY_BINDINGS['quit'])}/'Esc' to exit to main menu",curses.color_pair(3) if has_color else 0)

    pause_window = stdscr.derwin(rows+2,cols*Cell_Width+1,15,5)
    pause_window.box()
    pause_window.addstr(rows//2+1,(cols//2)*Cell_Width-5,"Game Paused",curses.color_pair(2) if has_color else 0)

    pause_window.refresh()
    stdscr.refresh()

def draw_final(stdscr:any,score:list,duration:timedelta,state:int,has_color:bool,level:int)->None:
    stdscr.clear()

    figlet_text=pyfiglet.figlet_format("Snake")
    stdscr.addstr(0,0,figlet_text,curses.color_pair(4) if has_color else 0)
    stdscr.addstr(9,0,f"Time taken: {time_elapsed(duration)}")
    stdscr.addstr(10,0,f"Score: {score[0]}    Level: {level_name(level)}")
    if(state==-1):
        stdscr.addstr(12,0,"You were doing great, shouldn't have left like this")
    stdscr.refresh()

def draw_game(stdscr:any, mat:np.ndarray, duration:timedelta, score:list, highest_score:list, has_color:bool, level:int)->None:
    stdscr.clear()

    figlet_text=pyfiglet.figlet_format("Snake")
    stdscr.addstr(0,0,figlet_text,curses.color_pair(4) if has_color else 0)
    stdscr.addstr(9,0,f"Duration: {time_elapsed(duration)}")
    stdscr.addstr(10,0,f"Score: {score[0]}  Level: {level_name(level)}  Highest Score: {highest_score[0]}")
    stdscr.addstr(11,0,f"Press {key_display(KEY_BINDINGS['pause'])} for pause and {key_display(KEY_BINDINGS['quit'])}/'Esc' to exit to main menu",curses.color_pair(3) if has_color else 0)
    stdscr.addstr(12,0,"Remember don't bite yourself")

    game_box = stdscr.derwin(rows+2,cols*Cell_Width+1,15,5)

    for r in range(rows):
        for c in range(cols):
            cell_str=format_cell(mat[r,c])
            y=r+1
            x=(c)*Cell_Width+1
            game_box.addstr(y,x,cell_str,curses.color_pair(color(mat[r,c])) if has_color else 0)
    
    game_box.box()
    stdscr.refresh()
    game_box.refresh()

def draw_instructions(stdscr:any,has_color:bool)->None:
    stdscr.clear()

    figlet_text=pyfiglet.figlet_format("Snake")
    stdscr.addstr(0,0,figlet_text,curses.color_pair(4) if has_color else 0) 

    stdscr.addstr(9,0,f"Press {key_display(KEY_BINDINGS['instructions'])} for instructions")
    stdscr.addstr(10,0,f"Press {key_display(KEY_BINDINGS['quit'])}/'Esc' for exiting")
    stdscr.addstr(11,0,f"Press {key_display(KEY_BINDINGS['pause'])} to play/pause")
    stdscr.addstr(12,0,f"Press {key_display(KEY_BINDINGS['up'])}/{key_display(KEY_BINDINGS['down'])} to choose level and 'Enter' to select level")
    stdscr.addstr(13,0,f"Press {key_display(KEY_BINDINGS['left'])}/{key_display(KEY_BINDINGS['right'])} to move snake")
    stdscr.addstr(14,0,f"'{powers_symbol[0]}' == {powers[0]}", curses.color_pair(color(powers_symbol[0])) if has_color else 0)
    stdscr.addstr(15,0,f"'{powers_symbol[1]}' == {powers[1]}", curses.color_pair(color(powers_symbol[1])) if has_color else 0)
    stdscr.addstr(16,0,f"'{powers_symbol[2]}' == {powers[2]}", curses.color_pair(color(powers_symbol[2])) if has_color else 0)
    stdscr.addstr(17,0,f"'{powers_symbol[3]}' == {powers[3]}", curses.color_pair(color(powers_symbol[3])) if has_color else 0)
    stdscr.addstr(18,0,f"'{powers_symbol[4]}' == {powers[4]}", curses.color_pair(color(powers_symbol[4])) if has_color else 0)

    stdscr.addstr(20,0,"NOTE:")
    stdscr.addstr(21,0,"Instruction's window is only accessed through pause state or via menu")

    stdscr.addstr(23,0,"Press any key to go back...",curses.color_pair(3) if has_color else 0)
    stdscr.refresh()
    stdscr.getch()


def draw_menu(stdscr:any,has_color:bool,level:int)->None:
    stdscr.clear()

    figlet_text=pyfiglet.figlet_format("Snake")
    stdscr.addstr(0,0,figlet_text,curses.color_pair(4) if has_color else 0)    
    stdscr.addstr(9,0,f"Press {key_display(KEY_BINDINGS['instructions'])} for instructions and {key_display(KEY_BINDINGS['quit'])}/'Esc' to exit",curses.color_pair(3) if has_color else 0)
    stdscr.addstr(12,0,"Choose Level:")

    for i in range(len(levels)):
        if(level==i):
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(i+13,2,level_name(i))
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(i+13,2,level_name(i))

    stdscr.refresh()

def main(stdscr:any)->None:

    curses.curs_set(0)
    has_color=curses.has_colors()
    setup_color(has_color)
    load_key_config()

    game_loop=1
    while(game_loop):

        level = 0
        menu_key=-1

        while(menu_key!=ord('\n')):
            draw_menu(stdscr,has_color,level)
            menu_key=stdscr.getch()
            if menu_key in [ord('\n')]:
                break
            elif menu_key in KEY_BINDINGS['instructions']:
                draw_instructions(stdscr,has_color)
            elif menu_key in KEY_BINDINGS['quit'] or menu_key==27:
                #######EXIT#######
                sys.exit(0)
            elif menu_key in KEY_BINDINGS['up']:
                level=(level-1)%3
            elif menu_key in KEY_BINDINGS['down']:
                level=(level+1)%3

        stdscr.nodelay(True)

        draw_menu(stdscr,has_color,level)

        highest_score=[high_score(level)]

        snake_set=set()
        snake_queue=q.Queue()
        snake_queue.put((rows//2,1))
        snake_queue.put((rows//2,2))
        snake_set.add((rows//2,1))
        snake_set.add((rows//2,2))

        mat=np.full((rows,cols),land,dtype=object)

        mat[rows//2,1]=snake
        mat[rows//2,2]=snake
        mat[rows//2,3]=snake_head

        snake_head_loc=(rows//2,3)
        snake_set.add(snake_head_loc)
        score=[0]
        state=1
        start_time=datetime.now()

        power_loc = [None]
        power_spawn_time=0
        power_start_time=[0]
        power_spawn_flag=[1]
        power_int=-1

        food_loc=[food_loc_generate(snake_set,power_loc)]
        mat[food_loc[0]]=food

        direction="right"
        frame_duration = [initial_frame_duration[level]]

        while(state):
            now_time=datetime.now()
            duration=now_time-start_time

            direction_list=["top","right","bottom","left"]

            key=-1
            # Wait for frame duration, but check for keypresses during that time
            loop_start_time = time.time()
            while (time.time() - loop_start_time) * 1000 < frame_duration[0]:
                k = stdscr.getch()
                if k != -1:
                    key = k  # keep only the latest valid keypress
                curses.napms(10) 
            
            if key in KEY_BINDINGS['left']:
                direction=direction_list[(direction_list.index(direction)-1)%4]
            elif key in KEY_BINDINGS['right']:
                direction=direction_list[(direction_list.index(direction)+1)%4]
            elif key in KEY_BINDINGS['quit']:
                state=-1
                break
            elif key in KEY_BINDINGS['pause']:
                exit_flag=0
                draw_pause(stdscr,duration,score,has_color,level)
                pause_key=0
                stdscr.nodelay(False)
                while(pause_key not in KEY_BINDINGS['pause'] or pause_key not in KEY_BINDINGS['quit']):
                    pause_key=stdscr.getch()
                    if pause_key in KEY_BINDINGS['pause']:
                        break
                    elif pause_key in KEY_BINDINGS['quit']:
                        state=-1
                        exit_flag=1
                        break 
                    elif pause_key in KEY_BINDINGS['instructions']:
                        draw_instructions(stdscr,has_color)
                        draw_pause(stdscr,duration,score,has_color,level)
                stdscr.nodelay(True)
                if exit_flag:
                    break
            else:
                pass

            if not(check_lose(direction,snake_head_loc,snake_set)):
                snake_head_loc = snake_move(mat,direction,snake_queue,snake_head_loc,snake_set,food_loc,score, highest_score, power_spawn_flag,power_loc,frame_duration,level,power_int,power_start_time)
            else:
                state=0

            if snake_size(snake_set)==rows*cols:
                state=2 #when game_finishes after all blocks covered
                break
            
            draw_game(stdscr, mat, duration, score, highest_score,has_color,level)

            if (score[0]%10==5 and power_spawn_flag[0]):
                power_loc[0]=power_loc_generate(snake_set,food_loc)
                power_int=int(np.random.choice(len(powers),1,replace=False)[0])
                mat[power_loc[0]]=powers_symbol[power_int]
                power_spawn_flag[0]=0
                power_spawn_time=time.time()

            if ((time.time()-power_spawn_time) >= power_time_up[level]) and (power_loc[0]!=None):
                mat[power_loc[0]]=land
                power_loc[0]=None
                power_int=-1

            if power_int in (0,1) and power_start_time[0]!=0:
                if ((time.time()-power_start_time[0]) >= powerup_speed_change_time):
                    power_func(1-power_int,mat,snake_queue,snake_set,level,frame_duration,score)
                    power_start_time[0]=0
                    power_int=-1
                    power_loc[0]=None


        stdscr.nodelay(False)
        draw_final(stdscr,score,duration,state,has_color,level)

        game_state={
            'Level': level_name(level),
            'Starting time': start_time.strftime("%d/%m/%Y, %H:%M:%S"),
            'Time taken' : time_elapsed(duration),
            'Score' : score[0]
        }

        if not(os.path.exists(log_folder)):
            os.makedirs(log_folder)
        log_game(game_state)

        if(state==2):
            stdscr.addstr(13,0,"Congratulations! Well somehow you have mansged to cover the whole field")
        
        highest_score=[high_score(level)]

        if (highest_score[0]<score[0]):
            if highest_score[0]:
                stdscr.addstr(14,0,f"Congratulations! You just broke the highest record of {highest_score[0]}")
            else:
                stdscr.addstr(14,0,f"Congratulations! You just setup the highest record of {score[0]} for the first time")
            score_update(game_state,level)
        else:
            stdscr.addstr(14,0,f"Oooh! You missed to break the highest record of {highest_score[0]} by {highest_score[0]-score[0]}")
        
        stdscr.addstr(17,0,f"Press {key_display(KEY_BINDINGS['quit'])}/'Esc' to exit...")
        stdscr.addstr(18,0,"Press any other key to get to main menu")
        
        stdscr.refresh()
    
        game_key=-1
        while(game_key==-1):
            game_key=stdscr.getch()

        if game_key in KEY_BINDINGS['quit']:
            game_loop=0
        else:
            game_loop=1 

def run_game(debug_mode=False):
    try:
        curses.wrapper(main)
    except curses.error:
        print("Terminal size too small.")
        print("Try resizing or maximizing the terminal window and rerun the game.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Game exited via Ctrl+C.")
        sys.exit(0)
    except Exception as e:
        print("Unexpected error occurred:")
        print(f"{e}")
        # print(e)
        print("Try maximizing the terminal or checking your Python environment.")

        # logging traceback
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        with open(os.path.join(log_folder, "error_traceback.log"), "a") as f:
            f.write(traceback.format_exc())
            f.write("\n" + "=" * 60 + "\n")

        if debug_mode:
            print("[DEBUG MODE] Full Traceback:")
            print(traceback.format_exc())

        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snake Game")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with full tracebacks")
    args = parser.parse_args()

    run_game(debug_mode=args.debug)
