import time, random
import numpy as np
from psychopy import visual, event, core

class WalkingExpUI:
    #unicode symbol of currency used
    currency_symbol = '\u00A3' #% GBP
#    currency_symbol = '\u20AC' #% EUR

    # Parameters of Kinect setup
    trajectory_path = 'monkey1b-pos1_2015-11-19.dat'
    start_threshold = 1.5    
    left_resp_area_center = [3.25, 1.45]
    right_resp_area_center = [3.25, -1.45]
    resp_area_radius = 0.25
    
    # set to True if automatic detection of trial start/end based on Kinect data is needed 
    auto_control = False
    
    def __init__(self, n_screens=2):
        self.n_screens = n_screens
        self.is_ss_left = random.choice([True, False])
        print 'Smaller sooner displayed on the left? %r' %(self.is_ss_left)
        
        if self.n_screens == 1:
            text_h_offset = 0.45
            text_v_offset_left = 0.35
            text_v_offset_right = text_v_offset_left
            
            text_height_left = 0.35
            text_height_right = text_height_left
            
            self.left_win = visual.Window(units='norm', fullscr=False, 
                                          screen=0, monitor='laptop_monitor') 
            self.right_win = self.left_win
            
        elif self.n_screens == 2: 
            text_h_offset = 0.0
            text_v_offset_left = 0.35
            text_v_offset_right = 0.3
            
            text_height_left = 0.35
            text_height_right = 0.2
            
            self.left_win = visual.Window(units='norm', fullscr=True, 
                                          screen=0, monitor='laptop_monitor') 
            self.right_win = visual.Window(units='norm', fullscr=True, 
                                           screen=1, monitor='walking_exp_monitor')
            
        left_delay_pos = [-text_h_offset, -text_v_offset_left]
        right_delay_pos = [text_h_offset, -text_v_offset_right]
        left_amount_pos = [-text_h_offset, text_v_offset_left]
        right_amount_pos = [text_h_offset, text_v_offset_right]        
                
        self.left_message = visual.TextStim(self.left_win, height = text_height_left)
        self.right_message = visual.TextStim(self.right_win, height = text_height_right)
        
        self.left_delay = visual.TextStim(self.left_win, pos = left_delay_pos, 
                                          height = text_height_left)
        self.right_delay = visual.TextStim(self.right_win, pos = right_delay_pos, 
                                           height = text_height_right)
        
        self.left_amount = visual.TextStim(self.left_win, pos=left_amount_pos,
                                           height = text_height_left)
        self.right_amount = visual.TextStim(self.right_win, pos = right_amount_pos,
                                            height = text_height_right)
            
    def show_messages(self, left_message, right_message = None):
        if right_message is None:
            right_message = left_message
            
        self.left_message.setText(left_message)       
        self.left_message.draw()
        self.left_win.flip()
        
        if self.n_screens == 2:
            self.right_message.setText(right_message)
            self.right_message.draw()
            self.right_win.flip()
        
        keys = event.waitKeys(['space', 'escape'])
        if 'escape' in keys:
            core.quit()

    def show_choices(self, params):
        ss_choice = {}
        ll_choice = {}
        response = ''

        ss_choice['delay'] = 'today' if params[0]==0 else 'in %d days'%params[0]
        ss_choice['amount'] = u'\u00A3%d' % params[1]
        
        ll_choice['delay'] = 'in %d days' % params[2]        
        ll_choice['amount'] = u'\u00A3%d' % params[3]
        
        if self.is_ss_left:
            left_choice = ss_choice
            right_choice = ll_choice
        else:
            left_choice = ll_choice
            right_choice = ss_choice

        self.left_delay.setText(left_choice['delay'])
        self.right_delay.setText(right_choice['delay'])
        
        self.left_amount.setText(left_choice['amount'])
        self.right_amount.setText(right_choice['amount'])

        if self.auto_control:
            # in this case, don't switch stimuli on until subject is far enough from Kinect
            position = self.get_current_position()
            while not self.is_far_enough(position):
                print(position)
                self.flip_screens()
            self.draw_choices_text()
            while True:                
                self.flip_screens()            
                has_responded, resp = self.is_near_monitor(self.get_current_position())
                if has_responded:
                    response = resp
                    break
        else:
            self.draw_choices_text()
            self.flip_screens()
            keys = event.waitKeys(['space', 'escape', 'lctrl', 'rctrl'])
            if 'escape' in keys:
                core.quit()
            elif 'lctrl' in keys:
                response = 'left'
            elif 'rctrl' in keys:
                response = 'right'
                
        print(response, self.is_ss_left)
        return response

    def draw_choices_text(self):
        self.left_delay.draw()
        self.right_delay.draw()
        self.left_amount.draw()
        self.right_amount.draw()
    
    def flip_screens(self):
        self.left_win.flip()
        if self.n_screens ==2:
            self.right_win.flip() 
    
    def get_current_position(self):
        # what happens if file is not available?
        # if the subject starts moving from Kinect, what happens with the data file?
        # is it empty, or NaNs are recorded?
        log = np.loadtxt(self.trajectory_path, delimiter = ' ')
        return (log[-1,[1,2]] + log[-1,[5,6]])/2
        
    def is_near_monitor(self, position):
        if np.sqrt((position[0]-self.left_resp_area_center[0])^2 + \
            (position[1]-self.left_resp_area_center[1])^2) < self.resp_area_radius:
                return True, 'left'
        elif np.sqrt((position[0]-self.right_resp_area_center[0])^2 + \
            (position[1]-self.right_resp_area_center[1])^2) < self.resp_area_radius:
                return True, 'right'
        else:
            return False, None
    
    def is_far_enough(self, position):
        return True if position[1]>self.start_threshold else False
