# Copyright (c) 2025 Perforated AI
import math
import torch 
import torch.nn as nn
import torchvision.models.resnet as resnet
import sys

### Global Constants

# Device configuration
use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")

# Debug settings
debugging_memory_leak = True
debugging_input_dimensions = 0
# Debugging input tensor sizes.
# This will slow things down very slightly and is not necessary but can help
# catch when dimensions were not filled in correctly.
confirm_correct_sizes = False

# Confirmation flags for non-recommended options
unwrapped_modules_confirmed = False
#using_pia_data_parallel = False
weight_decay_accepted = False
count_training_params = False

checked_skipped_modules = False
no_backward_workaround = False

# Verbosity settings
verbose = False
# Suppress all PAI prints
silent = False

extra_verbose = False
dpp_verbose = False
verbose_scores = False

# Analysis settings
save_old_graph_scores = True

# Testing settings
testing_dendrite_capacity = True

# File format settings
using_safe_tensors = True

# In place for future implementation options of adding multiple candidate
# dendrites together
global_candidates = 1

#Prevent flow of error back to network after candidates and dendrites
doing_perferated_candidates = True
doing_perferated_dendrites = True
#Do Correlation learning
doing_cc = True
#Allow dendrite weights to continue to learn
update_dendrite_weights = False

internal_batch_norm = False
variable_p = 142

#Typically the best way to do correlation scoring is to do a sum over each index, but sometimes for large convolutional layers this
#can cause exploding gradients.  To correct this, the mean can be used instead.
correlations_by_mean = False

grad_sum_first = True

#this is for whether or not to batch norm the PAI outputs
default_pai_batch = False
default_random_pai_to_candidates = False
default_pai_dropout = 0.0

# Graph and visualization settings
# A graph setting which can be set to false if you want to do your own
# training visualizations
drawing_pai = True
# Saving test intermediary models, good for experimentation, bad for memory
test_saves = True
# To be filled in later. pai_saves will remove some extra scaffolding for
# slight memory and speed improvements
pai_saves = False

# Input dimensions needs to be set every time. It is set to what format of
# planes you are expecting.
# Neuron index should be set to 0, variable indexes should be set to -1.
# For example, if your format is [batchsize, nodes, x, y]
# input_dimensions is [-1, 0, -1, -1].
# if your format is, [batchsize, time index, nodes] input_dimensions is
# [-1, -1, 0]
input_dimensions = [-1, 0, -1, -1]

# Improvement thresholds
# Percentage improvement increase needed to call a new best validation score
improvement_threshold = 0.0005
# Raw increase needed
improvement_threshold_raw = 1e-5# raw increase needed, if its lower than this its not really learning anyway

#this is if even a single node has gone up by at least 10% over the total number of epochs to switch.
pai_improvement_threshold = 0.1 #improvement increase needed to call a new best PAIScore
pai_improvement_threshold_raw = 1e-5# raw increase needed, if its lower than this its not really learning 

# Weight initialization settings
# Multiplier when randomizing dendrite weights
candidate_weight_initialization_multiplier = 0.01

doing_mean_best = 0
#if(doing_mean_best):
    #pai_improvement_threshold *= 0.1
formula_type = 0

# SWITCH MODE SETTINGS

# Add dendrites every time to debug implementation
DOING_SWITCH_EVERY_TIME = 0

# Switch when validation hasn't improved over x epochs
DOING_HISTORY = 1
# Epochs to try before deciding to load previous best and add dendrites
# Be sure this is higher than scheduler patience
n_epochs_to_switch = 10  
p_epochs_to_switch = 10  
#p_patience = 1
cap_at_n = False #Makes sure PAI rounds last max as long as first N round

# Number to average validation scores over
history_lookback = 1
# Amount of epochs to run after adding a new set of dendrites before checking
# to add more
initial_history_after_switches = 0

# Switch after a fixed number of epochs
DOING_FIXED_SWITCH = 2
# Number of epochs to complete before switching
fixed_switch_num = 250
# An additional flag if you want your first switch to occur later than all the
# rest for initial pretraining
first_fixed_switch_num = 249

#if you set doing PAI to be false but still have a switch mode it will do learning rate restart
#this mode sets it to actually never switch
DOING_NO_SWITCH = 3

# Default switch mode
switch_mode = DOING_HISTORY

# Reset settings
# Resets score on switch
# This can be useful if you need many epochs to catch up to the best score
# from the previous version after adding dendrites
reset_best_score_on_switch = False

#if DOING_HISTORY make sure this value is always shorter, scheduler will update learning rate after this many epochs so need to give average history time to catch up
scheduler_patience = 3
scheduler_eps = 1e-15 #if lr gets below this value scheduler wont step
if(scheduler_patience > n_epochs_to_switch or scheduler_patience > p_epochs_to_switch):
    print('patience is set too high')
    sys.exit(0)

doing_thing = 0

#if one is true both should be true.
#seems to be better for conv but may or may not be better for linear
learn_dendrites_live = False
no_extra_n_modes = False

# Data type for new modules and dendrite to dendrite / dendrite to neuron
# weights
d_type = torch.float

# Dendrite retention settings
# A setting to keep dendrites even if they do not improve scores
retain_all_dendrites = False
save_all_epochs = False

# Learning rate management
# A setting to automatically sweep over previously used learning rates when
# adding new dendrites
# Sometimes it's best to go back to initial LR, but often its best to start
# at a lower LR
find_best_lr = True
switch_on_lr_change = False

# Enforces the above even if the previous epoch didn't lower the learning rate
dont_give_up_unless_learning_rate_lowered = True

# Dendrite attempt settings
# Set to 1 if you want to quit as soon as one dendrite fails
# Higher values will try new random dendrite weights this many times before
# accepting that more dendrites don't improve
max_dendrite_tries = 5
max_dendrites = 100

# this number is to check how many batches to average out the initial correlation score over
# this should be at least 100 and up to 10% of a whole epoch
initial_correlation_batches = 100 

# Scheduler parameter settings
# Have learning rate params be by total epoch
PARAM_VALS_BY_TOTAL_EPOCH = 0
# Reset the params at every switch
PARAM_VALS_BY_UPDATE_EPOCH = 1
# Reset params for dendrite starts but not for normal restarts
PARAM_VALS_BY_NEURON_EPOCH_START = 2
# Default setting
param_vals_setting = PARAM_VALS_BY_UPDATE_EPOCH


doing_dropout_for_small = True
doing_dropout_for_small_input = False

relu_mode = 'relu'
sigmoid_mode = 'sigmoid'
tan_h_mode = 'tanH'
leaky_relu_mode = 'leakyRelu'
no_nonlinarity_mode = 'noNonliniarity'
softmax_top_layer_mode = 'softmaxTopLayer'


pb_forward_function = torch.sigmoid
# Prevent flow of error back to network after candidates and dendrites (Doing Perforation)
candidate_graph_mode = True #default True
dendrite_graph_mode = True #default True
# Do Correlation learning (Doing CC)
dendrite_learn_mode = True #default True
# Allow dendrite weights to continue to learn (unfreeze Dendrite weights)
dendrite_update_mode = False #default False


'''
This take in an array of layers.  for example:

    GPA..PAISequential([nn.Linear(2 * hidden_dim, seqWidth),
            nn.LayerNorm(seqWidth)])
    
    This should be used for:
        -all normalization layers
    This can be used for:
        -final output layer and softmax - showed final layer has a better score, but whole network did worse so might have to try it both ways
    This doesn't seem to be needed for:
        -max pooling layers for score but also might be effecting it somehow

'''


class PAISequential(nn.Sequential):
        def __init__(self, layer_array):
            super(PAISequential, self).__init__()
            self.model = nn.Sequential(*layer_array)
        def forward(self, *args, **kwargs):
            return self.model(*args, **kwargs)

'''
This should but models in a similar form to 

        self.out = nn.Sequential(
            MPA.layerBatch(nn.Linear(2 * hidden_dim, seqWidth),
            nn.LayerNorm(seqWidth)),
            nn.ReLU(inplace=True))
generally the idea is that everything in between the non-linearity functions should be within a single PAI block
'''

#this is just a subset of PAISequential, but keeping it just to remember order should be lin then bn
'''
class layerBatch(nn.Sequential):
        def __init__(self, linLayer, bnLayer):
            super(layerBatch, self).__init__()
            self.model = nn.Sequential(
                linLayer,bnLayer)
        def forward(self, x):
            return self.model(x)
'''
'''
class layerBatch(nn.Sequential):
        def __init__(self, linLayer, bnLayer):
            super(layerBatch, self).__init__()
            self.model = nn.Sequential(
                linLayer,bnLayer)
        def forward(self, x):
            return self.model(x)

'''


#why is this a thing?
'''
class moduleWrapper(nn.Module):
        def __init__(self, module):
            super(moduleWrapper, self).__init__()
            self.model = module
        def forward(self, x, extras=None):
            if(extras is None):
                return self.model(x)
            return self.model(x, extras)
'''

#modules = types
#names = str(types)
#IDs = str of module_name within network

### Global objects and variables

# Pointer to the PAI Tracker which handles adding dendrites
pai_tracker = []

# Lists for module types and names to add dendrites to
# For these lists no specifier means type, name is module name
# and ids is the individual modules id, eg. model.conv2
modules_to_convert = [nn.Conv1d, nn.Conv2d, nn.Conv3d, nn.Linear]
module_names_to_convert = ["PAISequential"]
module_ids_to_convert = []

# All modules should either be converted or tracked to ensure all modules
# are accounted for
modules_to_track = []
module_names_to_track = []
# IDs are for if you want to pass only a single module by its assigned ID rather than the module type by name
module_ids_to_track = []


# Replacement modules happen before the conversion,
# so replaced modules will then also be run through the conversion steps
# These are for modules that need to be replaced before addition of dendrites
# See the resnet example in models_perforatedai
modules_to_replace = []
replacement_modules = []
modules_to_skip = []

# Dendrites default to modules which are one tensor input and one tensor
# output in forward()
# Other modules require to be labeled as modules with processing and assigned
# processing classes
# This can be done by module type or module name see customization.md in API
# for example
modules_with_processing = []
modules_processing_classes = []
module_names_with_processing = []
module_by_name_processing_classes = []
module_ids_to_skip = []


# Similarly here as above. Some huggingface models have multiple pointers to
# the same modules which cause problems
# If you want to only save one of the multiple pointers you can set which ones
# not to save here
module_names_to_not_save = ['.base_model']
