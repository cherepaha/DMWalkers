from walking_exp_ui import WalkingExpUI
from walking_exp_da import WalkingExpDA
from datetime import datetime
import time, math
import numpy as np

class WalkingExp:   
    sc_steps = [4, 2, 1, 0]
    sc_delays = [7, 30, 183, 365, 1095]

    def __init__(self, user_interface, data_access):
        self.user_interface = user_interface
        self.data_access = data_access
        self.mcq_trial_params = self.data_access.get_trial_params()

    def run_exp(self, n_blocks=4):
        user_interface.show_messages('Left screen', 'Right screen')
        
        sc_state = { delay : [8, 16] for delay in self.sc_delays } 
        for i in range(1, n_blocks+1):
            sc_state = self.run_block(i, sc_state)         
        user_interface.show_messages('Game over!')
    
    def run_block(self, block_no, sc_state):
        mcq_trial_no = math.ceil(len(self.mcq_trial_params)/4.0)
        mcq_trials = self.mcq_trial_params[int((block_no-1)*mcq_trial_no):\
                                            int(min(block_no*mcq_trial_no, len(self.mcq_trial_params)))]
        sc_trials = [[0, sc_state[delay][0], delay, sc_state[delay][1], 1.0] for delay in self.sc_delays]
        
        trials = np.concatenate((mcq_trials, sc_trials))
        np.random.shuffle(trials)

        for i, trial_params in enumerate(trials):
            trial_info = self.run_trial((block_no-1)*12+i+1, trial_params)
            # if staircase trial, update the rewards
            if trial_params[-1]==1:
                # if ss was chosen, decrease ss reward
                if ((trial_info[-4] & (trial_info[-3]=='left')) or ((not trial_info[-4]) & \
                                                                    (trial_info[-3]=='right'))):
                    sc_state[trial_params[2]][0] -= self.sc_steps[block_no-1]
                # if ll was chosen, decrease ll reward
                else:
                    sc_state[trial_params[2]][1] -= self.sc_steps[block_no-1]
            self.data_access.write_trial_log(trial_info)     
        return sc_state

    def run_trial(self, trial_no, params, choice_type='mcq'):
        self.user_interface.show_messages('Ready?')
        self.user_interface.show_messages('Go!')
        trial_start_time_str = datetime.strftime(datetime.now(), '%Y-%m-%d--%H-%M-%S')
        trial_start_time = time.clock()
        response = self.user_interface.show_choices(params)
        response_time = time.clock() - trial_start_time            

        return [self.data_access.exp_info['subj_id'], trial_no, bool(params[-1]),
                params[0], params[1], params[2], params[3],
                self.user_interface.is_ss_left, response, 
                response_time, trial_start_time_str]
                
user_interface = WalkingExpUI(n_screens = 2)   
data_access = WalkingExpDA()   
we = WalkingExp(user_interface, data_access)
we.run_exp()
