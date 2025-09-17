import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F
import math
import sys
import numpy as np
import pdb
import io
import shutil

import time
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')
import pandas as pd
import copy
import os
from pydoc import locate

from perforatedai import globals_perforatedai as GPA
from perforatedai import modules_perforatedai as PA
from perforatedai import utils_perforatedai as UPA


class module_layer_tracker_perforatedai():
    
    def __init__(self, doing_pai, save_name, making_graphs=True, param_vals_setting=-1, values_per_train_epoch=-1, values_per_val_epoch=-1):
        #this allows the tracker to be initialized to just track values so if you want to test and make comparable graphs without pb layers you can use the same tracker
        self.member_vars = {}
        #Whether or not PAI will be running
        self.member_vars['doing_pai'] = doing_pai
        #How many Dendrite Nodes have been added
        self.member_vars['num_dendrites_added'] = 0
        self.member_vars['num_cycles'] = 0
        self.neuron_module_vector = []
        self.tracked_neuron_layer_vector = []
        self.member_vars['mode'] = 'n'
        self.member_vars['num_epochs_run'] = -1
        self.member_vars['total_epochs_run'] = -1
        # Last epoch that the validation score or correlation score was improved
        self.member_vars['epoch_last_improved'] = 0
        # Running validation accuracy
        self.member_vars['running_accuracy'] = 0
        # True if maxing validation, False if minimizing Loss
        self.member_vars['maximizing_score'] = True
        # Mode for switching back and forth between learning modes
        self.member_vars['switch_mode'] = GPA.switch_mode
        # Epoch of the last switch
        self.member_vars['last_switch'] = 0
        self.member_vars['current_best_validation_score'] = 0
        # Last epoch where the learning rate was updated
        self.member_vars['initial_lr_test_epoch_count'] = -1
        self.member_vars['global_best_validation_score'] = 0
        #list of switch epochs
        #last validation score of a switch is this.  so if there are 10 epochs, this will be 9
        self.member_vars['switch_epochs'] = []
        #paramter counts at each network structure
        self.member_vars['param_counts'] = []
        self.member_vars['n_switch_epochs'] = []
        self.member_vars['p_switch_epochs'] = []
        self.member_vars['accuracies'] = []
        self.member_vars['last_improved_accuracies'] = []
        self.member_vars['test_accuracies'] = []
        self.member_vars['n_accuracies'] = []
        self.member_vars['p_accuracies'] = []
        self.member_vars['running_accuracies'] = []
        self.member_vars['extra_scores'] = {}
        self.member_vars['extra_scores_without_graphing'] = {}
        self.member_vars['test_scores'] = []
        self.member_vars['n_extra_scores'] = {}
        self.member_vars['training_loss'] = []
        self.member_vars['training_learning_rates'] = []
        self.member_vars['best_scores'] = []
        self.member_vars['current_scores'] = []
        self.member_vars['watch_weights'] = []
        self.member_vars['n_epoch_times'] = []
        self.member_vars['p_epoch_times'] = []
        self.member_vars['n_train_times'] = []
        self.member_vars['p_train_times'] = []
        self.member_vars['n_val_times'] = []
        self.member_vars['p_val_times'] = []
        self.member_vars['overwritten_extras'] = []
        self.member_vars['overwritten_vals'] = []
        self.member_vars['overwritten_epochs'] = 0
        self.member_vars['param_vals_setting'] = GPA.param_vals_setting
        self.member_vars['optimizer'] = None
        self.member_vars['scheduler'] = None
        self.member_vars['optimizer_instance'] = None
        self.member_vars['scheduler_instance'] = None

        self.loaded = False

        self.member_vars['manual_train_switch'] = False
    
        if(GPA.doing_mean_best):
            self.member_vars['best_mean_scores'] = []
        self.member_vars['current_n_learning_rate_initial_skip_steps'] = 0
        self.member_vars['last_max_learning_rate_steps'] = 0
        self.member_vars['last_max_learning_rate_value'] = -1
        #this is to be filled in with [learning rate 1->2, and learning rate 2 start] to be compared
        self.member_vars['current_cycle_lr_max_scores'] = []
        self.member_vars['current_step_count'] = 0
        
        #set these to be True for the first initialization N
        self.member_vars['committed_to_initial_rate'] = True
        self.member_vars['current_n_set_global_best'] = True
        self.member_vars['best_mean_score_improved_this_epoch'] = 0
        self.member_vars['num_dendrite_tries'] = 0


        self.memberVarTypes = {}
        self.memberVarTypes['doing_pai'] = 'bool'
        self.memberVarTypes['num_dendrites_added'] = 'int'
        self.memberVarTypes['num_cycles'] = 'int'
        self.memberVarTypes['mode'] = 'string'
        self.memberVarTypes['num_epochs_run'] = 'int'
        self.memberVarTypes['total_epochs_run'] = 'int'
        self.memberVarTypes['epoch_last_improved'] = 'int'
        self.memberVarTypes['running_accuracy'] = 'float'
        self.memberVarTypes['maximizing_score'] = 'bool'
        self.memberVarTypes['switch_mode'] = 'int'
        self.memberVarTypes['last_switch'] = 'int'
        self.memberVarTypes['current_best_validation_score'] = 'float'
        self.memberVarTypes['initial_lr_test_epoch_count'] = 'int'
        self.memberVarTypes['global_best_validation_score'] = 'float'
        self.memberVarTypes['switch_epochs'] = 'int array'
        self.memberVarTypes['param_counts'] = 'int array'
        self.memberVarTypes['n_switch_epochs'] = 'int array'
        self.memberVarTypes['p_switch_epochs'] = 'int array'
        self.memberVarTypes['accuracies'] = 'float array'
        self.memberVarTypes['last_improved_accuracies'] = 'int array'
        self.memberVarTypes['test_accuracies'] = 'float array'
        self.memberVarTypes['n_accuracies'] = 'float array'
        self.memberVarTypes['p_accuracies'] = 'float array'
        self.memberVarTypes['running_accuracies'] = 'float array'
        self.memberVarTypes['extra_scores'] = 'float array dictionary'
        self.memberVarTypes['extra_scores_without_graphing'] = 'float array dictionary'
        self.memberVarTypes['test_scores'] = 'float array'
        self.memberVarTypes['n_extra_scores'] = 'float array dictionary'
        self.memberVarTypes['training_loss'] = 'float array'
        self.memberVarTypes['training_learning_rates'] = 'float array'
        self.memberVarTypes['best_scores'] = 'float array array'
        self.memberVarTypes['current_scores'] = 'float array array'
        self.memberVarTypes['watch_weights'] = 'float array'
        self.memberVarTypes['n_epoch_times'] = 'float array'
        self.memberVarTypes['p_epoch_times'] = 'float array'
        self.memberVarTypes['n_train_times'] = 'float array'
        self.memberVarTypes['p_train_times'] = 'float array'
        self.memberVarTypes['n_val_times'] = 'float array'
        self.memberVarTypes['p_val_times'] = 'float array'
        self.memberVarTypes['overwritten_extras'] = 'float array dictionary array'
        self.memberVarTypes['overwritten_vals'] = 'float array array'
        self.memberVarTypes['overwritten_epochs'] = 'int'
        self.memberVarTypes['param_vals_setting'] = 'int'
        self.memberVarTypes['optimizer'] = 'type'
        self.memberVarTypes['scheduler'] = 'type'
        self.memberVarTypes['optimizer_instance'] = 'empty array'
        self.memberVarTypes['scheduler_instance'] = 'empty array'
        self.memberVarTypes['manual_train_switch'] = 'bool'
        if(GPA.doing_mean_best):
            self.memberVarTypes['best_mean_scores'] = 'float array'
        self.memberVarTypes['current_n_learning_rate_initial_skip_steps'] = 'int'
        self.memberVarTypes['last_max_learning_rate_steps'] = 'int'
        self.memberVarTypes['last_max_learning_rate_value'] = 'float'
        self.memberVarTypes['current_cycle_lr_max_scores'] = 'float array'
        self.memberVarTypes['current_step_count'] = 'int'
        self.memberVarTypes['committed_to_initial_rate'] = 'bool'
        self.memberVarTypes['current_n_set_global_best'] = 'bool'
        self.memberVarTypes['best_mean_score_improved_this_epoch'] = 'int'
        self.memberVarTypes['num_dendrite_tries'] = 'int'




        self.values_per_train_epoch=values_per_train_epoch
        self.values_per_val_epoch=values_per_val_epoch
        self.save_name = save_name
        self.making_graphs = making_graphs

        self.start_time = time.time()
        self.saved_time = 0
        self.start_epoch(internal_call=True)

        if(GPA.verbose):
            print('initing with switch_mode%s' % (self.member_vars['switch_mode']))
        #if(GPA.using_pia_data_parallel == False and torch.cuda.device_count() > 1 and (GPA.device == 'cuda' or GPA.device == torch.device('cuda'))):
            #input('Seeing multiple GPUs but not using PAIDataParallel.  Please either perform the PAIDataParallel steps from the README or include CUDA_VISIBLE_DEVICES=0 in your call')
        #if(GPA.using_pia_data_parallel == True and torch.cuda.device_count() == 1):
            #input('Seeing one GPUs but using custom data parallel.')
            
    def to_string(self):
        full_string = ''
        for var in self.member_vars:
            full_string += (var+',')
            if(self.member_vars[var] == None):
                full_string += ('None')
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'bool':
                full_string += (str(self.member_vars[var]))
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'int':
                full_string += (str(self.member_vars[var]))
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'float':
                full_string += (str(self.member_vars[var]))
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'string':
                full_string += (str(self.member_vars[var]))
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'type':
                name = self.member_vars[var].__module__ + '.' + self.member_vars[var].__name__
                full_string += (str(self.member_vars[var]))
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'empty array':
                full_string += ('[]')
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'int array' or self.memberVarTypes[var] == 'float array':
                full_string += ('\n')
                string = ''
                for val in self.member_vars[var]:
                    string += str(val) + ','
                #remove the last ,
                string = string[:-1]
                full_string += (string)
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'float array dictionary array':
                full_string += ('\n')
                for array in self.member_vars[var]:
                    for key in array:
                        string = ''
                        string += key + ','
                        for val in array[key]:
                            string += str(val) + ','
                        #remove the last ,
                        string = string[:-1]
                        full_string += (string)
                        full_string += ('\n')
                    full_string += ('endkey')
                    full_string += ('\n')
                full_string += ('endarray')
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'float array dictionary':
                full_string += ('\n')
                for key in self.member_vars[var]:
                    string = ''
                    string += key + ','
                    for val in self.member_vars[var][key]:
                        string += str(val) + ','
                    #remove the last ,
                    string = string[:-1]
                    full_string += (string)
                    full_string += ('\n')
                full_string += ('end')
                full_string += ('\n')
            elif self.memberVarTypes[var] == 'float array array':
                full_string += ('\n')
                for array in self.member_vars[var]:
                    string = ''
                    for val in array:
                        string += str(val) + ','
                    #remove the last ,
                    string = string[:-1]
                    full_string += (string)
                    full_string += ('\n')
                full_string += ('end')
                full_string += ('\n')
            else:
                print('Didnt find a member variable')
                import pdb; pdb.set_trace()
        return full_string

    def from_string(self, string):
        f = io.StringIO(string)
        while(True):
            line = f.readline()
            if(not line):
                break
            vals = line.split(',')
            var = vals[0]
            if self.memberVarTypes[var] == 'bool':
                #Second item without \n
                val = vals[1][:-1]
                if(val == 'True'):
                    self.member_vars[var] = True
                elif(val == 'False'):
                    self.member_vars[var] = False
                elif(val == '1'):
                    self.member_vars[var] = 1
                elif(val == '0'):
                    self.member_vars[var] = 0
                else:
                    print('Something went wrong with loading')
                    import pdb; pdb.set_trace()
            elif self.memberVarTypes[var] == 'int':
                val = vals[1]
                self.member_vars[var] = int(val)
            elif self.memberVarTypes[var] == 'float':
                val = vals[1]
                self.member_vars[var] = float(val)
            elif self.memberVarTypes[var] == 'string':
                val = vals[1][:-1]
                self.member_vars[var] = val
            elif self.memberVarTypes[var] == 'type':
                #ignore loading types, the pai_tracker should already have them setup and overwriting will cause problems
                continue
                #val = vals[1][:-1]
                #self.member_vars[var] = locate(val)
            elif self.memberVarTypes[var] == 'empty array':
                val = vals[1]
                self.member_vars[var] = []
            elif self.memberVarTypes[var] == 'int array':
                vals = f.readline()[:-1].split(',')
                self.member_vars[var] = []
                if vals[0] == '':
                    continue
                for val in vals:
                    self.member_vars[var].append(int(val))
            elif self.memberVarTypes[var] == 'float array':
                vals = f.readline()[:-1].split(',')
                self.member_vars[var] = []
                if vals[0] == '':
                    continue
                for val in vals:
                    self.member_vars[var].append(float(val))
            elif self.memberVarTypes[var] == 'float array dictionary array':
                self.member_vars[var] = []
                line2 = f.readline()[:-1]
                while line2 != 'endarray':
                    temp = {}
                    while line2 != 'endkey':
                        vals = line2.split(',')
                        name = vals[0]
                        temp[name] = []
                        vals = vals[1:]
                        for val in vals:
                            temp[name].append(float(val))
                        line2 = f.readline()[:-1]
                    self.member_vars[var].append(temp)
                    line2 = f.readline()[:-1]
            elif self.memberVarTypes[var] == 'float array dictionary':
                self.member_vars[var] = {}
                line2 = f.readline()[:-1]
                while line2 != 'end':
                    vals = line2.split(',')
                    name = vals[0]
                    self.member_vars[var][name] = []
                    vals = vals[1:]
                    for val in vals:
                        self.member_vars[var][name].append(float(val))
                    line2 = f.readline()[:-1]
            elif self.memberVarTypes[var] == 'float array array':
                self.member_vars[var] = []
                line2 = f.readline()[:-1]
                while line2 != 'end':
                    vals = line2.split(',')
                    self.member_vars[var].append([])
                    if not line2 == '':
                        for val in vals:
                            self.member_vars[var][-1].append(float(val))
                    line2 = f.readline()[:-1]
            else:
                print('didnt find a member variable')
                import pdb; pdb.set_trace()
    
    #dont think this is called anymore.
    def setup_values_arrays(self):
        #This should be in the trianing loop but only run the first epoch
        if(self.member_vars['num_epochs_run'] == 0):
            for layer in self.neuron_module_vector:
                layer.dendrite_module.dendrite_values[0].setup_arrays(-1)
    
    def save_tracker_settings(self):
        if not os.path.isdir(self.save_name):
            os.makedirs(self.save_name)
        f = open(self.save_name + '/arrayDims.csv', 'w')
        for layer in self.neuron_module_vector:
            f.write('%s,%d\n' % (layer.name, layer.dendrite_module.dendrite_values[0].out_channels))
        f.close()
        if(not GPA.silent):
            print('Tracker settings saved.')
            print('You may now delete save_tracker_settings')

    def initialize_tracker_settings(self):
        channels = {}
        if not os.path.exists(self.save_name + '/arrayDims.csv'):
            print('You must call save_tracker_settings before initialize_tracker_settings')
            print('Follow instructions in customization.md')
            pdb.set_trace()
        f = open(self.save_name + '/arrayDims.csv', 'r')
        for line in f:
            channels[line.split(',')[0]] = int(line.split(',')[1])
        for layer in self.neuron_module_vector:
            layer.dendrite_module.dendrite_values[0].setup_arrays(channels[layer.name])
    '''
    and then add to README that if you are using data parallel or distributed data parallel. just do this in two phases.
        first dont call dataparallel and just use one GPU.
        call saveArrayDims after the first backward.
        Then call setupArrayDims after convert_network but before dataparallel.
        
        Also catch error that happens if you just call dataparalle without this and say this is whats wrong.
    '''
    

    ## CLOSED ONLY
    #this function is for when loading but then also need to change anything
    def do_temp_reinitialize_thing(self):
        print('doing a temp do_temp_reinitialize_thing make sure you want this')
        pdb.set_trace()
        for layer in self.neuron_module_vector:
            layer.dendrite_module.candidate_grad_average_for_scaling = layer.dendrite_module.candidate_grad_average
            layer.dendrite_module.main_grad_average_for_scaling = layer.dendrite_module.candidate_grad_average

    ## END CLOSED ONLY

    #this is the case for if you just want to use their optimizer and follow along rather than handle it here
    def set_optimizer_instance(self, optimizer_instance):
        try:
            if(optimizer_instance.param_groups[0]['weight_decay'] > 0 and GPA.weight_decay_accepted == False):
                print('For PAI training it is reccomended to not use weight decay in your optimizer')
                print('Set GPA.weight_decay_accepted = True to ignore this warning or c to continue')
                GPA.weight_decay_accepted = True
                import pdb; pdb.set_trace()
        except:
            pass

        
        self.member_vars['optimizer_instance'] = optimizer_instance

    def set_optimizer(self, optimizer):
        self.member_vars['optimizer'] = optimizer

    def set_scheduler(self, scheduler):
        if(not scheduler is torch.optim.lr_scheduler.ReduceLROnPlateau):
            if(GPA.verbose):
                print('Not using reduce on plateou, this is not reccomended')        
        self.member_vars['scheduler'] = scheduler
        

    def increment_scheduler(self, num_ticks, mode):
        current_steps = 0
        current_ticker = 0
        for param_group in GPA.pai_tracker.member_vars['optimizer_instance'].param_groups:
            learning_rate1 = param_group['lr']
        crashTest = 0
        if(GPA.verbose):
            print('using scheduler:')
            print(type(self.member_vars['scheduler_instance']))
        while current_ticker < num_ticks:
            if(GPA.verbose):
                print('lower start rate initial %f stepping %d times' % (learning_rate1, GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']))
            if type(self.member_vars['scheduler_instance']) is torch.optim.lr_scheduler.ReduceLROnPlateau:
                if(mode == 'step_learning_rate'):
                    #step with the counter as last improved accuracy from the initial value before this switch.  This is used to initially start with a lower rate
                    self.member_vars['scheduler_instance'].step(metrics=self.member_vars['last_improved_accuracies'][GPA.pai_tracker.steps_after_switch()-1])
                elif(mode == 'increment_epoch_count'):
                    #step with the the improved epoch counts up to current location, this is used when loading.
                    self.member_vars['scheduler_instance'].step(metrics=self.member_vars['last_improved_accuracies'][-((num_ticks-1)-current_ticker)-1])
            else:
                    self.member_vars['scheduler_instance'].step()
            for param_group in GPA.pai_tracker.member_vars['optimizer_instance'].param_groups:
                learning_rate2 = param_group['lr']
            if(learning_rate2 != learning_rate1):
                current_steps += 1
                learning_rate1 = learning_rate2
                if(mode == 'step_learning_rate'):
                    current_ticker += 1
                if(GPA.verbose):
                    print('1 step %d to %f' % (current_steps, learning_rate2))
            if(mode == 'increment_epoch_count'):
                current_ticker += 1
            crashTest += 1
            if(crashTest > 2000):
                pdb.set_trace()
        return current_steps, learning_rate1
    
    def setup_optimizer(self, net, opt_args, sched_args = None):
        #if this optimizer is just passing in the model then skip it
        if('weight_decay' in opt_args and not(GPA.weight_decay_accepted)):
            print('For PAI training it is recommended to not use weight decay in your optimizer')
            print('Set GPA.weight_decay_accepted = True to ignore this warning or c to continue')
            GPA.weight_decay_accepted = True
            import pdb; pdb.set_trace()
        if(not 'model' in opt_args.keys()):
            if(self.member_vars['mode'] == 'n'):
                opt_args['params'] = filter(lambda p: p.requires_grad, net.parameters())
            else:
                #sched_args['patience'] = GPA.p_patience
                #count = 0
                #for param in opt_args['params']:
                    #print(param)
                    #count = count + 1
                #print(count)
                opt_args['params'] = UPA.get_pai_network_params(net)
                #pdb.set_trace()
        optimizer = self.member_vars['optimizer'](**opt_args)
        self.member_vars['optimizer_instance'] = optimizer
        if(self.member_vars['scheduler'] != None):
            self.member_vars['scheduler_instance'] = self.member_vars['scheduler'](optimizer, **sched_args)
            current_steps = 0
            for param_group in GPA.pai_tracker.member_vars['optimizer_instance'].param_groups:
                learning_rate1 = param_group['lr']
            if(GPA.verbose):
                print('resetting scheduler with %d steps and %d initial ticks to skip' % (GPA.pai_tracker.steps_after_switch(), GPA.initial_history_after_switches))
            #reversed is fine because it is required for the first if and not used in the second if
            #if we just triggered a reset where we want to start with a lower learning rate then keep adding the last epoch improved until we get there
            if(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'] != 0):
                additional_steps, learning_rate1 = self.increment_scheduler(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'], 'step_learning_rate')
                current_steps += additional_steps
            if(self.member_vars['mode'] == 'n' or GPA.learn_dendrites_live):
                initial = GPA.initial_history_after_switches
            else:
                initial = 0
            if(GPA.pai_tracker.steps_after_switch() > initial):
                #minus an extra 1 becuase this will be getting called after start epoch has been called at the end of add validation score, which means steps after switch will actually be off by 1
                additional_steps, learning_rate1 = self.increment_scheduler((GPA.pai_tracker.steps_after_switch() - initial)-1, 'increment_epoch_count')
                current_steps += additional_steps
                #then after getting to the initial point if it loaded and has completed some steps after switch then apply those
            if(GPA.verbose):
                print('scheduler update loop with %d ended with %f' % (current_steps, learning_rate1))
                print('scheduler ended with %d steps and lr of %f' % (current_steps, learning_rate1))
            self.member_vars['current_step_count'] = current_steps
            return optimizer, self.member_vars['scheduler_instance']
        else:
            return optimizer

    def clear_optimizer_and_scheduler(self):
        #self.member_vars['optimizer'] = None
        #self.member_vars['scheduler'] = None
        self.member_vars['optimizer_instance'] = None
        self.member_vars['scheduler_instance'] = None


    def switch_time(self):
        switch_phrase = 'No mode, this should never be the case.'
        if(self.member_vars['switch_mode'] == GPA.DOING_SWITCH_EVERY_TIME):
           switch_phrase = 'DOING_SWITCH_EVERY_TIME'
        elif(self.member_vars['switch_mode'] == GPA.DOING_HISTORY):
           switch_phrase = 'DOING_HISTORY'
        elif(self.member_vars['switch_mode'] == GPA.DOING_FIXED_SWITCH):
           switch_phrase = 'DOING_FIXED_SWITCH'
        elif(self.member_vars['switch_mode'] == GPA.DOING_NO_SWITCH):
           switch_phrase = 'DOING_NO_SWITCH'
        if(not GPA.silent):
            print('Checking PAI switch with mode %c, switch mode %s, epoch %d, last improved epoch %d, total Epochs %d, cap_at_n setting: %d, n: %d, p:%d, num_cycles: %d' % 
            (self.member_vars['mode'], switch_phrase, self.member_vars['num_epochs_run'], self.member_vars['epoch_last_improved'], 
            self.member_vars['total_epochs_run'], GPA.cap_at_n, GPA.n_epochs_to_switch, GPA.p_epochs_to_switch, self.member_vars['num_cycles']))
        #this will fill in epoch last improved
        self.best_pai_score_improved_this_epoch() ## CLOSED ONLY
        if(self.member_vars['switch_mode'] == GPA.DOING_NO_SWITCH):
            if(not GPA.silent):
                print('Returning False - doing no switch mode')
            return False
        if(self.member_vars['switch_mode'] == GPA.DOING_SWITCH_EVERY_TIME):
            if(not GPA.silent):
                print('Returning True - switching every time')
            return True
        if(((self.member_vars['mode'] == 'n') or GPA.learn_dendrites_live) and (self.member_vars['switch_mode'] == GPA.DOING_HISTORY) and (GPA.pai_tracker.member_vars['committed_to_initial_rate'] == False) and (GPA.dont_give_up_unless_learning_rate_lowered)
           and (self.member_vars['current_n_learning_rate_initial_skip_steps'] < self.member_vars['last_max_learning_rate_steps']) and self.member_vars['scheduler'] != None):
            if(not GPA.silent):
                print('Returning False since no first step yet and comparing initial %d to last max %d' %(self.member_vars['current_n_learning_rate_initial_skip_steps'], self.member_vars['last_max_learning_rate_steps']))
            return False

        cap_switch = False ## CLOSED ONLY
        if(len(self.member_vars['switch_epochs']) == 0):
            thisCount = (self.member_vars['num_epochs_run'])
        else:
            thisCount = (self.member_vars['num_epochs_run'] - self.member_vars['switch_epochs'][-1])
        if(self.member_vars['switch_mode'] == GPA.DOING_HISTORY and self.member_vars['mode'] == 'p' and GPA.cap_at_n):
            #if(len(self.member_vars['switch_epochs']) == 1):
            #trying method with always capping at the first N
            prevCount = self.member_vars['switch_epochs'][0]
            #else:
                #prevCount = self.member_vars['switch_epochs'][-1] - self.member_vars['switch_epochs'][-2]
            #print('Checking cap_at_n switch with this count  %d, prev %d' % (thisCount, prevCount))
            if(thisCount >= prevCount):
                cap_switch = True
                if(not GPA.silent):
                    print('cap_at_n is True')
        if(self.member_vars['switch_mode'] == GPA.DOING_HISTORY and 
            (
                ((self.member_vars['mode'] == 'n') and (self.member_vars['num_epochs_run'] - self.member_vars['epoch_last_improved'] >= GPA.n_epochs_to_switch) and thisCount >= GPA.initial_history_after_switches + GPA.n_epochs_to_switch)
                or
                (((self.member_vars['mode'] == 'p') and (self.member_vars['num_epochs_run'] - self.member_vars['epoch_last_improved'] >= GPA.p_epochs_to_switch)))
             or cap_switch)):
            if(not GPA.silent):
                print('Returning True - History and last improved is hit or cap_at_n is hit')
            return True
        if(self.member_vars['switch_mode'] == GPA.DOING_FIXED_SWITCH and ((self.member_vars['total_epochs_run']%GPA.fixed_switch_num == 0) and self.member_vars['num_epochs_run'] >= GPA.first_fixed_switch_num)):
            if(not GPA.silent):
                print('Returning True - Fixed switch number is hit')
            return True
        if(not GPA.silent):
            print('Returning False - no triggers to switch have been hit')
        return False
    
    def steps_after_switch(self):
        if(self.member_vars['param_vals_setting'] == GPA.PARAM_VALS_BY_TOTAL_EPOCH):
            return self.member_vars['num_epochs_run']
        elif(self.member_vars['param_vals_setting'] == GPA.PARAM_VALS_BY_UPDATE_EPOCH):
            return self.member_vars['num_epochs_run'] - self.member_vars['last_switch']
        elif(self.member_vars['param_vals_setting'] == GPA.PARAM_VALS_BY_NEURON_EPOCH_START):
            if(self.member_vars['mode'] == 'p'):
                return self.member_vars['num_epochs_run'] - self.member_vars['last_switch']
            else:
                return self.member_vars['num_epochs_run']
        else:
            print('%d is not a valid param vals option' % self.member_vars['param_vals_setting'])
            pdb.set_trace()
    

    def add_pai_neuron_module(self, new_layer, initial_add=True):
        #if its a duplicate just ignore the second addition
        if(new_layer in self.neuron_module_vector):
            return
        self.neuron_module_vector.append(new_layer)
        if(self.member_vars['doing_pai']):
            PA.set_wrapped_params(new_layer)
            '''
            if(self.member_vars['mode'] == 'p'):
                for i in range(0, GPA.global_candidates):
                    self.candidate_layer[i].weight.pai_wrapped = True
                    self.candidate_layer[i].bias.pai_wrapped = True
                    self.candidate_batch_norm[i].weight.pai_wrapped = True
                    self.candidate_batch_norm[i].bias.pai_wrapped = True
                    self.candidate_batch_norm[i].running_mean.pai_wrapped = True
                    self.candidate_batch_norm[i].running_var.pai_wrapped = True
                    if(self.num_dendrites > 0):
                        self.dendrites_to_candidates[i].data.pai_wrapped = True
            '''
        if(initial_add):
            self.member_vars['best_scores'].append([])
            self.member_vars['current_scores'].append([])

    def add_tracked_neuron_layer(self, new_layer, initial_add=True):
        #if its a duplicate just ignore the second addition
        if(new_layer in self.neuron_module_vector):
            return
        self.tracked_neuron_layer_vector.append(new_layer)
        if(self.member_vars['doing_pai']):
            PA.set_tracked_params(new_layer)        
           
    def reset_layer_vector(self, net, load_from_restart):
        self.neuron_module_vector = []
        self.tracked_neuron_layer_vector = []
        this_list = UPA.get_pai_modules(net, 0)
        for module in this_list:
            self.add_pai_neuron_module(module, initial_add=load_from_restart)
        this_list = UPA.get_tracked_modules(net, 0)
        for module in this_list:
            self.add_tracked_neuron_layer(module, initial_add=load_from_restart)
            
    ### CLOSED ONLY
    def just_set_mode(self, mode):
        for layer in self.neuron_module_vector:
            layer.just_set_mode(mode)
        for layer in self.tracked_neuron_layer_vector:
            layer.just_set_mode(mode)
    ### END CLOSED ONLY
        
    def reset_vals_for_score_reset(self):
        if(GPA.find_best_lr):
            self.member_vars['committed_to_initial_rate'] = False        
        self.member_vars['current_n_set_global_best'] = False
        #dont rest the global best, but do reset the current best, this is needed when doing learning rate picking to not retain old best
        self.member_vars['current_best_validation_score'] = 0
        self.member_vars['initial_lr_test_epoch_count'] = -1
                
    def set_dendrite_training(self):
        #self.restoreTaggers()
        if(GPA.verbose):
            print('calling set_dendrite_training')

        for layer in self.neuron_module_vector[:]:
                worked = layer.set_mode('p')
                '''
                This should only happen if you have a layer that was added to the PAI vector
                but then its never actually be used.  This can happen when you have set a layers
                to have requires_grad = False or when you have a modlue as a member variable but
                its not actually part of the network.  in that case remove it from future things
                '''
                if not worked:
                    self.neuron_module_vector.remove(layer)
        for layer in self.tracked_neuron_layer_vector[:]:
                worked = layer.set_mode('p')

        self.create_new_dendrite_module()
        #reset last improved counter when switching modes
        self.member_vars['mode'] = 'p'
        self.member_vars['current_n_learning_rate_initial_skip_steps'] = 0
        if(GPA.learn_dendrites_live):
            self.reset_vals_for_score_reset()

        self.member_vars['last_max_learning_rate_steps'] = self.member_vars['current_step_count']

        GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'] = []
        GPA.pai_tracker.member_vars['num_cycles'] += 1

    def set_neuron_training(self):
        for layer in self.neuron_module_vector:
            layer.set_mode('n')
        for layer in self.tracked_neuron_layer_vector[:]:
            layer.set_mode('n')
        #reset last improved counter when switching modes
        #self.reinitialize_for_pai(0)
        self.member_vars['mode'] = 'n'
        self.member_vars['num_dendrites_added'] += 1
        self.member_vars['current_n_learning_rate_initial_skip_steps'] = 0
        self.reset_vals_for_score_reset()

        self.member_vars['current_cycle_lr_max_scores'] = []        
        if(GPA.learn_dendrites_live):
            self.member_vars['last_max_learning_rate_steps'] = self.member_vars['current_step_count']
        GPA.pai_tracker.member_vars['num_cycles'] += 1

        if(GPA.reset_best_score_on_switch):
            GPA.pai_tracker.member_vars['current_best_validation_score'] = 0
            GPA.pai_tracker.member_vars['running_accuracy'] = 0

    def start_epoch(self, internal_call=False):
        if(self.member_vars['manual_train_switch'] and internal_call==True):
            return
        #if its not a self call but it hasnt been initialized yet initialize
        if(internal_call==False and self.member_vars['manual_train_switch'] == False):
            self.member_vars['manual_train_switch'] = True
            #if calling this from a main loop reset the saved time so it knows this is the first call again
            self.saved_time = 0
            self.member_vars['num_epochs_run'] = -1
            self.member_vars['total_epochs_run'] = -1

        #init value so first epoch
        end = time.time()

        if(self.member_vars['manual_train_switch']):
            if(self.saved_time != 0):
                if(self.member_vars['mode'] == 'p'):
                    self.member_vars['p_val_times'].append(end - self.saved_time)
                else:
                    self.member_vars['n_val_times'].append(end - self.saved_time)

        if(self.member_vars['mode'] == 'p'):
            for layer in self.neuron_module_vector:
                for m in range(0, GPA.global_candidates):
                    with torch.no_grad():
                        if(GPA.verbose):
                            print('resetting score for %s' % layer.name)
                        layer.dendrite_module.dendrite_values[m].best_score_improved_this_epoch *= 0
                        layer.dendrite_module.dendrite_values[m].nodes_best_improved_this_epoch *= 0
            self.member_vars['best_mean_score_improved_this_epoch'] = 0

        self.member_vars['num_epochs_run'] += 1
        self.member_vars['total_epochs_run'] = self.member_vars['num_epochs_run'] + self.member_vars['overwritten_epochs']
        self.saved_time = end


    def stop_epoch(self, internal_call=False):
        end = time.time()
        if(self.member_vars['manual_train_switch'] and internal_call==True):
            return
        if(self.member_vars['manual_train_switch']):
            if(self.member_vars['mode'] == 'p'):
                self.member_vars['p_train_times'].append(end - self.saved_time)
            else:
                self.member_vars['n_train_times'].append(end - self.saved_time)
        else:
            if(self.member_vars['mode'] == 'p'):
                self.member_vars['p_epoch_times'].append(end - self.saved_time)
            else:
                self.member_vars['n_epoch_times'].append(end - self.saved_time)            
        self.saved_time = end

    ### CLOSED ONLY
    #this is for if the pb score improved
    def best_pai_score_improved_this_epoch(self, first_call=True):
        #This function must also set epoch last improved and fill in candidate weights
        #this is just scoring candidates. validation score below is for n mode
        if(self.member_vars['mode'] == 'n'):
            return False
        got_a_best = False
        ignore = False
        for layer in self.neuron_module_vector:
            if(GPA.dendrite_learn_mode and (layer.dendrite_module.dendrite_values[0].initialized < GPA.initial_correlation_batches and not ignore)):
                print('You set GPA.initial_correlation_batches to be greater than an entire epoch %d < %d.  This can result in weights not being updated.  You should set that GPA.initial_correlation_batches to be lower than the batches in one epoch. Start over or Load from \'latest\' for %s. It was caught on layer%s' % (layer.dendrite_module.dendrite_values[0].initialized, GPA.initial_correlation_batches,self.save_name,layer.name))
                print('If your epoch is larger than this number it means the layer is not being included in autograd backwards.')
                print('To double check what layers are included in the backwards call set GPA.extra_verbose = True and look for which layers call backward and forward.')
                print('This layer either must be inluded in the backward calls or included in in GPA.moduleNamesToSkip or GPA.module_names_to_track')
                print('If you are here for debugging with a tiny dataset feel free to ignore (this may happen more than once)')
                
                pdb.set_trace()
                ignore = True
            for m in range(0, GPA.global_candidates):
                #if(first_call):
                    #print('got the following improved with the next following sores')
                    #print(layer.dendrite_module.dendrite_values[m].nodes_best_improved_this_epoch)
                    #print(layer.dendrite_module.dendrite_values[m].best_score)
                if(layer.dendrite_module.dendrite_values[m].best_score_improved_this_epoch[0]):#if its anything other than 0, gets set to 1 but can be greater than that in gather
                    if(not GPA.doing_mean_best):
                        if(not GPA.learn_dendrites_live):
                            self.member_vars['epoch_last_improved'] = self.member_vars['num_epochs_run']
                            if(GPA.verbose):
                                print('Individual epoch improved is %d for layer %s with current score: %.16f' % 
                                      (GPA.pai_tracker.member_vars['epoch_last_improved'], 
                                       layer.name, 
                                       layer.dendrite_module.dendrite_values[m].best_score.max().tolist()))
                    #update the best weights
                    #pdb.set_trace()
                    if(first_call):
                        for node in range(len(layer.dendrite_module.dendrite_values[m].nodes_best_improved_this_epoch)):
                            if(layer.dendrite_module.dendrite_values[m].nodes_best_improved_this_epoch[node] > 0):
                                #print('node %d improved so saving its weights' % node)
                                with torch.no_grad():
                                    layer.dendrite_module.best_candidate_layer[m] = copy.deepcopy(layer.dendrite_module.candidate_layer[m])
                            #else:
                            #print('node %d did not improve' % node)
                    got_a_best = True
        if(GPA.doing_mean_best):
            if(self.member_vars['best_mean_score_improved_this_epoch']):
                if(not GPA.learn_dendrites_live):
                    self.member_vars['epoch_last_improved'] = self.member_vars['num_epochs_run']
                    if(GPA.verbose):
                        print('average epoch improved is %d' % GPA.pai_tracker.member_vars['epoch_last_improved'])
                return True
            else:
                return False
        return got_a_best
    ### END CLOSED ONLY

    def initialize(self, model, doing_pai=True, save_name='PAI', making_graphs=True, maximizing_score=True, num_classes=10000000000, values_per_train_epoch=-1, values_per_val_epoch=-1, zooming_graph=True):
        
        model = UPA.convert_network(model)
        self.member_vars['doing_pai'] = doing_pai
        self.member_vars['maximizing_score'] = maximizing_score
        self.save_name = save_name
        self.zooming_graph = zooming_graph
        self.making_graphs = making_graphs
        if(self.loaded == False):
            self.member_vars['running_accuracy'] = (1.0/num_classes) * 100
        self.values_per_train_epoch=values_per_train_epoch
        self.values_per_val_epoch=values_per_val_epoch
        
        if(GPA.testing_dendrite_capacity):
            if(not GPA.silent):
                print('Running a test of Dendrite Capacity.')
            GPA.switch_mode=GPA.DOING_SWITCH_EVERY_TIME
            self.member_vars['switch_mode'] = GPA.switch_mode
            GPA.retain_all_dendrites = True
            GPA.max_dendrite_tries = 1000
            GPA.max_dendrites = 1000
            GPA.initial_correlation_batches = 1
        else:
            if(not GPA.silent):
                print('Running PAI experiment')
        return model
        
    def save_graphs(self, extra_string=''):
        if(self.making_graphs == False):
            return
        
        save_folder = './' + self.save_name + '/'
        #if(GPA.pai_saves):
            #saveolder = '/pai'
        
        plt.ioff()
        fig = plt.figure(figsize=(28,14))
        ax = plt.subplot(221)
        
        
        df1 = None
        
        for list_id in range(len(self.member_vars['overwritten_extras'])):
            for extra_id in self.member_vars['overwritten_extras'][list_id]:
                ax.plot(np.arange(len(self.member_vars['overwritten_extras'][list_id][extra_id])), self.member_vars['overwritten_extras'][list_id][extra_id], 'r')
            ax.plot(np.arange(len(self.member_vars['overwritten_vals'][list_id])), self.member_vars['overwritten_vals'][list_id], 'b')
        
        if(GPA.drawing_pai):
            accuracies = self.member_vars['accuracies']
            extra_scores = self.member_vars['extra_scores']
        else:
            accuracies = self.member_vars['n_accuracies']
            extra_scores = self.member_vars['extra_scores']
        
        ax.plot(np.arange(len(accuracies)), accuracies, label='Validation Scores')
        ax.plot(np.arange(len(self.member_vars['running_accuracies'])), self.member_vars['running_accuracies'], label='Validation Running Scores')
        for extra_score in extra_scores:
            ax.plot(np.arange(len(extra_scores[extra_score])), extra_scores[extra_score], label=extra_score)
        plt.title(save_folder + '/' + self.save_name + "Scores")
        plt.xlabel('Epochs')
        plt.ylabel('Score')
        
        #this will add a point at emoch last improved so while watching can tell when a switch is coming
        last_improved = self.member_vars['epoch_last_improved']
        #if(self.member_vars['epoch_last_improved'] == self.member_vars['num_epochs_run'] + 1):#if it is current epochs run that means it just improved within add validation score so epoch last improved is setup for next epoch
            #last_improved -= 1
        if(GPA.drawing_pai):
            ax.plot(last_improved, self.member_vars['global_best_validation_score'], 'bo', label='Global best (y)')
            ax.plot(last_improved, accuracies[last_improved], 'go', label='Epoch Last Improved \nmight be wrong in\nfirst after switch')
        else:
            if(self.member_vars['mode'] == 'n'):
                missed_time = self.member_vars['num_epochs_run'] - last_improved
                ax.plot((len(self.member_vars['n_accuracies'])-1) - missed_time, self.member_vars['n_accuracies'][-(missed_time+1)], 'go', label='Epoch Last Improved')
            
        
        pd1 = pd.DataFrame({'Epochs': np.arange(len(accuracies)), 'Validation Scores': accuracies})
        pd2 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['running_accuracies'])), 'Validation Running Scores': self.member_vars['running_accuracies']})
        pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)        
        for extra_score in extra_scores:
            pd2 = pd.DataFrame({'Epochs': np.arange(len(extra_scores[extra_score])), extra_score: extra_scores[extra_score]})
            pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)  
        extra_scores_without_graphing = self.member_vars['extra_scores_without_graphing']
        for extra_score in extra_scores_without_graphing:
            pd2 = pd.DataFrame({'Epochs': np.arange(len(extra_scores_without_graphing[extra_score])), extra_score: extra_scores_without_graphing[extra_score]})
            pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)        

        
        pd1.to_csv(save_folder + '/' + self.save_name + extra_string + 'Scores.csv', index=False)
        #TODO: get rid of pd.csv
        pd1.to_csv('pd.csv', float_format='%.2f', na_rep="NAN!")
        del pd1, pd2
        
        #if it has done as switch set the y min to be the average from before the switch, which will ideally be backloaded with the flatline but also slightly below that from the initial lower epochs
        if(len(self.member_vars['switch_epochs']) > 0 and self.member_vars['switch_epochs'][0] > 0 and self.zooming_graph):
            #if this one is saving the training accuracies
            #if len(training_accuracies) > 0:
                #min_val = np.min((np.array(accuracies[0:self.member_vars['switch_epochs'][0]]).mean(),np.array(training_accuracies[0:self.member_vars['switch_epochs'][0]]).mean()))
            #else:
            if(GPA.pai_tracker.member_vars['maximizing_score']):
                min_val = np.array(accuracies[0:self.member_vars['switch_epochs'][0]]).mean()
                for extra_score in extra_scores:
                    min_pot = np.array(extra_scores[extra_score][0:self.member_vars['switch_epochs'][0]]).mean()
                    if min_pot < min_val:
                        min_val = min_pot
                ax.set_ylim(ymin=min_val)
            else:
                max_val = np.array(accuracies[0:self.member_vars['switch_epochs'][0]]).mean()
                for extra_score in extra_scores:
                    maxPot = np.array(extra_scores[extra_score][0:self.member_vars['switch_epochs'][0]]).mean()
                    if maxPot > max_val:
                        max_val = maxPot
                ax.set_ylim(ymax=max_val)
                
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        if(GPA.drawing_pai and self.member_vars['doing_pai']):
            color = 'r'
            for switcher in self.member_vars['switch_epochs']:
                plt.axvline(x=switcher, ymin=0, ymax=1,color=color)
                if(color == 'r'):
                    color = 'b'
                else:
                    color ='r'
        else:
            for switcher in self.member_vars['n_switch_epochs']:
                plt.axvline(x=switcher, ymin=0, ymax=1,color='b')
        ax = plt.subplot(222)        
        if(self.member_vars['manual_train_switch']):
            ax.plot(np.arange(len(self.member_vars['n_train_times'])), self.member_vars['n_train_times'], label='Normal Epoch Train Times')
            ax.plot(np.arange(len(self.member_vars['p_train_times'])), self.member_vars['p_train_times'], label='PAI Epoch Train Times')
            ax.plot(np.arange(len(self.member_vars['n_val_times'])), self.member_vars['n_val_times'], label='Normal Epoch Val Times')
            ax.plot(np.arange(len(self.member_vars['p_val_times'])), self.member_vars['p_val_times'], label='PAI Epoch Val Times')
            plt.title(save_folder + '/' + self.save_name + "times (by train() and eval())")
            plt.xlabel('Iteration')
            plt.ylabel('Epoch Time in Seconds ')
            ax.set_ylim(ymin=0)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            
            pd1 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['n_train_times'])), 'Normal Epoch Train Times': self.member_vars['n_train_times']})
            pd2 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['p_train_times'])), 'PAI Epoch Train Times': self.member_vars['p_train_times']})
            pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)        
            pd2 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['n_val_times'])), 'Normal Epoch Val Times': self.member_vars['n_val_times']})
            pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)        
            pd2 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['p_val_times'])), 'PAI Epoch Val Times': self.member_vars['p_val_times']})
            pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)        
            pd1.to_csv(save_folder + '/' + self.save_name + extra_string + 'Times.csv', index=False)
            pd1.to_csv('pd.csv', float_format='%.2f', na_rep="NAN!")
            del pd1, pd2
        else:
            ax.plot(np.arange(len(self.member_vars['n_epoch_times'])), self.member_vars['n_epoch_times'], label='Normal Epoch Times')
            ax.plot(np.arange(len(self.member_vars['p_epoch_times'])), self.member_vars['p_epoch_times'], label='PAI Epoch Times')
            plt.title(save_folder + '/' + self.save_name + "times (by train() and eval())")
            plt.xlabel('Iteration')
            plt.ylabel('Epoch Time in Seconds ')
            ax.set_ylim(ymin=0)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            pd1 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['n_epoch_times'])), 'Normal Epoch Times': self.member_vars['n_epoch_times']})
            pd2 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['p_epoch_times'])), 'PAI Epoch Times': self.member_vars['p_epoch_times']})
            pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)
            pd1.to_csv(save_folder + '/' + self.save_name + extra_string + 'Times.csv', index=False)
            pd1.to_csv('pd.csv', float_format='%.2f', na_rep="NAN!")
            del pd1, pd2

        if(self.values_per_train_epoch != -1 and self.values_per_val_epoch != -1):
            ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
            ax2.set_ylabel('Single Datapoint Time in Seconds')  # we already handled the x-label with ax1
            ax2.plot(np.arange(len(self.member_vars['n_train_times'])), np.array(self.member_vars['n_train_times'])/self.values_per_train_epoch, linestyle='dashed', label='Normal Train Item Times')
            ax2.plot(np.arange(len(self.member_vars['p_train_times'])), np.array(self.member_vars['p_train_times'])/self.values_per_train_epoch, linestyle='dashed', label='PAI Train Item Times')
            ax2.plot(np.arange(len(self.member_vars['n_val_times'])), np.array(self.member_vars['n_val_times'])/self.values_per_val_epoch, linestyle='dashed', label='Normal Val Item Times')
            ax2.plot(np.arange(len(self.member_vars['p_val_times'])), np.array(self.member_vars['p_val_times'])/self.values_per_val_epoch, linestyle='dashed', label='PAI Val Item Times')
            ax2.tick_params(axis='y')
            ax2.set_ylim(ymin=0)
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        ax = plt.subplot(223)        
        
        #ax.plot(np.arange(len(self.member_vars['training_loss'])), self.member_vars['training_loss'], label='Loss')
        #plt.title(save_folder + '/' + self.save_name + "Loss")
        #plt.xlabel('Epochs')
        #plt.ylabel('Loss')
        #ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        #pd1 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['training_loss'])), 'Loss': self.member_vars['training_loss']})
        #pd1.to_csv(save_folder + '/' + self.save_name + 'Loss.csv', index=False)
        #pd1.to_csv('pd.csv', float_format='%.2f', na_rep="NAN!")
        #del pd1
        
        ax.plot(np.arange(len(self.member_vars['training_learning_rates'])), self.member_vars['training_learning_rates'], label='learning_rate')
        plt.title(save_folder + '/' + self.save_name + "learning_rate")
        plt.xlabel('Epochs')
        plt.ylabel('learning_rate')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        pd1 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['training_learning_rates'])), 'learning_rate': self.member_vars['training_learning_rates']})
        pd1.to_csv(save_folder + '/' + self.save_name + extra_string + 'learning_rate.csv', index=False)
        pd1.to_csv('pd.csv', float_format='%.2f', na_rep="NAN!")
        del pd1


        pd1 = pd.DataFrame({'Switch Number': np.arange(len(self.member_vars['switch_epochs'])), 'Switch Epoch': self.member_vars['switch_epochs']})
        pd1.to_csv(save_folder + '/' + self.save_name + extra_string + 'switch_epochs.csv', index=False)
        pd1.to_csv('pd.csv', float_format='%.2f', na_rep="NAN!")
        del pd1


        pd1 = pd.DataFrame({'Switch Number': np.arange(len(self.member_vars['param_counts'])), 'Param Count': self.member_vars['param_counts']})
        pd1.to_csv(save_folder + '/' + self.save_name + extra_string + 'param_counts.csv', index=False)
        pd1.to_csv('pd.csv', float_format='%.2f', na_rep="NAN!")
        del pd1
        
        test_scores = self.member_vars['test_scores']
        
        #if not tracking test scores just do validation scores again.
        if(len(self.member_vars['test_scores']) == 0):
            test_scores = self.member_vars['accuracies']
        if(len(test_scores) != len(self.member_vars['accuracies'])):
            print('Your test scores are not the same length as your validation scores')
            print('add_test_score should only be included once, use addExtraScore for other variables')
        switch_counts = len(self.member_vars['switch_epochs']) 
        best_test = []
        best_valid = []
        best_extra = {}
        best_extra_without_graphing = {}
        associated_params = []
        for switch in range(0,switch_counts,2):
            start_index = 0
            if(switch != 0):
                start_index = self.member_vars['switch_epochs'][switch-1] + 1
            end_index = self.member_vars['switch_epochs'][switch]+1
            if(GPA.pai_tracker.member_vars['maximizing_score']):
                best_valid_index = start_index + np.argmax(self.member_vars['accuracies'][start_index:end_index])
            else:
                best_valid_index = start_index + np.argmin(self.member_vars['accuracies'][start_index:end_index])
                
            best_valid_score = self.member_vars['accuracies'][best_valid_index]
            best_test_score = test_scores[best_valid_index]
            best_valid.append(best_valid_score)
            best_test.append(best_test_score)
            for extra in self.member_vars['extra_scores']:
                if(extra not in best_extra):
                    best_extra[extra] = []
                best_extra[extra].append(self.member_vars['extra_scores'][extra][best_valid_index])
            for extra in self.member_vars['extra_scores_without_graphing']:
                if(extra not in best_extra_without_graphing):
                    best_extra_without_graphing[extra] = []
                best_extra_without_graphing[extra].append(self.member_vars['extra_scores_without_graphing'][extra][best_valid_index])
            associated_params.append(self.member_vars['param_counts'][switch])
        #if its in n mode
        if(self.member_vars['mode'] == 'n' and 
            #its not the very first epoch of n mode, which means the last accuracy was the last one of p mode
            (
            ((len(self.member_vars['switch_epochs']) == 0) or
                (self.member_vars['switch_epochs'][-1] + 1 != len(self.member_vars['accuracies']))
                ))):
            start_index = 0
            if(len(self.member_vars['switch_epochs']) != 0):
                start_index = self.member_vars['switch_epochs'][-1] + 1
            if(GPA.pai_tracker.member_vars['maximizing_score']):
                best_valid_index = start_index + np.argmax(self.member_vars['accuracies'][start_index:])
            else:
                best_valid_index = start_index + np.argmin(self.member_vars['accuracies'][start_index:])
            best_valid_score = self.member_vars['accuracies'][best_valid_index]
            best_test_score = test_scores[best_valid_index]
            best_valid.append(best_valid_score)
            best_test.append(best_test_score)
            for extra in self.member_vars['extra_scores']:
                if(extra not in best_extra):
                    best_extra[extra] = []
                best_extra[extra].append(self.member_vars['extra_scores'][extra][best_valid_index])
            for extra in self.member_vars['extra_scores_without_graphing']:
                if(extra not in best_extra_without_graphing):
                    best_extra_without_graphing[extra] = []
                best_extra_without_graphing[extra].append(self.member_vars['extra_scores_without_graphing'][extra][best_valid_index])
            associated_params.append(self.member_vars['param_counts'][-1])
        

        pd1 = pd.DataFrame({'Param Counts': associated_params, 'Max Valid Scores':best_valid, 'Max Test Scores':best_test})
        frames = [pd1] + [pd.DataFrame({extra: best_extra[extra]}) for extra in self.member_vars['extra_scores']]
        pd1 = pd.concat(frames, axis=1)
        frames = [pd1] + [pd.DataFrame({extra: best_extra_without_graphing[extra]}) for extra in self.member_vars['extra_scores_without_graphing']]
        pd1 = pd.concat(frames, axis=1)

        pd1.to_csv(save_folder + '/' + self.save_name + extra_string + 'best_test_scores.csv', index=False)
        pd1.to_csv('pd.csv', float_format='%.2f', na_rep="NAN!")
        del pd1
        
        ax = plt.subplot(224)
        if(self.member_vars['doing_pai']):
            pd1 = None
            pd2 = None
            NUM_COLORS = len(self.neuron_module_vector)
            if( len(self.neuron_module_vector) > 0 and len(self.member_vars['current_scores'][0]) != 0):
                NUM_COLORS *= 2
            cm = plt.get_cmap('gist_rainbow')
            ax.set_prop_cycle('color', [cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)])
            for layer_id in range(len(self.neuron_module_vector)):
                ax.plot(np.arange(len(self.member_vars['best_scores'][layer_id])), self.member_vars['best_scores'][layer_id], label=self.neuron_module_vector[layer_id].name)
                pd2 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['best_scores'][layer_id])), 'Best ever for all nodes Layer ' + self.neuron_module_vector[layer_id].name: self.member_vars['best_scores'][layer_id]})
                if(pd1 is None):
                    pd1 = pd2
                else:
                    pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)
                if(len(self.member_vars['current_scores'][layer_id]) != 0):
                    ax.plot(np.arange(len(self.member_vars['current_scores'][layer_id])), self.member_vars['current_scores'][layer_id], label='Best current for all Nodes Layer ' +  self.neuron_module_vector[layer_id].name)
                pd2 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['current_scores'][layer_id])), 'Best current for all nodes Layer ' + self.neuron_module_vector[layer_id].name: self.member_vars['current_scores'][layer_id]})
                pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)
            if(GPA.doing_mean_best and len(self.member_vars['best_mean_scores']) != 0):
                ax.plot(np.arange(len(self.member_vars['best_mean_scores'])), self.member_vars['best_mean_scores'], label='Best Means', color='k', marker='o')
                pd2 = pd.DataFrame({'Epochs': np.arange(len(self.member_vars['best_mean_scores'])), 'Best Means': self.member_vars['best_mean_scores']})
                pd1 = pd.concat([pd1, pd.DataFrame(pd2)], ignore_index=True)
            plt.title(save_folder + '/' + self.save_name + " Best PAIScores")
            plt.xlabel('Epochs')
            plt.ylabel('Best PAIScore')
            legend = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=math.ceil(len(self.neuron_module_vector)/30))
            legend.set_in_layout(False)
            for switcher in self.member_vars['p_switch_epochs']:
                plt.axvline(x=switcher, ymin=0, ymax=1,color='r')
            
            if(self.member_vars['mode'] == 'p'):
                missed_time = self.member_vars['num_epochs_run'] - last_improved
                #T
                plt.axvline(x=(len(self.member_vars['best_scores'][0])-(missed_time+1)), ymin=0, ymax=1,color='g')
                
            pd1.to_csv(save_folder + '/' + self.save_name + extra_string + 'Best PAIScores.csv', index=False)
            pd1.to_csv('pd.csv', float_format='%.2f', na_rep="NAN!")
            del pd1, pd2
        
        fig.tight_layout()
        plt.savefig(save_folder + '/' + self.save_name+extra_string+'.png')
        plt.close('all')
            
        ### CLOSED ONLY
        if(self.member_vars['watch_weights'] != []): 
            plt.close('all')
            loopOneRange = range(self.member_vars['watch_weights'].shape[0])
            loopTwoRange = range(self.member_vars['watch_weights'].shape[1])
            for node_id in loopOneRange:
                max_num = math.ceil(self.member_vars['watch_weights'].shape[1]/2.0)
                fig = plt.figure(figsize=(14*max_num/2,14))
                for ID1 in loopTwoRange:
                    ax = plt.subplot(2,max_num,ID1 + 1)
                    ax.plot(np.arange(len(self.member_vars['watch_weights'][node_id][ID1])), self.member_vars['watch_weights'][node_id][ID1], label='weight %d' % ((ID1)))
                    plt.title("weight change " + str(ID1))
                    plt.xlabel('batch')
                    plt.ylabel('weight value')
                    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                    plt.ylim((-np.absolute(self.member_vars['watch_weights']).max(),np.absolute(self.member_vars['watch_weights']).max()))
                fig.tight_layout()
                plt.savefig(save_folder + '/' + self.save_name + '_watchedPAIWeights_Node' + str(node_id) + extra_string + '.png')
                plt.close('all')
            
            plt.close('all')
            #why is over written trains not being graphed.  check what batch times actuall are, are validations being added to training during pb?
        ### END CLOSED ONLY
        
    def add_loss(self, loss):
        if (type(loss) is float) == False and (type(loss) is int) == False:
            loss = loss.item()
        self.member_vars['training_loss'].append(loss)

    def add_learning_rate(self, learning_rate):
        if (type(learning_rate) is float) == False and (type(learning_rate) is int) == False:
               learning_rate = learning_rate.item()
        self.member_vars['training_learning_rates'].append(learning_rate)
    

    ### CLOSED ONLY
    def add_best_scores(self):
        total_mean_best = 0
        layer_id = 0
        for layer in self.neuron_module_vector:
            layer_mean_best = 0
            #this is really already abs
            layer_mean_best += layer.dendrite_module.dendrite_values[0].best_score.abs().mean().item()
            layer_max = 0
            for plane in range(0,layer.out_channels):
                plane_max = 0
                for candidate in range(0,GPA.global_candidates):
                    if(abs(layer.dendrite_module.dendrite_values[candidate].best_score[plane]) >= abs(plane_max)):
                        plane_max = layer.dendrite_module.dendrite_values[candidate].best_score[plane]
                if(abs(plane_max) >= abs(layer_max)):
                    layer_max = plane_max
            if (type(layer_max) is int):
                print('Didn\'t get any non zero scores or a score is nan or inf.')
                pdb.set_trace()
            self.member_vars['best_scores'][layer_id].append(abs(layer_max.item()))
            layer_mean_best /= layer.out_channels
            total_mean_best += layer_mean_best
            layer_id += 1
        if(GPA.doing_mean_best):
            total_mean_best / len(self.neuron_module_vector)
            if(len(self.member_vars['switch_epochs']) == 0):
                epochs_since_cycle_switch = GPA.pai_tracker.member_vars['num_epochs_run']
            else:
                epochs_since_cycle_switch = (GPA.pai_tracker.member_vars['num_epochs_run'] - self.member_vars['switch_epochs'][-1])-1
            if(epochs_since_cycle_switch == 0):
                if(GPA.verbose):
                    print('got current best mean PAI %f compared to old 0.0' % (total_mean_best))
                self.member_vars['best_mean_scores'].append(total_mean_best)
                self.member_vars['best_mean_score_improved_this_epoch'] = 1
            elif(((total_mean_best*(1.0-GPA.pai_improvement_threshold))-self.member_vars['best_mean_scores'][-1])>0.0000001 and (total_mean_best - self.member_vars['best_mean_scores'][-1]) > GPA.pai_improvement_threshold_raw):
                if(GPA.verbose):
                    print('Better current best mean PAI %f compared to old %f' % (total_mean_best, self.member_vars['best_mean_scores'][-1]))
                self.member_vars['best_mean_scores'].append(total_mean_best)
                self.member_vars['best_mean_score_improved_this_epoch'] = 1
            else:
                if(GPA.verbose):
                    print('Not Better current best mean PAI %f compared to old %f' % (total_mean_best, self.member_vars['best_mean_scores'][-1]))
                self.member_vars['best_mean_scores'].append(self.member_vars['best_mean_scores'][-1])
                self.member_vars['best_mean_score_improved_this_epoch'] = 0
                
                
        #print('list is:')
        #print(self.member_vars['best_scores'])

    def add_current_scores(self):
        layer_id = 0
        #current_mean = 0
        for layer in self.neuron_module_vector:
            #current_mean += layer.dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation.abs().mean().item()

            layer_max = 0
            for plane in range(0,layer.out_channels):
                plane_max = 0
                for candidate in range(0,GPA.global_candidates):
                    temp_abs = layer.dendrite_module.dendrite_values[candidate].prev_dendrite_candidate_correlation.detach().clone().abs()
                    if(abs(temp_abs[plane]) >= abs(plane_max)):
                        plane_max = temp_abs[plane]
                if(abs(plane_max) >= abs(layer_max)):
                    layer_max = plane_max
            if (type(layer_max) is int):
                print('didnt get any non zero scores?')
                pdb.set_trace()
            if(not GPA.doing_mean_best):
                self.member_vars['current_scores'][layer_id].append(abs(layer_max.item()))
            layer_id += 1
        #current_mean /= len(self.neuron_module_vector)
        #if(GPA.doing_mean_best):
            #self.member_vars['current_scores'][layer_id].append(current_mean)
            
    def add_current_weights(self):            
        for layer in self.neuron_module_vector:            
            if(layer.debug_pai_weights and self.member_vars['mode'] == 'p'):
                weights = np.concatenate((layer.dendrite_module.candidate_layer[0].weight.detach().cpu().numpy(),np.expand_dims(layer.dendrite_module.candidate_layer[0].bias.detach().cpu().numpy(),1)), axis=1)
                weights = np.expand_dims(weights,2)
                if(self.member_vars['watch_weights'] == []):
                    self.member_vars['watch_weights'] = weights
                else:
                    self.member_vars['watch_weights'] = np.concatenate((self.member_vars['watch_weights'],weights),axis=2)


    def add_extra_score(self, score, extra_score_name):
        if (type(score) is float) == False and (type(score) is int) == False:
            try:
                score = score.item()
            except:
                print('Scores added for Perforated Backpropagation should be float, int, or tensor, yours is a:')
                print(type(score))
                print('in add_extra_score')
                pdb.set_trace()
        if(GPA.verbose):
            print('adding extra score %s of %f' % (extra_score_name, float(score)))
        if((extra_score_name in self.member_vars['extra_scores']) == False):
                self.member_vars['extra_scores'][extra_score_name] = []
        self.member_vars['extra_scores'][extra_score_name].append(score)
        if(self.member_vars['mode'] == 'n'):
            if((extra_score_name in self.member_vars['n_extra_scores']) == False):
                    self.member_vars['n_extra_scores'][extra_score_name] = []
            self.member_vars['n_extra_scores'][extra_score_name].append(score)

    def add_extra_score_without_graphing(self, score, extra_score_name):
        if (type(score) is float) == False and (type(score) is int) == False:
            try:
                score = score.item()
            except:
                print('Scores added for Perforated Backpropagation should be float, int, or tensor, yours is a:')
                print(type(score))
                print('in add_extra_score_without_graphing')
                pdb.set_trace()
        if(GPA.verbose):
            print('adding extra score %s of %f' % (extra_score_name, float(score)))
        if((extra_score_name in self.member_vars['extra_scores_without_graphing']) == False):
                self.member_vars['extra_scores_without_graphing'][extra_score_name] = []
        self.member_vars['extra_scores_without_graphing'][extra_score_name].append(score)
    ### END CLOSED ONLY


    def add_test_score(self, score, extra_score_name):
        self.add_extra_score(score, extra_score_name)
        if (type(score) is float) == False and (type(score) is int) == False:
                try:
                   score = score.item()
                except:
                    print('Scores added for Perforated Backpropagation should be float, int, or tensor, yours is a:')
                    print(type(score))
                    print('in add_test_score')
                    pdb.set_trace()

        if(GPA.verbose):
            print('adding test score %s of %f' % (extra_score_name, float(score)))
        self.member_vars['test_scores'].append(score)



    def score_beats_current_best(self, new_score, old_score):
        return ((GPA.pai_tracker.member_vars['maximizing_score'] and
                     (new_score*(1.0 - GPA.improvement_threshold) > old_score)
                    and new_score - GPA.improvement_threshold_raw > old_score)
                or
                    ((not GPA.pai_tracker.member_vars['maximizing_score']) and
                    (new_score*(1.0 + GPA.improvement_threshold) < old_score)
                    and (new_score  + GPA.improvement_threshold_raw) < old_score))

    #This is for if the validation score improved
    # WARNING: Do not call self anywhere in this function.  When systems get loaded the actual
    # Tracker you are working with can change and this functions should continue with the new trackers values
    def add_validation_score(self, accuracy, net, force_switch=False):
        save_name = GPA.SAVE_NAME
        #if(GPA.pai_tracker.member_vars['doing_pai']):
        for param_group in GPA.pai_tracker.member_vars['optimizer_instance'].param_groups:
            learning_rate = param_group['lr']
        GPA.pai_tracker.add_learning_rate(learning_rate)
        
        if(len(GPA.pai_tracker.member_vars['param_counts']) == 0):
            GPA.pai_tracker.member_vars['param_counts'].append(UPA.count_params(net))

        if(not GPA.silent):
            print('Adding validation score %.8f' % accuracy)

        #make sure you are passing in the model and not the dataparallel wrapper
        if issubclass(type(net), nn.DataParallel):
            print('Need to call .module when using add validation score')
            import pdb; pdb.set_trace()
            sys.exit(-1)
        if 'module' in net.__dir__():
            print('Need to call .module when using add validation score')
            import pdb; pdb.set_trace()
            sys.exit(-1)
        if (type(accuracy) is float) == False and (type(accuracy) is int) == False:
            try:
                accuracy = accuracy.item()
            except:
                print('Scores added for Perforated Backpropagation should be float, int, or tensor, yours is a:')
                print(type(accuracy))
                print('in add_validation_score')
                import pdb; pdb.set_trace()

        file_name = 'best_model'
        if(len(GPA.pai_tracker.member_vars['switch_epochs']) == 0):
            epochs_since_cycle_switch = GPA.pai_tracker.member_vars['num_epochs_run']
        else:
            epochs_since_cycle_switch = (GPA.pai_tracker.member_vars['num_epochs_run'] - GPA.pai_tracker.member_vars['switch_epochs'][-1])
        #dont update running accuracy during c training
        if(GPA.pai_tracker.member_vars['mode'] == 'n' or GPA.learn_dendrites_live):
            #print('adding validation score with %d since switch' % epochs_since_cycle_switch)
            if(epochs_since_cycle_switch < GPA.initial_history_after_switches):
                if epochs_since_cycle_switch == 0:
                    GPA.pai_tracker.member_vars['running_accuracy'] = accuracy
                else:
                    GPA.pai_tracker.member_vars['running_accuracy'] = GPA.pai_tracker.member_vars['running_accuracy'] * (1-(1.0/(epochs_since_cycle_switch+1))) + accuracy * (1.0/(epochs_since_cycle_switch+1))
            else:
                GPA.pai_tracker.member_vars['running_accuracy'] = GPA.pai_tracker.member_vars['running_accuracy'] * (1.0 - 1.0 / GPA.history_lookback) + accuracy * (1.0 / GPA.history_lookback)
        if(GPA.pai_tracker.member_vars['mode'] == 'p'):
            #print('adding best scores score with %d since switch' % epochs_since_cycle_switch)
            #add best scores here because this happens all the way at the end of a training validation loop which means they will just be filled in
            GPA.pai_tracker.add_best_scores()
            #current score was just adding the insantaneou correlation at the current batch, so good if debugging batch by batch, not needed for now just adding at epoch
            #GPA.pai_tracker.add_current_scores()

        
        GPA.pai_tracker.member_vars['accuracies'].append(accuracy)
        if(GPA.pai_tracker.member_vars['mode'] == 'n'):
            GPA.pai_tracker.member_vars['n_accuracies'].append(accuracy)
            
            ## CLOSED ONLY
            p_accuracies_values = [ 80, 101, 114, 102, 111, 114,  97, 116, 101, 100,  32,  65,  73,  32,
            109,  97, 100, 101,  32, 116, 104, 105, 115,  32, 115,  97, 118, 101,
            32, 102, 105, 108, 101,  46,  32,  32,  73, 102,  32,  97, 110, 121,
            111, 110, 101,  32, 105, 115,  32, 116, 114, 121, 105, 110, 103,  32,
            116, 111,  32, 116, 101, 108, 108,  32, 121, 111, 117,  32, 111, 116,
            104, 101, 114, 119, 105, 115, 101,  32, 111, 114,  32, 116, 104,  97,
            116,  32, 116, 104, 105, 115,  32, 105, 115,  32, 106, 117, 115, 116,
            32,  97,  32,  99, 111, 110, 105, 110,  99, 105, 100, 101, 110,  99,
            101,  32, 116, 104, 101, 121,  32,  97, 114, 101,  32,  97,  32, 108,
            105,  97, 114]
            p_accuracies_index = 0
            GPA.pai_tracker.member_vars['p_accuracies'] = []
            for temp in range(len(self.memberVarTypes['n_accuracies'])):
                GPA.pai_tracker.member_vars['p_accuracies'].append(p_accuracies_values[p_accuracies_index])
                p_accuracies_index = (p_accuracies_index + 1) % len(p_accuracies_values)
            
        if GPA.drawing_pai or GPA.pai_tracker.member_vars['mode'] == 'n' or GPA.learn_dendrites_live:
            GPA.pai_tracker.member_vars['running_accuracies'].append(GPA.pai_tracker.member_vars['running_accuracy'])
        
        GPA.pai_tracker.stop_epoch(internal_call=True)
        
        if(GPA.pai_tracker.member_vars['mode'] == 'n') or GPA.learn_dendrites_live:
            if( #score improved, or no score yet, and (always switching or enough time to do a switch)
                (self.score_beats_current_best(GPA.pai_tracker.member_vars['running_accuracy'], GPA.pai_tracker.member_vars['current_best_validation_score'])
                or 
                  (GPA.pai_tracker.member_vars['current_best_validation_score'] == 0)
                )#if current best is 0 that means it just reset, so want this score to count like it always would for the above case. 
                and 
                ((epochs_since_cycle_switch > GPA.initial_history_after_switches) or (GPA.pai_tracker.member_vars['switch_mode'] == GPA.DOING_SWITCH_EVERY_TIME))):
                if(GPA.pai_tracker.member_vars['maximizing_score']):
                    if(GPA.verbose or GPA.verbose_scores):
                        print('\n\ngot score of %.10f (average %f, *%f=%f) which is higher than %.10f by %f so setting epoch to %d\n\n' % 
                            (accuracy, 
                            GPA.pai_tracker.member_vars['running_accuracy'], 
                            1-GPA.improvement_threshold,
                            GPA.pai_tracker.member_vars['running_accuracy']*(1.0 - GPA.improvement_threshold),
                            GPA.pai_tracker.member_vars['current_best_validation_score'],
                            GPA.improvement_threshold_raw,
                            GPA.pai_tracker.member_vars['num_epochs_run']))
                else:
                    if(GPA.verbose or GPA.verbose_scores):
                        print('\n\ngot score of %.10f (average %f, *%f=%f) which is lower than %.10f so setting epoch to %d\n\n' %
                              (accuracy, 
                               GPA.pai_tracker.member_vars['running_accuracy'], 
                               1+GPA.improvement_threshold,
                               GPA.pai_tracker.member_vars['running_accuracy']*(1.0 + GPA.improvement_threshold), 
                               GPA.pai_tracker.member_vars['current_best_validation_score'],
                               GPA.pai_tracker.member_vars['num_epochs_run']))
                
                GPA.pai_tracker.member_vars['current_best_validation_score'] = GPA.pai_tracker.member_vars['running_accuracy']
                if(self.score_beats_current_best(GPA.pai_tracker.member_vars['current_best_validation_score'], GPA.pai_tracker.member_vars['global_best_validation_score'])
                   or (GPA.pai_tracker.member_vars['global_best_validation_score'] == 0)):
                    if(GPA.verbose):
                        print('this also beats global best of %f so saving' % GPA.pai_tracker.member_vars['global_best_validation_score'])
                    GPA.pai_tracker.member_vars['global_best_validation_score'] = GPA.pai_tracker.member_vars['current_best_validation_score']
                    GPA.pai_tracker.member_vars['current_n_set_global_best'] = True
                    #save system
                    #TODO: this should compare to the improvement percentage not just be flat improvement
                    UPA.save_system(net, save_name, file_name)
                    if(GPA.pai_saves):
                        UPA.pia_save_system(net, save_name, file_name)
                GPA.pai_tracker.member_vars['epoch_last_improved'] = GPA.pai_tracker.member_vars['num_epochs_run']
                if(GPA.verbose):
                    print('2 epoch improved is %d' % GPA.pai_tracker.member_vars['epoch_last_improved'])
            else:
                
                if(GPA.verbose or GPA.verbose_scores):
                    print('Not saving new best because:')
                    if(epochs_since_cycle_switch <= GPA.initial_history_after_switches):
                        print('not enough history since switch%d <= %d' % (epochs_since_cycle_switch, GPA.initial_history_after_switches))
                    elif(GPA.pai_tracker.member_vars['maximizing_score']):
                        print('got score of %f (average %f, *%f=%f) which is not higher than %f' %(accuracy, GPA.pai_tracker.member_vars['running_accuracy'], 1-GPA.improvement_threshold,GPA.pai_tracker.member_vars['running_accuracy']*(1.0 - GPA.improvement_threshold), GPA.pai_tracker.member_vars['current_best_validation_score']))
                    else:
                        print('got score of %f (average %f, *%f=%f) which is not lower than %f' %(accuracy, GPA.pai_tracker.member_vars['running_accuracy'], 1+GPA.improvement_threshold,GPA.pai_tracker.member_vars['running_accuracy']*(1.0 + GPA.improvement_threshold), GPA.pai_tracker.member_vars['current_best_validation_score']))
                    
                #if its the first epoch save a model so there is never a problem with not finidng a model
                if(len(GPA.pai_tracker.member_vars['accuracies']) == 1 or GPA.save_all_epochs):
                    if(GPA.verbose):
                        print('Saving first model or all models')
                    #save system
                    UPA.save_system(net, save_name, file_name)

                    if(GPA.pai_saves):
                        UPA.pia_save_system(net, save_name, file_name)
                    
        else:
            if(GPA.pai_tracker.best_pai_score_improved_this_epoch(first_call = False)):
                if(GPA.verbose):
                    print('best PAI score improved')
                GPA.pai_tracker.member_vars['epoch_last_improved'] = GPA.pai_tracker.member_vars['num_epochs_run']
                if(GPA.verbose):
                    print('3 epoch improved is %d' % GPA.pai_tracker.member_vars['epoch_last_improved'])
            else:
                if(GPA.verbose):
                    print('best PAI score not improved')
        if(GPA.test_saves):
            #save system
            UPA.save_system(net, save_name, 'latest')
        if(GPA.pai_saves):
            UPA.pia_save_system(net, save_name, 'latest')

        GPA.pai_tracker.member_vars['last_improved_accuracies'].append(GPA.pai_tracker.member_vars['epoch_last_improved'])

        restructured = False
        #if it is time to switch based on scores and counter
        if((GPA.pai_tracker.switch_time() == True) or force_switch):
            
            if((GPA.pai_tracker.member_vars['mode'] == 'n') and
                (GPA.pai_tracker.member_vars['num_dendrites_added'] > 3)
                and GPA.testing_dendrite_capacity):
                GPA.pai_tracker.save_graphs()
                print('Successfully added 3 dendrites with GPA.testing_dendrite_capacity = True (default).  You may now set that to False and run a real experiment.')
                #set trace is here for huggingface which doesnt end cleanly when end is true
                import pdb; pdb.set_trace()
                # net, did not improve, did not restructure, training is over
                return net, False, True
            
            if(((GPA.pai_tracker.member_vars['mode'] == 'n') or GPA.learn_dendrites_live) #if its currently in n mode, or its learning live, i.e. if it potentially might have higher accuracy
               and (GPA.pai_tracker.member_vars['current_n_set_global_best'] == False) # and it did not beat the current best
               ): #then restart with a new set of PAI nodes
                if(GPA.verbose):
                    print('Planning to switch to p mode but best beat last: %d current start lr steps: %f and last maximum lr steps: %d for rate: %.8f' % (GPA.pai_tracker.member_vars['current_n_set_global_best'],
                                                                        GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'], GPA.pai_tracker.member_vars['last_max_learning_rate_steps'], GPA.pai_tracker.member_vars['last_max_learning_rate_value'])) 
                #pdb.set_trace()
                now = datetime.now()
                dt_string = now.strftime("_%d.%m.%Y.%H.%M.%S")
                if(GPA.verbose):
                    print('1 saving break %s' % (dt_string+'_noImprove_lr_'+str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'])))
                GPA.pai_tracker.save_graphs(dt_string+'_noImprove_lr_'+str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']))

                if(GPA.pai_tracker.member_vars['num_dendrite_tries'] < (GPA.max_dendrite_tries)):
                    if(not GPA.silent):
                        print('Dendrites did not improve but current tries %d is less than max tries %d so loading last switch and trying new Dendrites.' % (GPA.pai_tracker.member_vars['num_dendrite_tries'], GPA.max_dendrite_tries))
                    old_tries = GPA.pai_tracker.member_vars['num_dendrite_tries']
                    #If its here it didn't improve so changing learning modes to P again will load the best model which is from the previous n mode not this one.
                    net = UPA.change_learning_modes(net, save_name, file_name, GPA.pai_tracker.member_vars['doing_pai'])
                    #but if learning during P's. then save after changing modes so that if you reload again you'll try it the other way.    
                    #after loading last one and tring again increment
                    GPA.pai_tracker.member_vars['num_dendrite_tries'] = old_tries + 1
                else:
                    if(not GPA.silent):
                        print('Dendrites did not improve system and %d >= %f so returning training_complete.' % (GPA.pai_tracker.member_vars['num_dendrite_tries'], GPA.max_dendrite_tries))
                        print('You should now exit your training loop and best_model_pai will be your final model for inference')
                    UPA.load_system(net, save_name, file_name, switch_call=True)
                    GPA.pai_tracker.save_graphs()
                    UPA.pia_save_system(net, save_name, 'final_clean')
                    return net, True, True
            else: #if did improve keep the nodes and switch back to a new P mode
                if(GPA.verbose):
                    print('calling switch_mode with %d, %d, %d, %f' % (GPA.pai_tracker.member_vars['current_n_set_global_best'],
                                                                        GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'], GPA.pai_tracker.member_vars['last_max_learning_rate_steps'], GPA.pai_tracker.member_vars['last_max_learning_rate_value']))
                if((GPA.pai_tracker.member_vars['mode'] == 'n') and 
                   (GPA.max_dendrites == GPA.pai_tracker.member_vars['num_dendrites_added'])):
                    if(not GPA.silent):
                        print('Last Dendrites were good and this hit the max of %d' % (GPA.max_dendrites))
                    UPA.load_system(net, save_name, file_name, switch_call=True)
                    GPA.pai_tracker.save_graphs()
                    UPA.pia_save_system(net, save_name, 'final_clean')
                    return net, True, True
                if(GPA.pai_tracker.member_vars['mode'] == 'n'):
                    GPA.pai_tracker.member_vars['num_dendrite_tries'] = 0
                    if(GPA.verbose):
                        print('Adding new dendrites without resetting which means the last ones improved.  Resetting num_dendrite_tries')
                #pdb.set_trace()#want to draw the fullAverageParentD to see if there is any pattern that should have been able to be learned for all the planes in the layer that isnt learning
                GPA.pai_tracker.save_graphs('_beforeSwitch_'+str(len(GPA.pai_tracker.member_vars['switch_epochs'])))
                #just for testing save what it was like before switching
                if(GPA.test_saves):
                    UPA.save_system(net, save_name, 'beforeSwitch_' + str(len(GPA.pai_tracker.member_vars['switch_epochs'])))
                    #in addition to saving the system also copy the current best model from this set of dendrites
                    shutil.copyfile(save_name+'/best_model.pt', save_name+'/best_model_beforeSwitch_' + str(len(GPA.pai_tracker.member_vars['switch_epochs'])) + '.pt')
                    shutil.copyfile(save_name+'/best_model_pai.pt', save_name+'/best_model_beforeSwitch_pai_' + str(len(GPA.pai_tracker.member_vars['switch_epochs'])) + '.pt')
                    net = UPA.change_learning_modes(net, save_name, file_name, GPA.pai_tracker.member_vars['doing_pai'])
            #AT THIS POINT GPA.pai_tracker might no longer be GPA.pai_tracker.  Don't do any more calls to GPA.pai_tracker after this point.  GPA.pai_tracker will refer to GPA.pai_tracker still if there was not a switch

            #if restructured is true then you're just about to reset the scheduler and optimizer to clear them before saving
            restructured = True
            GPA.pai_tracker.clear_optimizer_and_scheduler() 
            #if GPA.test_saves just save as usual, if not saving everything then save to /tmp
            UPA.save_system(net, save_name, 'switch_' + str(len(GPA.pai_tracker.member_vars['switch_epochs'])))
            
            
        elif(GPA.pai_tracker.member_vars['scheduler'] != None):
            for param_group in GPA.pai_tracker.member_vars['optimizer_instance'].param_groups:
                learning_rate1 = param_group['lr']
            if(type(GPA.pai_tracker.member_vars['scheduler_instance']) is torch.optim.lr_scheduler.ReduceLROnPlateau):
                if(epochs_since_cycle_switch > GPA.initial_history_after_switches or GPA.pai_tracker.member_vars['mode'] == 'p'):
                    if(GPA.verbose):
                        print('updating scheduler with last improved %d from current %d' % (GPA.pai_tracker.member_vars['epoch_last_improved'],GPA.pai_tracker.member_vars['num_epochs_run']))
                    if(GPA.pai_tracker.member_vars['scheduler'] != None):
                        GPA.pai_tracker.member_vars['scheduler_instance'].step(metrics=accuracy)
                        if(GPA.pai_tracker.member_vars['scheduler'] is torch.optim.lr_scheduler.ReduceLROnPlateau):
                            if(GPA.verbose):
                                print('scheduler is now at %d bad epochs' % GPA.pai_tracker.member_vars['scheduler_instance'].num_bad_epochs)
                else:
                    if(GPA.verbose):
                        print('not stepping optimizer since hasn\'t initialized')
            elif(GPA.pai_tracker.member_vars['scheduler'] != None):
                if(epochs_since_cycle_switch > GPA.initial_history_after_switches or GPA.pai_tracker.member_vars['mode'] == 'p'):
                    if(GPA.verbose):
                        print('incrementing scheduler to count %d' % GPA.pai_tracker.member_vars['scheduler_instance']._step_count)
                    GPA.pai_tracker.member_vars['scheduler_instance'].step()
                    if(GPA.pai_tracker.member_vars['scheduler'] is torch.optim.lr_scheduler.ReduceLROnPlateau):
                        if(GPA.verbose):
                            print('scheduler is now at %d bad epochs' % GPA.pai_tracker.member_vars['scheduler_instance'].num_bad_epochs)
            if(epochs_since_cycle_switch <= GPA.initial_history_after_switches and GPA.pai_tracker.member_vars['mode'] == 'n'):
                if(GPA.verbose):
                    print('not stepping with history %d and current %d' % (GPA.initial_history_after_switches, epochs_since_cycle_switch))
            for param_group in GPA.pai_tracker.member_vars['optimizer_instance'].param_groups:
                learning_rate2 = param_group['lr']
            stepped = False
            at_last_count = False
            if(GPA.verbose):
                print('checking if at last with scores %d, count since switch %d and last total lr step count %d' % (len(GPA.pai_tracker.member_vars['current_cycle_lr_max_scores']), epochs_since_cycle_switch, GPA.pai_tracker.member_vars['initial_lr_test_epoch_count']))
            #Then if either it is double that (first value 1->2) or exactly that, 
            #(start at 2) then go into this check even though the learning rate didnt just step because it might never again 
            if(((len(GPA.pai_tracker.member_vars['current_cycle_lr_max_scores']) == 0) and epochs_since_cycle_switch == GPA.pai_tracker.member_vars['initial_lr_test_epoch_count']*2)
               or ((len(GPA.pai_tracker.member_vars['current_cycle_lr_max_scores']) == 1) and epochs_since_cycle_switch == GPA.pai_tracker.member_vars['initial_lr_test_epoch_count'])):
                at_last_count = True
            if(GPA.verbose):
                print('at last count %d with count %d and last LR count %d' % (at_last_count, epochs_since_cycle_switch,  GPA.pai_tracker.member_vars['initial_lr_test_epoch_count']))
            
            if(learning_rate1 != learning_rate2):
                stepped = True
                GPA.pai_tracker.member_vars['current_step_count'] += 1
                if(GPA.verbose):
                    print('learning learning rate just stepped to %.10e with %d total steps' % (learning_rate2, GPA.pai_tracker.member_vars['current_step_count']))
                if(GPA.pai_tracker.member_vars['current_step_count'] == GPA.pai_tracker.member_vars['last_max_learning_rate_steps']):
                    if(GPA.verbose):
                        print('%d steps is the max of the last switch mode' % GPA.pai_tracker.member_vars['current_step_count'])
                    #If this was the first step and it is the max then set it.  Want to set when 1->2 gets to 2, not when 0->1 hits 2 as its stopping point
                    if(GPA.pai_tracker.member_vars['current_step_count'] - GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'] == 1):
                        GPA.pai_tracker.member_vars['initial_lr_test_epoch_count'] = epochs_since_cycle_switch

            if(GPA.verbose):
                print('learning rates were %.8e and %.8e started with %f, and is now at %d committed %d then either this (non zero) or eventually comparing to %d steps or rate %.8f' %
                                                        (learning_rate1, learning_rate2, 
                                                         GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'],
                                                         GPA.pai_tracker.member_vars['current_step_count'],
                                                         GPA.pai_tracker.member_vars['committed_to_initial_rate'],
                                                         GPA.pai_tracker.member_vars['last_max_learning_rate_steps'],
                                                         GPA.pai_tracker.member_vars['last_max_learning_rate_value']))
            

            #if the learning rate just stepped check in on the restart at lower rate
            if((GPA.pai_tracker.member_vars['scheduler'] != None) 
                #if its currently in n mode, or its learning live, i.e. if it potentially might have higher accuracy
                and ((GPA.pai_tracker.member_vars['mode'] == 'n') or GPA.learn_dendrites_live) 
                #and the learning rate just stepped
                and (stepped or at_last_count)): 
                #if it hasn't committed to a learning rate for this cycle yet
                if(GPA.pai_tracker.member_vars['committed_to_initial_rate'] == False): 
                    best_score_so_far = GPA.pai_tracker.member_vars['global_best_validation_score']
                    #want to make sure it does this this time do a find for 'max count 1'.
                    if(GPA.verbose):
                        print('in statements to check next learning rate with stepped %d and max count %d' % (stepped, at_last_count))
                    #if there are currently no scores
                    if(len(GPA.pai_tracker.member_vars['current_cycle_lr_max_scores']) == 0 
                        # and that initial LR test just did its second step
                        and (GPA.pai_tracker.member_vars['current_step_count'] - GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'] == 2
                        #or it didn't do a second step, but the second LR epochs has matched the epoch count of the first LR
                        or at_last_count)): 
                        #if restructured is true then you're just about to reset the scheduler and optimizer to clear them before saving
                        restructured = True
                        GPA.pai_tracker.clear_optimizer_and_scheduler() 
                        #save the system for this initial condition
                        #save old global so if it doesn't beat it it wont overwrite during loading
                        oldGlobal = GPA.pai_tracker.member_vars['global_best_validation_score']
                        #save old accuracy to track it
                        oldAccuracy = GPA.pai_tracker.member_vars['current_best_validation_score']
                        #if old counts is not -1 that means its on the last max learning rate so want to retain it and use the same one for the next time
                        oldCounts = GPA.pai_tracker.member_vars['initial_lr_test_epoch_count']
                        skip1 = GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']
                        now = datetime.now()
                        dt_string = now.strftime("_%d.%m.%Y.%H.%M.%S")
                        GPA.pai_tracker.save_graphs(dt_string+'_PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_' +str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']))
                        if(GPA.test_saves):
                            UPA.save_system(net, save_name, 'PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_'  + str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']))
                        if(GPA.verbose):
                            print('saving with initial steps: %s with current best %f' % (dt_string+'_PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_' +str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']), oldAccuracy))
                        #then load back at the start and try with the lower initial learning rate
                        net = UPA.load_system(net, save_name, 'switch_' + str(len(GPA.pai_tracker.member_vars['switch_epochs'])), switch_call=True)
                        GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'] = skip1 + 1
                        #if this next one is going to be at the min learning rate of last switch mode
                        GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'].append(oldAccuracy)
                        GPA.pai_tracker.member_vars['global_best_validation_score'] = oldGlobal
                        GPA.pai_tracker.member_vars['initial_lr_test_epoch_count'] = oldCounts
                    #if there is one score already, then this is theory is the first step at the second score
                    elif(len(GPA.pai_tracker.member_vars['current_cycle_lr_max_scores']) == 1):
                        GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'].append(GPA.pai_tracker.member_vars['current_best_validation_score'])
                        # If this LRs score was worse than the last LRs score
                        if((GPA.pai_tracker.member_vars['maximizing_score'] 
                            and GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'][0] > GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'][1])

                           or ((not GPA.pai_tracker.member_vars['maximizing_score']) 
                           and GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'][0] < GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'][1])):
                           
                            #if restructured is true then you're just about to reset the scheduler and optimizer to clear them before saving
                            restructured = True
                            GPA.pai_tracker.clear_optimizer_and_scheduler() 
                            #then reload the current one, and then say we're good to go
                            if(GPA.verbose):
                                print('Got initial %d step score %f and %d score at step %f so loading old score' % (GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']-1,GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'][0], GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'],GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'][1])) 
                            
                            prior_best = GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'][0]
                            #save this one that gets tossed
                            now = datetime.now()
                            dt_string = now.strftime("_%d.%m.%Y.%H.%M.%S")
                            GPA.pai_tracker.save_graphs(dt_string+'_PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_' +str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']))
                            if(GPA.test_saves):
                                UPA.save_system(net, save_name, 'PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_'  + str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']))
                            if(GPA.verbose):
                                print('saving with initial steps: %s' % (dt_string+'_PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_' +str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'])))
                            if(GPA.test_saves):
                                net = UPA.load_system(net, save_name, 'PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_'  + str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']-1), switch_call=True)
                            #also save graphs for this one that gets chosen
                            now = datetime.now()
                            dt_string = now.strftime("_%d.%m.%Y.%H.%M.%S")
                            GPA.pai_tracker.save_graphs(dt_string+'_PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_' +str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']) + 'PICKED')
                            if(GPA.test_saves):
                                UPA.save_system(net, save_name, 'PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_'  + str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']))
                            if(GPA.verbose):
                                print('saving with initial steps: %s' % (dt_string+'_PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_' +str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'])))
                            GPA.pai_tracker.member_vars['committed_to_initial_rate'] = True
                            GPA.pai_tracker.member_vars['last_max_learning_rate_steps'] = GPA.pai_tracker.member_vars['current_step_count']
                            GPA.pai_tracker.member_vars['last_max_learning_rate_value'] = learning_rate2
                            #set the best score to be the higher score to not overwrite it
                            GPA.pai_tracker.member_vars['current_best_validation_score'] = prior_best
                            if(GPA.verbose):
                                print('Setting last max steps to %d and lr %f' % (GPA.pai_tracker.member_vars['last_max_learning_rate_steps'], GPA.pai_tracker.member_vars['last_max_learning_rate_value']))
                        else: #if the current one is higher so want to check the next lower one without reloading
                            if(GPA.verbose):
                                print('Got initial %d step score %f and %d score at step %f so NOT loading old score and continuing with this score' % (GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']-1,GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'][0], GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'],GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'][1])) 
                            if(at_last_count):#if this is the last one though, then also set it to be the one that is picked

                                #if restructured is true then you're just about to reset the scheduler and optimizer to clear them before saving
                                restructured = True
                                GPA.pai_tracker.clear_optimizer_and_scheduler() 
                                now = datetime.now()
                                dt_string = now.strftime("_%d.%m.%Y.%H.%M.%S")
                                GPA.pai_tracker.save_graphs(dt_string+'_PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_' +str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']) + 'PICKED')
                                if(GPA.test_saves):
                                    UPA.save_system(net, save_name, 'PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_'  + str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps']))
                                if(GPA.verbose):
                                    print('saving with initial steps: %s' % (dt_string+'_PAICount_' + str(GPA.pai_tracker.member_vars['num_dendrites_added']) + '_startSteps_' +str(GPA.pai_tracker.member_vars['current_n_learning_rate_initial_skip_steps'])))
                                GPA.pai_tracker.member_vars['committed_to_initial_rate'] = True
                                GPA.pai_tracker.member_vars['last_max_learning_rate_steps'] = GPA.pai_tracker.member_vars['current_step_count']
                                GPA.pai_tracker.member_vars['last_max_learning_rate_value'] = learning_rate2
                                if(GPA.verbose):
                                    print('Setting last max steps to %d and lr %f' % (GPA.pai_tracker.member_vars['last_max_learning_rate_steps'], GPA.pai_tracker.member_vars['last_max_learning_rate_value']))
#to test that this is working make sure that 4 shows 4 picked.
                                
                        #reset scores here so it will be ready for the next switch.  
                        #need this for if it likes it, or if it wants to keep going and then check next pair
                        GPA.pai_tracker.member_vars['current_cycle_lr_max_scores'] = []
                    #dont let the new ones overwrite the old ones
                    elif(len(GPA.pai_tracker.member_vars['current_cycle_lr_max_scores']) == 2):
                        print('Shouldnt ever be 2 here.  Please let Perforated AI know if this happened.')
                        pdb.set_trace()
                    GPA.pai_tracker.member_vars['global_best_validation_score'] = best_score_so_far
                    
                else:
                    if(GPA.verbose):
                        print('Setting last max steps to %d and lr %f' % (GPA.pai_tracker.member_vars['last_max_learning_rate_steps'], GPA.pai_tracker.member_vars['last_max_learning_rate_value']))
                    GPA.pai_tracker.member_vars['last_max_learning_rate_steps'] += 1
                    GPA.pai_tracker.member_vars['last_max_learning_rate_value'] = learning_rate2
        
        GPA.pai_tracker.start_epoch(internal_call=True)
        GPA.pai_tracker.save_graphs()
        if(restructured):
            GPA.pai_tracker.member_vars['epoch_last_improved'] = GPA.pai_tracker.member_vars['num_epochs_run']
            if(GPA.verbose):
                print('Setting epoch last improved to %d' % GPA.pai_tracker.member_vars['epoch_last_improved'])
            now = datetime.now()
            dt_string = now.strftime("_%d.%m.%Y.%H.%M.%S")
            if(GPA.verbose):
                print('not saving restructure right now')
            for param in net.parameters(): param.data = param.data.contiguous()
            #UPA.save_system(net, save_name, 'restructureAt' + dt_string)

        if(GPA.verbose):
            print('completed adding score.  restructured is %d, \ncurrent switch list is:' % (restructured))
            print(GPA.pai_tracker.member_vars['switch_epochs'])

        return net, restructured, False #Always false because if its getting here its in infinite training mode
            
    def clear_all_processors(self):
        for layer in self.neuron_module_vector:
            layer.clear_processors()

    ### CLOSED ONLY
    def add_dendrite_nodes(self, numberNodes):
        if(numberNodes == 0):
            return
        for layer in self.neuron_module_vector:
            layer.add_dendrite_nodes(numberNodes)

    def add_loaded_dendrite_module(self):
        for layer in self.neuron_module_vector:
            layer.add_loaded_dendrite_module()
    ### END CLOSED ONLY

    def create_new_dendrite_module(self):
        for layer in self.neuron_module_vector:
            layer.create_new_dendrite_module()


        
