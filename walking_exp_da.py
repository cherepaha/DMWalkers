import csv
import numpy as np
from numpy import random
from datetime import datetime
import os

class WalkingExpDA:
    trial_log_file = ''
    exp_info = {}
    
    def __init__(self):
        self.exp_info['subj_id'] = self.generate_subj_id()        
        self.exp_info['start_time'] = datetime.strftime(datetime.now(), '%b_%d_%Y_%H_%M')
        self.initialize_log()
        
    def generate_subj_id(self):
        file_name = 'existing_subj_ids.txt'
        try:
            f = open(file_name, 'r')
        except IOError:
            with open(file_name, 'w') as f:
                f.write('666\n')
                
        existing_subj_ids = np.loadtxt(file_name)
        subj_id = int(random.uniform(100, 999))
        while subj_id in existing_subj_ids:
            subj_id = int(random.uniform(100, 999))

        with open(file_name, 'ab+') as fp:
            writer = csv.writer(fp, delimiter = '\t')
            writer.writerow([str(subj_id)])
        print('subj_id: %i' % subj_id)
        return str(subj_id)

    def initialize_log(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        self.log_file = 'data/' + self.exp_info['subj_id'] + '_' + self.exp_info['start_time'] + '.txt'    
        with open(self.log_file, 'ab+') as fp:
            writer = csv.writer(fp, delimiter = '\t')
            writer.writerow(['subj_id', 'trial_no', 'is_staircase', 'left_delay', 'left_amount', 
                   'right_delay', 'right_amount', 'is_ss_on_left', 'response', 
                   'RT', 'start_time'])
        
    def write_trial_log(self, trial_info):
        with open(self.log_file, 'ab+') as fp:
            writer = csv.writer(fp, delimiter = '\t')
            writer.writerow(trial_info)

    def get_trial_params(self):
        trial_params = np.loadtxt('mcq.csv', skiprows = 1, delimiter = ',')
        # zeros indicate mcq trials
        trial_params = np.column_stack((trial_params, np.zeros(27)))
        return trial_params
    