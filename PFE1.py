# Import packages
from psychopy import core, event, visual
import time, serial
import math
import random
import csv
import os

ports_live = None # Set to None if parallel ports not plugged for coding/debugging other parts of exp

### Experiment details/parameters
## equipment parameters
port_buffer_duration = 1000000 # microseconds, giving time to turn on and off trigs  
pain_response_duration = float("inf")
response_hold_duration = 1 # How long the rating screen is left on the response (only used for Pain ratings)
RENS_pulse_int = 0.1 # interval length for RENS on/off signals (e.g. 0.1 = 0.2s per pulse)

# serial port triggers
if ports_live == True:
    s = serial.Serial('COM3', baudrate=128000, timeout=0.01)
    s.write(b'WRITE 0\n')    

elif ports_live == None:
    s = None #Get from device Manager

shock_levels = 10

shock_trig = {"high": 1, 
              "low": 11, 
              "medium": 21} #byte values start on lowest levels

rens_trig = 128

## within experiment parameters
experimentcode = "NC1"
P_info = {"PID": "",
        "SONA" : ""}
info_order = ["PID"]

# iti_range = [6,8]
trial_iti = 6
instruction_iti = 3

rating_scale_pos = (0,-350)
rating_text_pos = (0,-250) 
text_height = 30 
textStim_arguments = {'height':30,
                      'color': "white",
                      'wrapWidth': 960}

RENS_image_size = (400,300)
RENS_image_pos = (0,200)
RENS_text_pos = (0,300)

context_image_size = (1920, 1080)
context_image_pos = (0,0)

timer_precision_range = 0.015 # pulses should be accurate to within 10 milliseconds

midtrial_rating_list = ["anxiety","expectancy"]

# within experiment parameters
P_info = {"PID": ""}
info_order = ["PID"]

# Participant info input
while True:
    try:
        P_info["PID"] = input("Enter participant ID: ")
        if not P_info["PID"]:
            print("Participant ID cannot be empty.")
            continue
            
        csv_filename = P_info["PID"] + "_responses.csv"
        script_directory = os.path.dirname(os.path.abspath(__file__))  #Set the working directory to the folder the Python code is opened from
        
        #set a path to a "data" folder to save data in
        data_folder = os.path.join(script_directory, "data")

        #set stimuli folder path

        stimulus_folder =  os.path.join(script_directory, "stimuli")
        
        # if data folder doesn"t exist, create one
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        #set file name within "data" folder
        csv_filepath = os.path.join(data_folder,csv_filename)
        
        if os.path.exists(csv_filepath):
            print(f"Data for participant {P_info['PID']} already exists. Choose a different participant ID.") ### to avoid re-writing existing data
            
        else:
            cb = int(P_info["PID"]) % 16
            

            
            break  # Exit the loop if the participant ID is valid
    except KeyboardInterrupt:
        print("Participant info input canceled.")
        break  # Exit the loop if the participant info input is canceled

    # get date and time of experiment start
datetime = time.strftime("%Y-%m-%d_%H.%M.%S")

# set up screen
exp_win = visual.Window(
    size=(1920, 1080), fullscr=True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor="testMonitor", color=[0, 0, 0], colorSpace="rgb1",
    blendMode="avg", useFBO=True,
    units="pix")

mouse = event.Mouse(visible=True)

# fixation stimulus
fix_stim = visual.TextStim(exp_win,
                            text = "x",
                            color = "white",
                            height = 50,
                            font = "Roboto Mono Medium")

#load in RENS graphics
RENS_names = ["monopolar", "bipolar"]

RENS_pulse_pattern_names = {
    "monopolar": "constant",
    "bipolar": "pause"
}
RENS_cb = {"N" : (cb // 8) % 2,
           "M" : (cb // 8) % 2 - 1,
           }

RENS_pulse_pattern_images = {"monopolar": visual.ImageStim(exp_win,
                                    image=os.path.join(stimulus_folder, RENS_pulse_pattern_names["monopolar"]+".png"),
                                    size = RENS_image_size,
                                    pos = RENS_image_pos
                                    ),
                            "bipolar": visual.ImageStim(exp_win,
                                    image=os.path.join(stimulus_folder, RENS_pulse_pattern_names["bipolar"]+".png"),
                                    size = RENS_image_size,
                                    pos = RENS_image_pos
                            ),
}

RENS_pulse_pattern_trig_list = {"pause": [(0.0, rens_trig), # 3 rapid pulses followed by pause, first number specifies time in seconds, second number port send value
                                 (0.2, rens_trig),
                                 (0.4, rens_trig)],
                                "constant": [(0.0, rens_trig),
                                (0.333, rens_trig),
                                (0.666, rens_trig)], # constant equally spaced pulses 
}

RENS_pulse_pattern_text = {
    name: visual.TextStim(
        exp_win,
        text=f"You are receiving {name} RENS",
        height=35,
        color="white",
        pos=RENS_text_pos,
        wrapWidth=960
    )
    for name in RENS_names
}
context_trial_list = ["C","X","F","G"]
context_image_names = {
    context_trial_list[cb % 4]: "field",
    context_trial_list[(cb % 4) - 1]: "mountain",
    context_trial_list[(cb % 4) - 2]: "forest",
    context_trial_list[(cb % 4) - 3]: "beach"
}

context_images = {"C": visual.ImageStim(exp_win,
                                    image=os.path.join(stimulus_folder, context_image_names["C"]+".jpg"),
                                    size = context_image_size,
                                    pos = context_image_pos
                                    ),
                "X": visual.ImageStim(exp_win,
                                    image=os.path.join(stimulus_folder, context_image_names["X"]+".jpg"),
                                    size = context_image_size,
                                    pos = context_image_pos
                                        ),
                "F": visual.ImageStim(exp_win,
                                    image=os.path.join(stimulus_folder, context_image_names["F"]+".jpg"),
                                    size = context_image_size,
                                    pos = context_image_pos
                                        ),
                "G": visual.ImageStim(exp_win,
                                    image=os.path.join(stimulus_folder, context_image_names["G"]+".jpg"),
                                    size = context_image_size,
                                    pos = context_image_pos
                                        ),
                }

#define waiting function so experiment doesn't freeze as it does with core.wait()
def wait(time):
    countdown_timer = core.CountdownTimer(time)
    while countdown_timer.getTime() > 0:
        termination_check()
        
#create instruction trials
def instruction_trial(instructions,holdtime): 
    termination_check()
    visual.TextStim(exp_win,
                    text = instructions,
                    height = 35,
                    color = "white",
                    pos = (0,0),
                    wrapWidth= 960
                    ).draw()
    exp_win.flip()
    wait(holdtime)
    visual.TextStim(exp_win,
                    text = instructions,
                    height = 35,
                    color = "white",
                    pos = (0,0),
                    wrapWidth= 960
                    ).draw()
    visual.TextStim(exp_win,
                    text = instructions_text["continue"],
                    height = 35,
                    color = "white",
                    pos = (0,-400)
                    ).draw()
    exp_win.flip()
    event.waitKeys(keyList=["space"])
    exp_win.flip()
    
    wait(instruction_iti)
    
# Create functions
    # Save responses to a CSV file
def save_data(data):
    for trial in trial_order:
        trial['datetime'] = datetime
        trial["PID"] = P_info["PID"]
        trial["cb"] = cb
        trial["shock_calib_level"] = shock_trig["high"]

    # Extract column names from the keys in the first trial dictionary
    colnames = list(trial_order[0].keys())

    # Open the CSV file for writing
    with open(csv_filepath, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=colnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each trial"s data to the CSV file
        for trial in data:
            writer.writerow(trial)
    
def exit_screen(instructions):
    exp_win.flip()
    visual.TextStim(exp_win,
            text = instructions,
            height = 35,
            color = "white",
            pos = (0,0)).draw()
    exp_win.flip()
    event.waitKeys()
    exp_win.close()
    
def termination_check(): #insert throughout experiment so participants can end at any point.
    keys_pressed = event.getKeys(keyList=["escape"])  # Check for "escape" key during countdown
    if "escape" in keys_pressed:
        if ports_live:
            s.write(b'WRITE 0\n')  # Set all pins to 0 to shut off RENS, shock etc.
        # Save participant information

        save_data(trial_order)
        exit_screen(instructions_text["termination"])
        core.quit()
        
# Define trials
# Setting conditioning trial order
# Number of trials
trial_order = []

#### 4 x blocks (2 RENS + low shock, 2 control + high shock)
num_blocks_calibration = 1
num_blocks_conditioning = 9
num_blocks_extinction = 9
num_blocks_test = 6
num_trials_block = {
        "calibration": {
            "calibration": {
                "num":10,
                "stimulus": None,
                "trialtype": "calibration",
                "outcome": "high",
                "context": None,
                }
            },
        "conditioning": {
            "N": {
                "num":1,
                "stimulus": RENS_names[RENS_cb["N"]],
                "trialtype": RENS_names[RENS_cb["N"]],
                "outcome": "high",
                "context": None,
            },
            "M": {
                "num":1,
                "stimulus": RENS_names[RENS_cb["M"]],
                "trialtype": RENS_names[RENS_cb["M"]],
                "outcome": "high",
                "context": None, 
            },
            "C": {
                "num":1,
                "stimulus": None,
                "trialtype": "control",
                "outcome": "med",
                "context": "C", 
            },
            "F": {
                "num":1,
                "stimulus": None,
                "trialtype": "control",
                "outcome": "high",
                "context": "F", 
            },
        },
        "extinction": {
            "N": {
                "num":1,
                "stimulus": RENS_names[RENS_cb["N"]],
                "trialtype": RENS_names[RENS_cb["N"]],
                "outcome": "med",
                "context": "X",
            },
            "M": {
                "num":1,
                "stimulus": RENS_names[RENS_cb["M"]],
                "trialtype": RENS_names[RENS_cb["M"]],
                "outcome": "med",
                "context": None, 
            },
            "C": {
                "num":1,
                "stimulus": None,
                "trialtype": "control",
                "outcome": "med",
                "context": "C", 
            },
            "F": {
                "num":1,
                "stimulus": None,
                "trialtype": "control",
                "outcome": "med",
                "context": "F", 
            },
            "G": {
                "num":1,
                "stimulus": None,
                "trialtype": "control",
                "outcome": "high",
                "context": "G", 
            },
        },
        "test": {
            "N": {
                "num":1,
                "stimulus": RENS_names[RENS_cb["N"]],
                "trialtype": RENS_names[RENS_cb["N"]],
                "outcome": "med",
                "context": None,
            },
            "M": {
                "num":1,
                "stimulus": RENS_names[RENS_cb["M"]],
                "trialtype": RENS_names[RENS_cb["M"]],
                "outcome": "med",
                "context": None, 
            },
            "X": {
                "num":1,
                "stimulus": None,
                "trialtype": "control",
                "outcome": "med",
                "context": "X", 
            },
            "C": {
                "num":1,
                "stimulus": None,
                "trialtype": "control",
                "outcome": "med",
                "context": "C", 
            },
            "F": {
                "num":1,
                "stimulus": None,
                "trialtype": "control",
                "outcome": "med",
                "context": "F", 
            },
            "G": {
                "num":1,
                "stimulus": None,
                "trialtype": "control",
                "outcome": "med",
                "context": "G", 
            },
        }
}

for phase, trials in num_trials_block.items():
    num_blocks = {
        "calibration": num_blocks_calibration,
        "conditioning": num_blocks_conditioning,
        "extinction": num_blocks_extinction,
        "test": num_blocks_test,
    }[phase]
    
    for block in range(num_blocks):
        temp_trial_order = []

        for trial_name, trial_info in trials.items():
            for num in range(trial_info["num"]):
                trial = {
                    "phase": phase,
                    "trialname": trial_name,
                    "trialtype": trial_info["trialtype"],
                    "stimulus": trial_info["stimulus"],
                    "context": trial_info["context"],
                    "context_stim": context_image_names.get(trial_info["context"]),
                    "outcome": trial_info["outcome"],
                    "expectancy_response": None,
                    "anxiety_response": None,
                    "pain_response": None
                }
                trial["blocknum"] = block + 1
                    
                temp_trial_order.append(trial)

        random.shuffle(temp_trial_order)
        trial_order.extend(temp_trial_order)
    
# Assign trial numbers
for trialnum, trial in enumerate(trial_order, start=1):
    trial["trialnum"] = trialnum
    
#Test questions
# #Test questions
# Rating stim details
rating_list = {
    "calibration": {
        "pos": (0, -200),
        "ticks": [0, 50, 100],
        "labels": (1, 5, 10),
    },
    "pain": {
        "pos": rating_scale_pos,
        "ticks": [0, 100],
        "labels": ("Not painful", "Very painful"),
    },
    "expectancy": {
        "pos": rating_scale_pos,
        "ticks": [0, 100],
        "labels": ("Not painful", "Very painful"),
    },
    "anxiety": {
        "pos": rating_scale_pos,
        "ticks": [0, 100],
        "labels": ("Not at all", "Very anxious"),
    },
}

rating_stim = {
    name: visual.Slider(
        exp_win,
        pos=spec["pos"],
        ticks=spec["ticks"],
        labels=spec["labels"],
        granularity=0.1,
        size=(600, 60),
        style=["rating"],
        autoLog=False,
        labelHeight=30,
    )
    for name, spec in rating_list.items()
}

for slider in rating_stim.values():
    slider.marker.size = (30, 30)
    slider.marker.color = "yellow"
    slider.validArea.size = (660, 100)


# text stimuli
instructions_text = {
    "welcome": "Welcome to the experiment! Please read the following instructions carefully.", 
    "RENS_introduction": "This experiment aims to investigate the effects of Repetitive Electrical Nerve Stimulation (RENS) and imagery on pain sensitivity. Different frequencies of RENS and types of imagery have been shown to alter pain perception. \n\n"
        "The RENS itself is not painful, but you will feel a small sensation when it is turned on. Today we are testing the effects of monopolar and bipolar frequencies. You will also be shown a number of different images during the experiment",
    "calibration" : "Firstly, we are going to calibrate the pain intensity for the shocks you will receive in the experiment without RENS or imagery. As this is a study about pain, we want you to feel a moderate bit of pain, but nothing unbearable. "
        "The machine will start low, and then will gradually work up. We want to get to a level which is painful but tolerable, so roughly at a rating of around 7 out of 10, where 1 is not painful and 10 is very painful. \n\n"
        "Note that participants must be able to tolerate at least the third level of shock intensity to be eligible for this experiment.\n\n"
        "After reaching the minimum level of shock you will be given the option to increase the intensity or set the current shock level for the experiment.\n\n"
        "Please ask the experimenter if you have any questions at anytime. ",
    "calibration_finish": "Thank you for completing the calibration, your maximum shock intensity has now been set.",
    "experiment":  "We can now begin the experiment. \n\n"
        "You will now receive a series of shocks and your task is to rate the intensity of the pain caused by each shock on a rating scale. "
        "This rating scale ranges from NOT PAINFUL to VERY PAINFUL. \n\n"
        "All shocks will be signaled by a 10 second countdown. The shocks will occur when an X appears. "
        "On RENS trials, you will be receiving monopolar or bipolar frequencies of RENS. This will activate during the countdown. On imagery trials, you will also see specific images. This will appear during the countdown. "
        "As you are waiting for the shock during the countdown, you will be asked to rate your expectancy or anxiety. After each trial there will be a brief interval to allow you to rest between shocks. \n\n"
        "Please ask the experimenter if you have any questions now before proceeding.",

    "continue" : "\n\nPress spacebar to continue",
    
    "end" : "This concludes the experiment. Please ask the experimenter to help remove the devices.",
    
    "termination" : "The experiment has been terminated. Please ask the experimenter to help remove the devices."
}

response_instructions = {
    "pain": "How painful was the shock?",
    "expectancy": "How painful do you EXPECT the next shock to be?",
    "anxiety": "How ANXIOUS are you about the next shock?",
    "shock": "Press spacebar to activate the shock",
    "shock_check": "Would you like to try the previous level of shock again?",
    "Check_>3": "Please select whether you would like to try the next level of shock, stay at this level, or go back to the previous level for the experiment.",
    "Check_=3": "This is the minimum level of shock.\n\n"
    "Please select whether you would like to try the next level of shock or stay at this level",
    "Check_max": "This is the maximum level of shock.\n\n"
        "Would you like to stay at this level or go down a level?"
                         }

# Rating instruction text
rating_text_list = {
    "pain": "pain",
    "expectancy": "expectancy",
    "anxiety": "anxiety",
}

rating_text = {
    name: visual.TextStim(
        exp_win,
        text=response_instructions[instruction],
        height=35,
        pos=(0, -100),
    )
    for name, instruction in rating_text_list.items()
}

# Define button_text and buttons dictionaries
# Button specifications
button_specs = {
    "calibration": {
        "Next": {
            "text": "Try the next shock level",
            "pos": (400, -300),
        },
        "Stay": {
            "text": "Stay at this shock level",
            "pos": (0, -300),
        },
        "Previous": {
            "text": "Set the previous shock level",
            "pos": (-400, -300),
        },
    },
    "confirm": {
        "Yes": {
            "text": "Yes",
            "pos": (400, -300),
        },
        "No": {
            "text": "No",
            "pos": (-400, -300),
        },
    },
}


# Create button text
button_text_list = {
    group: {
        button: visual.TextStim(
            exp_win,
            text=spec["text"],
            color="white",
            height=25,
            pos=spec["pos"],
            wrapWidth=300,
        )
        for button, spec in button_type.items()
    }
    for group, button_type in button_specs.items()
}

# Create button rectangles
button_rect_list = {
    group: {
        button: visual.Rect(
            exp_win,
            width=300,
            height=80,
            fillColor="black",
            lineColor="white",
            pos=spec["pos"],
        )
        for button, spec in button_type.items()
    }
    for group, button_type in button_specs.items()
}

# pre-draw countdown stimuli (numbers 10-1)
countdown_text = {}
for i in range(0,11):
    countdown_text[str(i)] = visual.TextStim(exp_win, 
                            color="white", 
                            height = 50,
                            text=str(i))

#### Make trial functions

calib_finish = False

    # calibration trials
def show_calib_trial(trial_order):
    trial_index = 0
    global calib_finish
    previous_trial = False
    termination_check()

    while 0 <= trial_index < len(trial_order) and not calib_finish:
        current_trial = trial_order[trial_index]
        #if participant selected to move down level, offer to receive shock again or to confirm level
        if previous_trial == True:
            termination_check()
            visual.TextStim(exp_win,
                text=response_instructions["shock_check"],
                height = 35,
                pos = (0,0),
                wrapWidth= 800
                ).draw()
            
            buttons_keylist = button_rect_list["confirm"].keys()
            for button_name in buttons_keylist:
                button_rect_list["confirm"][button_name].draw()
                button_text_list["confirm"][button_name].draw()
            exp_win.flip()

            #wait for mouse click
            choice_finish = False
            mouse.clickReset()  
            
            while choice_finish == False:
                for button_name, button_rect in button_rect_list["confirm"].items():
                    termination_check()
                    if mouse.isPressedIn(button_rect):
                        if button_name == "Yes":
                            choice_finish = True
                            previous_trial = False
                            exp_win.flip()
                            break
                        elif button_name == "No":
                            choice_finish = True
                            calib_finish = True
                            previous_trial = False
                            exp_win.flip()
                            wait(instruction_iti)
                            return
                            
            mouse.clickReset()  
            exp_win.flip()
            wait(instruction_iti)
            
        # show fixation stimulus and deliver shock    
        visual.TextStim(exp_win,
            text=response_instructions["shock"],
            height = 35,
            pos = (0,0),
            wrapWidth= 800
            ).draw()
        
        exp_win.flip()
        event.waitKeys(keyList = ["space"])
    
        if s != None:
            s.write(b'WRITE 0\n') 

        fix_stim.draw()
        exp_win.flip()
        
        if s != None:
            s.write(('WRITE '+str(shock_trig["high"])+' '+str(port_buffer_duration)+' 0\n').encode('utf-8'))

        wait(1)
        
        # Get pain rating
        while rating_stim["calibration"].getRating() is None: # while mouse unclicked
            termination_check()
            rating_text["pain"].draw()
            rating_stim["calibration"].draw()
            exp_win.flip()
            
        pain_response_end_time = core.getTime() + response_hold_duration # amount of time for participants to adjust slider after making a response
        
        while core.getTime() < pain_response_end_time:
            termination_check()
            rating_text["pain"].draw()
            rating_stim["calibration"].draw()
            exp_win.flip()

        current_trial["pain_response"] = rating_stim["calibration"].getRating()
        rating_stim["calibration"].reset()
        exp_win.flip()
        wait(instruction_iti)

        # if shock level < 3, increase shock level and loop back to shock again
        if shock_trig["high"] < 3:
            shock_trig["high"] += 1
            shock_trig["low"] += 1
            shock_trig["medium"] += 1
            trial_index += 1    
        # give participants choice to navigate shock levels after reaching level 3 intensity
        elif shock_trig["high"] >= 3:
            if shock_trig["high"] == 3:
                text = response_instructions["Check_=3"]
            elif 3 < shock_trig["high"] < 10:
                text = response_instructions["Check_>3"]
            elif shock_trig["high"] == 10:
                text = response_instructions["Check_max"]

            visual.TextStim(exp_win, text=text, height=35, pos=(0, 0)).draw()

            # Draw buttons and text
            if shock_trig["high"] == 3:
                buttons_keylist = ["Next", "Stay"]
            elif 3 < shock_trig["high"] < 10:
                buttons_keylist = ["Previous","Next", "Stay"]
            elif shock_trig["high"] == 10:
                buttons_keylist = ["Previous", "Stay"]
            else:
                buttons_keylist = button_rect_list["calibration"].keys()

            for button_name in buttons_keylist:
                button_rect_list["calibration"][button_name].draw()
                button_text_list["calibration"][button_name].draw()

            exp_win.flip()
            
            # Wait for a mouse click
            trial_finish = False
            mouse.clickReset()
        
            while trial_finish == False:
                for button_name, button_rect in button_rect_list["calibration"].items():
                    termination_check()
                    if mouse.isPressedIn(button_rect):
                        if button_name == "Next":
                            shock_trig["high"] += 1
                            shock_trig["low"] += 1
                            shock_trig["medium"] += 1
                            trial_index += 1
                            
                        elif button_name == "Stay":
                            calib_finish = True
                            
                        elif button_name == "Previous":
                            shock_trig["high"] -= 1
                            shock_trig["low"] -= 1
                            shock_trig["medium"] -= 1
                            trial_index -= 1
                            previous_trial = True
        
                        trial_finish = True
                        mouse.clickReset()    
                        break                    
            exp_win.flip()
            wait(3)

            
def show_trial(current_trial,midtrial_rating):
    termination_check()
    if s != None:
        s.write(b'WRITE 0\n') 
        
    exp_win.flip()
    # Start countdown to shock
    # Make a count-down screen
    countdown_timer = core.CountdownTimer(10)  # Set the initial countdown time to 10 seconds
  
    while countdown_timer.getTime() > 8:
        termination_check()
        countdown_text[str(int(math.ceil(countdown_timer.getTime())))].draw()
        exp_win.flip()
        
    while countdown_timer.getTime() < 8 and countdown_timer.getTime() > 7: #turn on RENS at 8 seconds
        termination_check()
        if current_trial["context"] != None:
            context_images[current_trial["context"]].draw()
        if current_trial["stimulus"] != None:
            RENS_pulse_pattern_images[current_trial["stimulus"]].draw()
            RENS_pulse_pattern_text[current_trial["stimulus"]].draw()
            if s != None:
                for time, port in RENS_pulse_pattern_trig_list[RENS_pulse_pattern_names[current_trial["stimulus"]]]:
                    if abs(countdown_timer.getTime() - math.floor(countdown_timer.getTime()) - time) < timer_precision_range:
                        s.write(('WRITE '+str(port)+' 1000 0\n').encode('utf-8'))
        countdown_text[str(int(math.ceil(countdown_timer.getTime())))].draw()
        exp_win.flip()

    while countdown_timer.getTime() < 7 and countdown_timer.getTime() > 0: #ask for expectancy at 7 seconds
        termination_check()
        if current_trial["context"] != None:
            context_images[current_trial["context"]].draw()
        if current_trial["stimulus"] != None:
            RENS_pulse_pattern_images[current_trial["stimulus"]].draw()
            RENS_pulse_pattern_text[current_trial["stimulus"]].draw()
            if s != None:
                for time, port in RENS_pulse_pattern_trig_list[RENS_pulse_pattern_names[current_trial["stimulus"]]]:
                    if abs(countdown_timer.getTime() - math.floor(countdown_timer.getTime()) - time) < timer_precision_range:
                        # s.write(('WRITE '+str(port)+ '1000 0\n').encode('utf-8'))
                        s.write(('WRITE '+str(port)+' 1000 0\n').encode('utf-8'))
        countdown_text[str(int(math.ceil(countdown_timer.getTime())))].draw()
        
        # Ask for expectancy/anxiety rating
        if midtrial_rating != None:
            rating_text[str(midtrial_rating)].draw() 
            rating_stim[str(midtrial_rating)].draw()
        exp_win.flip()    
        
    if midtrial_rating != None:
        current_trial[str(midtrial_rating)+"_response"] = rating_stim[str(midtrial_rating)].getRating() #saves the expectancy response for that trial
        rating_stim[str(midtrial_rating)].reset() #resets the expectancy slider for subsequent trials
        
    # deliver shock
    fix_stim.draw()
    exp_win.flip()
    
    if s != None:
        s.write(('WRITE '+str(shock_trig["high"])+' '+str(port_buffer_duration)+' 0\n').encode('utf-8'))

    wait(1)
    
    # Get pain rating
    while rating_stim["pain"].getRating() is None: # while mouse unclicked
        termination_check()
        rating_text["pain"].draw()
        rating_stim["pain"].draw()
        exp_win.flip()
            
    pain_response_end_time = core.getTime() + response_hold_duration # amount of time for participants to adjust slider after making a response
        
    while core.getTime() < pain_response_end_time:
        termination_check()
        rating_text["pain"].draw()
        rating_stim["pain"].draw()
        exp_win.flip()

    current_trial["pain_response"] = rating_stim["pain"].getRating()
    rating_stim["pain"].reset()

    exp_win.flip()
    
    wait(trial_iti)

exp_finish = False


# Run experiment
while not exp_finish:
    termination_check()
    # display welcome and calibration instructions
    instruction_trial(instructions_text["welcome"],3)
    instruction_trial(instructions_text["RENS_introduction"],3)
    
    instruction_trial(instructions_text["calibration"],8)
    show_calib_trial([
        trial for trial in trial_order
        if trial["phase"] == "calibration"])
        
    instruction_trial(instructions_text["calibration_finish"],2)

    #display main experiment phase
    instruction_trial(instructions_text["experiment"],10)
    previous_block = 1
    midtrial_index = (cb // 4) % 2
    
    for trial in [t for t in trial_order if t["phase"] != "calibration"]:
        #alternate anxiety vs expectancy
        if trial["blocknum"] == 1 and trial["phase"] == "extinction":
            show_trial(trial,None)
        else: 
            if trial["blocknum"] != previous_block:    
                midtrial_index = (midtrial_index + 1) % len(midtrial_rating_list)
                previous_block = trial["blocknum"]
                
            midtrial_rating = midtrial_rating_list[midtrial_index]
            show_trial(trial,midtrial_rating)
        
    if s != None:
        s.write(b'WRITE 0\n')  # Set all pins to 0 to shut off RENS, shock etc.    
    # # save trial data
    save_data(trial_order)
    exit_screen(instructions_text["end"])
    
    exp_finish = True
    
exp_win.close()