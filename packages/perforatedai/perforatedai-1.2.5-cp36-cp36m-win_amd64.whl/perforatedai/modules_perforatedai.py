import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F
import math
import sys
import numpy as np
import pdb
import os 

import time
from itertools import chain

from datetime import datetime
from perforatedai import globals_perforatedai as GPA
from perforatedai import models_perforatedai as MPA
from perforatedai import module_layer_tracker_perforatedai as TPA
from perforatedai import utils_perforatedai as UPA
import copy


pretrained_dendrite_load_values = ['out_channels', 'dendrite_modules_added', 'dendrites_to_top', 'main_module', 'name']
pretrained_pai_dendrite_load_values = ['out_channels']

dendrite_tensor_values = ['top_dendrite_candidate_averages', 
                        'prev_dendrite_candidate_correlation', 
                        'current_correlations_for_parallel', 
                        'best_score',
                        'previous_best_score',
                        'prev_dendrite_candidate_average',
                        'main_grad_average_for_scaling',
                        'candidate_grad_average_for_scaling',
                        'indexes_of_best',
                        'nodes_best_improved_this_epoch',
                        'parents_average_d_vector',
                        #'parents_average_d_mags',
                        'normal_pass_average_d',
                        #'normal_pass_average_d_mags',
                        #'normal_pass_average_d_sq'
                        ]
dendrite_single_values = ['breaking',
                        'locked',
                        'best_score_improved_this_time_step',
                        'best_score_improved_this_epoch',
                        #'parents_average_d_sq'
                        ]

#These are included above, they just get skipped for reinit if not live
non_live_skip_values = [   'normal_pass_average_d',
                        #'normal_pass_average_d_mags',
                        #'normal_pass_average_d_sq'
                        ]    



if(GPA.doing_thing):
    dendrite_single_values = dendrite_single_values + ['normal_pass_max_mean_act', 'parent_max_mean_act']
    non_live_skip_values = non_live_skip_values + ['normal_pass_max_mean_act']

dendrite_init_values = ['initialized',
                       'parallel_buffers_initialized',
                      'current_d_init']
#This is intentionally before adding the data parallel values which dont get zeroed at rinit
dendrite_re_init_values = dendrite_tensor_values + dendrite_single_values
#if(GPA.using_pia_data_parallel):
    #dendrite_tensor_values.append('current_d_sum')
    ##dendrite_tensor_values.append('current_d_mag_sum')
    #dendrite_single_values.append('current_d_sq_sum')

dendrite_save_values = dendrite_tensor_values + dendrite_single_values + dendrite_init_values

value_tracker_arrays = ['current_parent_d', 'dendrite_outs']

    
def fake_copy(net):
    return UPA.deep_copy_pai(net)

def filter_backward(grad_out, values, candidate_nonlinear_outs):
    debugging_dpp = True
    if(debugging_dpp and torch.cuda.device_count() > 1):
        import torch.distributed as dist
        rank = dist.get_rank()
    else:
        rank = 0
    if(GPA.extra_verbose):
        print('%d: %s calling backward' % (rank, values[0].layer_name))

    #This assumes that no matter what is happening you will always get batch_size, neurons, other_dims... as setup
    
    with torch.no_grad():
        val = grad_out.detach()
        if(GPA.extra_verbose):
            print('%d: %s 1' % (rank, values[0].layer_name))
        if(GPA.extra_verbose):
            print(id(values[0]))
            temp = values[0].current_d_init
            print('past')
            print(values[0].current_d_init)
            print(values[0].current_d_init[0])
        if(not values[0].current_d_init.item()):
            #make sure all dimensions are accounted for
            if(GPA.extra_verbose):
                print('%d: %s 1.5' % (rank, values[0].layer_name))
            if(len(values[0].this_input_dimensions) != len(grad_out.shape)):
                print('The following layer has not properly set this_input_dimensions')
                print(values[0].layer_name)
                print('it is expecting:')
                print(values[0].this_input_dimensions)
                print('but received')
                print(grad_out.shape)
                print('to check these all at once set GPA.debugging_input_dimensions = 1')
                print('Call set_this_input_dimensions on this layer after initialize_pai')
                
                if(not GPA.debugging_input_dimensions):
                    sys.exit(0)
                else:
                    GPA.debugging_input_dimensions = 2
                    return

                #return
            #make sure the ones that should be fixed are correct
            if(GPA.extra_verbose):
                print('%d: %s 2' % (rank, values[0].layer_name))
            for i in range(len(values[0].this_input_dimensions)):
                if(values[0].this_input_dimensions[i] == 0):
                    break
                if(not (grad_out.shape[i] == values[0].this_input_dimensions[i])
                    and not values[0].this_input_dimensions[i] == -1):
                    print('The following layer has not properly set this_input_dimensions with this incorrect shape')
                    print(values[0].layer_name)
                    print('it is expecting:')
                    print(values[0].this_input_dimensions)
                    print('but received')
                    print(grad_out.shape)
                    print('to check these all at once set GPA.debugging_input_dimensions = 1')
                    if(not GPA.debugging_input_dimensions):
                        sys.exit(0)
                    else:
                        GPA.debugging_input_dimensions = 2
                        return
                    #return
            if(GPA.extra_verbose):
                print('%d: %s 3' % (rank, values[0].layer_name))

            with(torch.no_grad)():
                if(GPA.verbose):
                    print('setting d shape for')
                    print(values[0].layer_name)
                    print(val.size())
                
                values[0].set_out_channels(val.size())
                values[0].setup_arrays(values[0].out_channels)
            #why would we not want to set this for data parallel?
            #if(GPA.using_pai_data_parallel == False):
            values[0].current_d_init[0] = 1
        #self.current_d = val
        if(GPA.extra_verbose):
            print('%d: %s 4' % (rank, values[0].layer_name))

        math_tuple = []
        view_tuple = []
        full_mult = 1
        for i in range(len(val.size())):
            if i == values[0].this_node_index:
                view_tuple.append(-1)
                continue
            full_mult *= val.shape[i]
            math_tuple.append(i)
            view_tuple.append(1)
        if(GPA.extra_verbose):
            print('%d: %s 5' % (rank, values[0].layer_name))
        if(GPA.pai_tracker.member_vars['mode'] =='p'):
            for i in range(0,GPA.global_candidates):
                #this is where the grad_in is actually set for the tagger
                average_d_matrix = values[i].parents_average_d_vector.view(view_tuple)
                if(val.device.type=='cpu'):
                    device_index = 0
                else:
                    device_index = val.device.index
                if(GPA.debugging_memory_leak and len(values[i].current_parent_d[device_index]) != 0):
                    print('%s called backward but then didn\'t get PAIified.  This can cause a memory leak. Check processors.' % values[i].layer_name)
                if(len(candidate_nonlinear_outs) == 0):
                    print('Trying to call backwards but module %s wasn\'t PAIified' % values[i].layer_name)
                    sys.exit(0)
                if(GPA.dendrite_learn_mode):
                    values[i].current_parent_d[device_index].append((val - (average_d_matrix)).detach())
                    candidate_nonlinear_outs[i].register_hook(lambda grad: values[i].current_parent_d[device_index][-1].to(val.device))
                #pretty sure this next line is the right way to do this, not above.  doesn't seem to really have any significant impact though.  should run normal unit tests and xor_main with it to be sure.
                #Values[i].current_parent_d = (val).detach()
                #candidate_nonlinear_outs[i].register_hook(lambda grad: (Values[i].current_parent_d  - (Values[i].parents_average_d_matrix)))
        if(GPA.extra_verbose):
            print('%d: %s 6' % (rank, values[0].layer_name))
        if(True):
            values[0].normal_pass_average_d *= 0.99
            '''
            print('val and tuple')
            print(val.shape)
            print(math_tuple)
            print(values[0].layer_name)
            '''
            try:
                values[0].normal_pass_average_d += (val.sum(math_tuple) * 0.01) / full_mult
                if(GPA.dpp_verbose):
                    print('no error with')
                    print(val.shape)
                    print(values[0].this_node_index)
                    print(math_tuple)
                    print(full_mult)
            except Exception as e:
                print(e)
                print('Error with type shape in %s' % values[0].layer_name)
                print(val.shape)
                print(values[0].this_node_index)
                print(math_tuple)
                print(full_mult)
                import pdb; pdb.set_trace()
                exit(0)
            #values[0].normal_pass_average_d_mags *= 0.99
            #values[0].normal_pass_average_d_mags += (val.abs().sum(math_tuple) * 0.01) / full_mult
            #values[0].normal_pass_average_d_std = values[0].normal_pass_average_d_std * 0.99 + val.std((math_tuple))*0.01

            #this is **2 after everything because it is a scalar to scale the final grad_in.  The final gradient that actually gets applied is gradient.sum(math_tuple)
            #final weight adjustment/actual grad value is net.module.main_module[0].PAINeuronModule.current_d.sum(math_tuple)
            #You can tell this by looking at the bias values in grad.  It will be similar for the convolution kernel weight values in grad
            '''
            values[0].normal_pass_average_d_sq *= 0.99
            if(GPA.grad_sum_first):
                values[0].normal_pass_average_d_sq += ((val)**2).sum(math_tuple) * 0.01# / full_mult #if changing here change previous in data parallel
            else:
                values[0].normal_pass_average_d_sq += ((val)).sum(math_tuple)**2 * 0.01# / full_mult
            '''
                    
                #values[0].current_d_out = grad_output
            if(GPA.learn_dendrites_live):
                full_mult = 1
                view_tuple = []
                for dim in range(len(val.shape)):
                    if dim == values[0].this_node_index:
                        view_tuple.append(-1)
                        continue
                    full_mult *= val.shape[dim]
                    view_tuple.append(1)
                    
                #Keep these values updated on the fly  if this works, might only need to do mean, above and will stay the same and be faster.
                #values[0].parents_average_d_mags.copy_(values[0].normal_pass_average_d_mags.double().detach().clone()/(full_mult))
                values[0].parents_average_d_vector.copy_(values[0].normal_pass_average_d.detach().clone()/(full_mult))
                #values[0].parents_average_d_sq.copy_(values[0].normal_pass_average_d_sq.double().mean().detach().clone())#/full_mult)

                values[0].parents_average_d_vector.requires_grad = False
                #Values[0].parents_average_d_sq.requires_grad = False
                #Values[0].parents_average_d_mags.requires_grad = False
    if(GPA.extra_verbose):
        print('%s completing backward' % values[0].layer_name)

def set_grad_params(model, to_set):
    for p in model.parameters():
        p.requires_grad = to_set

def set_wrapped_params(model):
    for p in model.parameters():
        p.wrapped = True

def set_tracked_params(model):
    for p in model.parameters():
        p.tracked = True

class PAINeuronModule(nn.Module):
    #Why did I make an option to load with a pretrained_dendrite?  I dont know what the use case would be.  pretrained regular just happens automatically now.
    def __init__(self, start_module, name, pretrained_dendrite=None):
        super(PAINeuronModule, self).__init__()

        if(pretrained_dendrite is None):
            self.main_module = start_module
            self.name = name
        else:
            self.main_module = pretrained_dendrite.main_module
            self.name = pretrained_dendrite.name
            
        set_wrapped_params(self.main_module)
        if(GPA.verbose):
            print('initiating a layer %s with main type %s' % (self.name, type(self.main_module)))
            print(start_module)
        if(type(self.main_module) in GPA.modules_with_processing):
            module_index = GPA.modules_with_processing.index(type(self.main_module))
            self.processor = GPA.modules_processing_classes[module_index]()
            if(GPA.verbose):
                print('with processor')
                print(self.processor)
        elif(type(self.main_module).__name__ in GPA.module_names_with_processing):
            module_index = GPA.module_names_with_processing.index(type(self.main_module).__name__)
            self.processor = GPA.module_by_name_processing_classes[module_index]()
            if(GPA.verbose):
                print('with processor')
                print(self.processor)
        else:
            self.processor = None
            
        self.random_pai_to_candidates = GPA.default_random_pai_to_candidates
        self.activation_function_value = -1
        self.type = 'neuron_layer'
        
        self.register_buffer('this_input_dimensions', (torch.tensor(GPA.input_dimensions)))
        if((self.this_input_dimensions == 0).sum() != 1):
            print('5 Need exactly one 0 in the input dimensions: %s' % self.name)
            print(self.this_input_dimensions)
            sys.exit(-1)
        self.register_buffer('this_node_index', torch.tensor(GPA.input_dimensions.index(0)))
        self.dendrite_modules_added = 0
        #have to do it like this because .cat to make it bigger returns a variable instead of a parameter so it cant just keep being made bigger
        self.dendrites_to_top = nn.ParameterList()
        self.register_parameter('newest_dendrites_to_top', None)
        self.candidate_to_top = nn.ParameterList()
        self.register_parameter('current_candidate_to_top', None)
        if(pretrained_dendrite is None):
            self.dendrite_module = PAIDendriteModule(self.main_module,
                                        pai_dropout_rate = GPA.default_pai_dropout, 
                                        random_pai_to_candidates = self.random_pai_to_candidates,
                                        activation_function_value = self.activation_function_value,
                                        name = self.name,
                                        input_dimensions = self.this_input_dimensions)
        else:
            self.dendrite_module = pretrained_dendrite.dendrite_module
        if ((issubclass(type(start_module),nn.Linear) or #if this is a linear
            (issubclass(type(start_module),GPA.PAISequential) and issubclass(type(start_module.model[0]),nn.Linear))) #or its layer batch with a linear
            and (np.array(self.this_input_dimensions)[2:] == -1).all()): #and everything past 2 is a negative 1
            self.set_this_input_dimensions(self.this_input_dimensions[0:2])        
        if(not pretrained_dendrite is None):
            self.load_from_pretrained_dendrite(pretrained_dendrite)
        GPA.pai_tracker.add_pai_neuron_module(self)        
        
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.main_module, name)
            

    # If processors save values they must be cleared in order to call DeepCopy
    def clear_processors(self):
        if not self.processor:
            return
        else:
            self.processor.clear_processor()
            self.dendrite_module.clear_processors()

    # before loading from a state dict Dendrites should be cleared and reset.
    # this may not be the most effecient way to do things, but clearing and then
    # simulating cycles is the easeiest way to ensure the state dict and the
    # current network have the same number of dendrites
    def clear_dendrites(self):
        self.dendrite_modules_added = 0
        self.dendrites_to_top = nn.ParameterList()
        self.candidate_to_top = nn.ParameterList()
        self.dendrite_module = PAIDendriteModule(self.main_module,
            pai_dropout_rate = GPA.default_pai_dropout, 
            random_pai_to_candidates = self.random_pai_to_candidates,
            activation_function_value = self.activation_function_value,
            name = self.name,
            input_dimensions = self.this_input_dimensions)

    #This was to hide that modules are wrapped, but now thats getting patented and part of instructions
    
    def __str__(self):
        if(GPA.verbose):
            total_string = self.main_module.__str__()
            total_string = 'PAILayer(' + total_string + ')'
            return total_string + self.dendrite_module.__str__()
        else:
            total_string = self.main_module.__str__()
            total_string = 'PAILayer(' + total_string + ')'
            return total_string
    def __repr__(self):
        return self.__str__()
    
    def load_from_pretrained_dendrite(self, pretrained_dendrite):
        for value_name in pretrained_dendrite_load_values:
            setattr(self,value_name, getattr(pretrained_dendrite,value_name))
        #self.dendrite_module.dendrite_load_from_pretrained_dendrite(pretrained_dendrite.dendrite_module)

    def set_this_input_dimensions(self, new_input_dimensions):
        if type(new_input_dimensions) is list:
            new_input_dimensions = torch.tensor(new_input_dimensions)

        #if hasattr(self,'this_input_dimensions'):
        delattr(self, 'this_input_dimensions')
        self.register_buffer('this_input_dimensions', new_input_dimensions.detach().clone())
        if (new_input_dimensions == 0).sum() != 1:
            print('6 need exactly one 0 in the input dimensions: %s' % self.name)
            print(new_input_dimensions)
        self.this_node_index.copy_((new_input_dimensions == 0).nonzero(as_tuple=True)[0][0])
        self.dendrite_module.set_this_input_dimensions(new_input_dimensions)

    def set_mode(self, mode):
        if(GPA.verbose):
            print('%s calling set mode %c' % (self.name, mode))
        if(mode == 'n'):
            self.dendrite_module.set_mode(mode)
            if(self.dendrite_modules_added > 0):
                if(GPA.learn_dendrites_live):
                    values = torch.cat((self.dendrites_to_top[self.dendrite_modules_added-1],nn.Parameter(self.candidate_to_top.detach().clone())),0)
                else:
                    values = torch.cat((self.dendrites_to_top[self.dendrite_modules_added-1],nn.Parameter(torch.zeros((1,self.out_channels), device=self.dendrites_to_top[self.dendrite_modules_added-1].device, dtype=GPA.d_type))),0)
                self.dendrites_to_top.append(nn.Parameter(values.detach().clone().to(GPA.device), requires_grad=True))
                #self.register_parameter('newest_dendrites_to_top'+str(self.dendrite_modules_added), self.dendrites_to_top[self.dendrite_modules_added])
            else:
                if(GPA.learn_dendrites_live):
                    self.dendrites_to_top.append(nn.Parameter(self.candidate_to_top.detach().clone(), requires_grad=True))
                else:
                    self.dendrites_to_top.append(nn.Parameter(torch.zeros((1,self.out_channels), device=GPA.device, dtype=GPA.d_type).detach().clone(), requires_grad=True))
                #self.register_parameter('newest_dendrites_to_top'+str(self.dendrite_modules_added), self.dendrites_to_top[self.dendrite_modules_added])
            self.dendrite_modules_added += 1
            set_grad_params(self.main_module, True)
            #pb to top [x] is a nodes_x_dendrite_module array, old one of one smaller is deleted and never used again
            if(self.dendrite_modules_added > 0):
                self.dendrites_to_top[self.dendrite_modules_added-1].requires_grad = True
                for param in self.dendrite_module.dendrite_to_dendrite:
                    param.requires_grad = False
        else:
            #this gets set in n mode and isnt needed till first p mode so set here
            '''
            DEBUG: If you are getting here but out_channels has not been set
            A common reason is that this layer never had gradients flow through it.
            I have seen this happen because:
                The weights were frozen (requires_grad = False)
                something was added but not used. e.g. self.layer was then added to self.layerPAI 
                    but forward is only called on layerPAI.  in these cases remove self from the original
                
            '''
            try:
                self.out_channels = self.dendrite_module.dendrite_values[0].out_channels
                self.dendrite_module.out_channels = self.dendrite_module.dendrite_values[0].out_channels
            except Exception as e:
                #if this is happening just stop this layer from being converted and remove it from places that it should be
                print(e)
                print('this occurred in layer: %s' % self.dendrite_module.dendrite_values[0].layer_name)
                print('If you are getting here but out_channels has not been set')
                print('A common reason is that this layer never had gradients flow through it.')
                print('I have seen this happen because:')
                print('-The weights were frozen (requires_grad = False)')
                print('-A model is added but not used so it was converted but never PAI initialized')
                print('-A module was converted that doesn\'t have weights that get modified so backward doesn\'t flow through it')
                print('If this is normal behavior set GPA.checked_skipped_modules = True in the main to ignore')
                print('You can also set right now in this pdb terminal to have this not happen more after checking all layers this cycle.')
                if(not GPA.checked_skipped_modules):
                    import pdb; pdb.set_trace()
                return False
            #only change mode if it actually is learning and calculating grads
            self.dendrite_module.set_mode(mode)
            if(GPA.learn_dendrites_live):
                self.candidate_to_top = nn.Parameter(torch.zeros((1,self.out_channels), device=GPA.device, dtype=GPA.d_type).detach().clone(), requires_grad=True)
                self.register_parameter('current_candidate_to_top', self.candidate_to_top)    
                
                #THIS SHOULDN'T BE NEEDED BUT MESSED IT UP IN THIS RUN
                set_grad_params(self.main_module, True)
                #pb to top [x] is a nodes_x_dendrite_module array, old one of one smaller is deleted and never used again
                if(self.dendrite_modules_added > 0):
                    self.dendrites_to_top[self.dendrite_modules_added-1].requires_grad = True
                    for param in self.dendrite_module.dendrite_to_dendrite:
                        param.requires_grad = True



            #set normal layers to no longer learn
            else:
                set_grad_params(self.main_module, False)
                if(self.dendrite_modules_added > 0):
                    self.dendrites_to_top[self.dendrite_modules_added-1].requires_grad = False
                    for param in self.dendrite_module.dendrite_to_dendrite:
                        param.requires_grad = False
        return True

    def create_new_dendrite_module(self):
        self.dendrite_module.create_new_dendrite_module()

    def add_loaded_dendrite_module(self):
        self.dendrite_module.add_loaded_dendrite_module()
    
    def load_tagger_values(self):
        self.dendrite_module.load_tagger_values()

    def add_dendrite_nodes(self, numberNodes):
        self.dendrite_module.in_channels = self.in_channels
        self.dendrite_module.out_channels = self.out_channels
        self.dendrite_module.stride = self.stride
        self.dendrite_module.padding = self.padding
        self.dendrite_module.kernel_size = self.kernel_size
        self.dendrite_module.add_dendrite_nodes(numberNodes)
            
    def forward(self, *args, **kwargs):
        if(GPA.extra_verbose):
            print('%s calling forward' % self.name)
        
        if(GPA.debugging_input_dimensions == 2):
            print('all input dim problems now printed')
            sys.exit(0)
        out = self.main_module(*args, **kwargs)
        if not self.processor is None:
            out = self.processor.post_n1(out)
        
        dendrite_outs, candidate_outs, candidate_nonlinear_outs, candidate_outs_non_zeroed = self.dendrite_module(*args, **kwargs)

        if(self.dendrite_modules_added > 0):
            for i in range(0,self.dendrite_modules_added):
                to_top = self.dendrites_to_top[self.dendrite_modules_added-1][i,:]
                for dim in range(len(dendrite_outs[i].shape)):
                    if(dim == self.this_node_index):
                        continue
                    to_top = to_top.unsqueeze(dim)
                if(GPA.confirm_correct_sizes):
                    to_top = to_top.expand(list(dendrite_outs[i].size())[0:self.this_node_index] + [self.out_channels] + list(dendrite_outs[i].size())[self.this_node_index+1:])
                #PARALELL HACK TODO what does this mean?
                out = ( out + (dendrite_outs[i].to(out.device) * to_top.to(out.device)))
        #if pb is not in p mode it means this one isnt doing a grad
        if(GPA.pai_tracker.member_vars['mode'] == 'p' and self.dendrite_module.mode == 'p'):
            ## NEED LOOP HERE
            for i in range(0,GPA.global_candidates):
                if(GPA.learn_dendrites_live):
                    to_top = self.candidate_to_top[i,:]
                    for dim in range(len(candidate_outs_non_zeroed[i].shape)):
                        if(dim == self.this_node_index):
                            continue
                        to_top = to_top.unsqueeze(dim)
                    if(GPA.confirm_correct_sizes):
                        to_top = to_top.expand(list(candidate_outs_non_zeroed[i].size())[0:self.this_node_index] + [self.out_channels] + list(candidate_outs_non_zeroed[i].size())[self.this_node_index:])                    
                    out = ( out + (candidate_outs_non_zeroed[i].to(out.device) * to_top.to(out.device)))
                        
                #also try this before the next out thing
                out = (out + candidate_outs[i].to(out.device))                 
        
        #POINT1    
        if(GPA.pai_tracker.member_vars['mode'] == 'n' and GPA.doing_thing):
            if(out.abs().max() > self.dendrite_module.dendrite_values[0].normal_pass_max_mean_act):
                self.dendrite_module.dendrite_values[0].normal_pass_max_mean_act[0] = out.abs().max().item()
                if(GPA.learn_dendrites_live):
                    self.dendrite_module.dendrite_values[0].parent_max_mean_act.copy_(self.dendrite_module.dendrite_values[0].normal_pass_max_mean_act[0].detach().clone())
                    self.dendrite_module.dendrite_values[0].parent_max_mean_act.requires_grad = False
            if(self.dendrite_module.dendrite_values[0].normal_pass_max_mean_act[0] == 0):
                print('An entire layer got exactly 0 Correlation')
                
                import pdb; pdb.set_trace()
        
        #POINT2
        if(type(out) is tuple):
            print(self)
            print('The output of the above module %s is a tuple when it must be a single tensor')
            print('Look in the API at section 2.2 regarding processors to fix this.')
            import pdb; pdb.set_trace()
        
        if(out.requires_grad):
            if candidate_nonlinear_outs == {}:
                out.register_hook(lambda grad: filter_backward(grad, self.dendrite_module.dendrite_values, {}))
            else:
                candidate_nonlinear_outs[0] = candidate_nonlinear_outs[0].to(out.device)
                out.register_hook(lambda grad: filter_backward(grad, self.dendrite_module.dendrite_values, candidate_nonlinear_outs))
        
        if not self.processor is None:
            out = self.processor.post_n2(out)
        return out
        

'''
This class exists to wrap the modules you dont want to add Dendrites to.
These will still be correctly changed to learning and not leraning
with calls to set_mode
'''
class TrackedNeuronLayer(nn.Module):
    def __init__(self, start_module, name):
        super(TrackedNeuronLayer, self).__init__()

        self.main_module = start_module
        self.name = name
            
        self.type = 'tracked_layer'
        set_tracked_params(self.main_module)
        if(GPA.verbose):
            print('tracking a layer %s with main type %s' % (self.name, type(self.main_module)))
            print(start_module)
        GPA.pai_tracker.add_tracked_neuron_layer(self)        
        
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.main_module, name)
            
    def set_mode(self, mode):
        if(GPA.verbose):
            print('%s calling set mode %c' % (self.name, mode))
        if(mode == 'n'):
            set_grad_params(self.main_module, True)
        else:
            set_grad_params(self.main_module, False)
        return True
           
    def forward(self, *args, **kwargs):
        return self.main_module(*args, **kwargs)
    def __str__(self):
        if(GPA.verbose):
            total_string = self.main_module.__str__()
            total_string = 'PAITrackedLayer(' + total_string + ')'
            return total_string
        else:
            total_string = self.main_module.__str__()
            total_string = 'PAITrackedLayer(' + total_string + ')'
            return total_string
    def __repr__(self):
        return self.__str__()

def init_params(model):
    for p in model.parameters():
        p.data=torch.randn(p.size(), dtype=p.dtype)*GPA.candidate_weight_initialization_multiplier # Random weight initialization

class PAIDendriteModule(nn.Module):
    def __init__(self, initialModule, pai_dropout_rate=0.0,  
                 #resNetLayer=False,
                 random_pai_to_candidates=False, activation_function_value=0.3, name='no_name_given',
                 input_dimensions = []):
        super(PAIDendriteModule, self).__init__()
        
        if(pai_dropout_rate > 0.0000001):
            print('initing with dropout')
            self.doing_dropout = True
            self.pai_dropout_rate = pai_dropout_rate
            self.pbDropoutLayers = nn.ModuleList([])
        else:
            self.doing_dropout = False
        self.layers = nn.ModuleList([])
        self.processors = []
        self.candidate_processors = []
        self.num_dendrites = 0
        self.register_buffer('num_cycles', torch.zeros(1, device=GPA.device, dtype=GPA.d_type))
        #default to n mode
        self.mode = 'n'
        
        self.name=name
        #this deep copy shouldn't specifically be required but huggingface save complains without it
        self.parent_module = UPA.deep_copy_pai(initialModule)

        ### CLOSED ONLY     
        #base layer options
        self.current_recurrent_pass_tensors = []
        self.current_recurrent_pass_candidate_tensors = []
        if(input_dimensions == []):
            self.register_buffer('this_input_dimensions', torch.tensor(GPA.input_dimensions))
        else:
            self.register_buffer('this_input_dimensions', input_dimensions.detach().clone())
        if((self.this_input_dimensions == 0).sum() != 1):
            print('1 need exactly one 0 in the input dimensions: %s' % self.name)
            print(self.this_input_dimensions)
            sys.exit(-1)
        self.register_buffer('this_node_index', torch.tensor(GPA.input_dimensions.index(0)))

        #self.resNetLayer = resNetLayer
        #PAI VALUES
        #self.dendrite_values = nn.ModuleList([])
        self.normal_learning_taggers = {}
        #self.dendrite_outs = {}
        self.internal_recurrent = False

        self.best_weights = {}
        self.best_biases = {}
        self.best_bn_weights = {}
        self.best_bn_biases = {}
        self.dendrites_to_candidates = nn.ParameterList()
        self.dendrite_to_dendrite = nn.ParameterList()
        self.added_taggers = False
        self.random_pai_to_candidates = random_pai_to_candidates
        self.activation_function_value = activation_function_value
        self.dendrite_values = nn.ModuleList([])
        for j in range(0, GPA.global_candidates):
            if(GPA.verbose):
                print('creating pb values for %s' % (self.name))
            self.dendrite_values.append(DendriteValueTracker(False, self.activation_function_value, self.name, self.this_input_dimensions))

        ### END CLOSED ONLY

    def set_this_input_dimensions(self, new_input_dimensions):
        if type(new_input_dimensions) is list:
            new_input_dimensions = torch.tensor(new_input_dimensions)
        delattr(self, 'this_input_dimensions')
        self.register_buffer('this_input_dimensions', new_input_dimensions.detach().clone())
        if (new_input_dimensions == 0).sum() != 1:
            print('2 Need exactly one 0 in the input dimensions: %s' % self.name)
            print(new_input_dimensions)
            sys.exit(-1)
        self.this_node_index.copy_((new_input_dimensions == 0).nonzero(as_tuple=True)[0][0])
        for j in range(0, GPA.global_candidates):
            self.dendrite_values[j].set_this_input_dimensions(new_input_dimensions)

    ### CLOSED ONLY
    def dendrite_load_from_pretrained_dendrite(self, pretrained_dendrite):
        for j in range(0, GPA.global_candidates):
            self.dendrite_values[j].setup_arrays(pretrained_dendrite.dendrite_values[j].out_channels)
            for value_name in (dendrite_save_values + pretrained_pai_dendrite_load_values):
                setattr(self.dendrite_values[j],value_name, getattr(pretrained_dendrite.dendrite_values[j],value_name))
            self.dendrite_values[j].activation_function_value = pretrained_dendrite.activation_function_value
    ### END CLOSED ONLY

    def create_new_dendrite_module(self):
        self.candidate_layer = nn.ModuleList([])
        self.best_candidate_layer = nn.ModuleList([])
        if(GPA.verbose):
            print(self.name)
            print('setting candidate processors')
        self.candidate_processors = []
        with torch.no_grad():
            for i in range(0, GPA.global_candidates):
                
                new_module = fake_copy(self.parent_module)
                init_params(new_module)
                set_grad_params(new_module, True)
                self.candidate_layer.append(new_module)
                self.best_candidate_layer.append(fake_copy(new_module))
                if(type(self.parent_module) in GPA.modules_with_processing):
                    module_index = GPA.modules_with_processing.index(type(self.parent_module))
                    self.candidate_processors.append(GPA.modules_processing_classes[module_index]())
                elif(type(self.parent_module).__name__ in GPA.module_names_with_processing):
                    module_index = GPA.module_names_with_processing.index(type(self.parent_module).__name__)
                    self.candidate_processors.append(GPA.module_by_name_processing_classes[module_index]())

        for i in range(0, GPA.global_candidates):
            self.candidate_layer[i].to(GPA.device)
            self.best_candidate_layer[i].to(GPA.device)
            
        #normalize average_d_sq?
        #normal_pass_average_d_sq = normal_pass_average_d_sq/((normal_pass_average_d_sq*normal_pass_average_d_sq).sum()).sqrt()
        # for i in range(0, self.out_channels):
        for j in range(0, GPA.global_candidates):
            self.dendrite_values[j].reinitialize_for_pai(0)
        
        self.added_taggers = True ### CLOSED ONLY
            
        if(self.num_dendrites > 0):
            self.dendrites_to_candidates = nn.ParameterList()
            for j in range(0,GPA.global_candidates): #Loopy Loops
                self.dendrites_to_candidates.append(nn.Parameter(torch.zeros((self.num_dendrites, self.out_channels), device=GPA.device, dtype=GPA.d_type), requires_grad=True))
                self.dendrites_to_candidates[j].data.pai_wrapped = True
                if(self.random_pai_to_candidates):
                    with torch.no_grad():
                        self.dendrites_to_candidates[j].normal_(0, math.sqrt(2. / self.out_channels))
                #self.register_parameter(('dendrites_to_candidates'+str(j)), self.dendrites_to_candidates[j])

    def clear_processors(self):
        for processor in self.processors:
            if not processor:
                continue
            else:
                processor.clear_processor()
        for processor in self.candidate_processors:
            if not processor:
                continue
            else:
                processor.clear_processor()

        
    def set_mode(self, mode):
        self.mode = mode
        self.num_cycles += 1
        if(GPA.verbose):
            print('pb calling set mode %c : %d' % (mode, self.num_cycles))
        if(mode == 'n'):
            if(GPA.verbose):
                print('so calling all the things to add to layers')
            for i in range(0,GPA.global_candidates):
                self.dendrite_values[i].locked[0] = 1
                
            if(self.doing_dropout):
                self.pbDropoutLayers.append(nn.Dropout(p=self.pai_dropout_rate).to(GPA.device))

            #copy weights/bias from correct candidates
            if(self.num_dendrites == 1):
                self.dendrite_to_dendrite = nn.ParameterList()
                self.dendrite_to_dendrite.append(torch.tensor([]))
            if(self.num_dendrites >= 1):
                self.dendrite_to_dendrite.append(torch.nn.Parameter(torch.zeros([self.num_dendrites,self.out_channels], device=GPA.device, dtype=GPA.d_type), requires_grad=GPA.dendrite_update_mode))#NEW
            with torch.no_grad():
                if(GPA.global_candidates > 1):
                    print('This was a flag that will be needed if using multiple candidates.  It\'s not set up yet but nice work finding it.')
                    pdb.set_trace()
                plane_max_index = 0
                self.layers.append(fake_copy(self.best_candidate_layer[plane_max_index]))
                self.layers[self.num_dendrites].to(GPA.device)
                if(self.num_dendrites > 0):
                    if(GPA.verbose):
                        print('this maybe should have a clone and data')
                    self.dendrite_to_dendrite[self.num_dendrites].copy_(self.dendrites_to_candidates[plane_max_index])
                if(type(self.parent_module) in GPA.modules_with_processing):
                    self.processors.append(self.candidate_processors[plane_max_index])
                if(type(self.parent_module).__name__ in GPA.module_names_with_processing):
                    self.processors.append(self.candidate_processors[plane_max_index])

            #set PAI nodes to no longer learn
            
            set_grad_params(self.layers[self.num_dendrites], GPA.dendrite_update_mode)
            for param in self.dendrite_to_dendrite:
                param.requires_grad = GPA.dendrite_update_mode
            if(self.num_dendrites > 0):
                for j in range(0,GPA.global_candidates): #Loopy Loops
                    self.dendrites_to_candidates[j].requires_grad = False

            del self.candidate_layer, self.best_candidate_layer

            self.num_dendrites += 1

    ### CLOSED ONLY
    def killer_recursive(self, in_vals, killing):
        device = None
        if type(in_vals) is list:
            if(len(in_vals) == 0):
                return in_vals, None
            for index in range(len(in_vals)):
                in_vals[index], device2 = self.killer_recursive(in_vals[index], killing)
                if(not device2 is None):
                    device = device2
        elif type(in_vals) is tuple:
            if(len(in_vals) == 0):
                return in_vals, None
            for index in range(len(in_vals)):
                in_vals = list(in_vals)
                in_vals[index], device2 = self.killer_recursive(in_vals[index], killing)
                if(not device2 is None):
                    device = device2
                in_vals = tuple(in_vals)
        elif type(in_vals) is dict:
            if(len(in_vals.keys()) == 0):
                return in_vals, None
            for index in in_vals.keys():
                in_vals[index], device2 = self.killer_recursive(in_vals[index], killing)
                if(not device2 is None):
                    device = device2
        elif issubclass(torch.Tensor, type(in_vals)):
            with torch.cuda.device_of(in_vals):
                if(killing):
                    to_return = grad_killer(in_vals).detach().clone()
                else:
                    to_return = in_vals
                return to_return, in_vals.device
        else:
            return in_vals, None
        return in_vals, device

    def killer_recursive_old(self, in_vals):
        if type(in_vals) is list:
            for index in range(len(in_vals)):
                in_vals[index] = self.killer_recursive(in_vals[index])
        elif type(in_vals) is tuple:
            for index in range(len(in_vals)):
                in_vals = list(in_vals)
                in_vals[index] = self.killer_recursive(in_vals[index])
                in_vals = tuple(in_vals)
        elif type(in_vals) is dict:
            for index in in_vals.keys():
                in_vals[index] = self.killer_recursive(in_vals[index])
        elif issubclass(torch.Tensor, type(in_vals)):
            return grad_killer(in_vals).detach().clone()
        return in_vals
    
    ### END CLOSED ONLY
        
    def forward(self, *args, **kwargs):
        outs = {}
            
        for c in range(0,self.num_dendrites):
            args2, device = self.killer_recursive(args, GPA.dendrite_graph_mode)
            kwargs2, device2 = self.killer_recursive(kwargs, GPA.dendrite_graph_mode)
            #args2, = self.killer_recursive(args)
            #kwargs2 = self.killer_recursive(kwargs)
            if(self.processors != []):
                args2, kwargs2 = self.processors[c].pre_d(*args2, **kwargs2)
            out_values = self.layers[c](*args2, **kwargs2)
            if(self.processors != []):
                outs[c] = self.processors[c].post_d(out_values)
            else:
                outs[c] = out_values

        for out_index in range(0,self.num_dendrites):
            current_out = outs[out_index]
            view_tuple = []
            for dim in range(len(current_out.shape)):
                if dim == self.this_node_index:
                    view_tuple.append(-1)
                    continue
                view_tuple.append(1)

            for in_index in range(0,out_index):
                #PARALLEL HACK
                if(view_tuple == [1]): #This is only the case when passing a single datapoint rather than a batch
                    current_out += self.dendrite_to_dendrite[out_index][in_index,:].to(current_out.device) * outs[in_index]            
                else:
                    current_out += self.dendrite_to_dendrite[out_index][in_index,:].view(view_tuple).to(current_out.device) * outs[in_index]            

            current_out.copy_( GPA.pb_forward_function(current_out))
            if(self.doing_dropout):
                for out_index in range(0,self.num_dendrites):
                    current_out.copy_( self.pbDropoutLayers[out_index](current_out))

        ### CLOSED ONLY
        candidate_outs = {}
        candidate_nonlinear_outs = {}
        candidate_non_zeroed = {}
        for i in range(0,GPA.global_candidates):
            #self.mode will only not also be p if this is not learning
            if(GPA.pai_tracker.member_vars['mode'] == 'p' and self.mode == 'p'):
                args2, device = self.killer_recursive(args, GPA.candidate_graph_mode)
                kwargs2, device2  = self.killer_recursive(kwargs, GPA.candidate_graph_mode)
                if device is None:
                    device = device2

                '''
                DEBUG: if you\'re here this layer should have PAI nodes which means
                candidate processors should have been initialized.  If its not you are likely
                still pointing to the old model that doesn\'t have PAI nodes added.  make sure
                when you call add validation score you are properly setting the model
                '''
                if(self.candidate_processors != []):
                    args2, kwargs2 = self.candidate_processors[i].pre_d(*args2, **kwargs2)
                
                '''
                DEBUG:
                If you are getting a cpu vs gpu issue on this line its because the model is receiving args that are on the wrong thing, but within the forward function it gets passed to the correct spot.  don't ever call to() in the forward function, call it before it gets passed in
                '''
                candidate_out_values = self.candidate_layer[i].to(device)(*args2, **kwargs2)
                if(self.candidate_processors != []):
                    candidate_outs[i] = self.candidate_processors[i].post_d(candidate_out_values)
                else:
                    candidate_outs[i] = candidate_out_values

                for in_index in range(self.num_dendrites):
                    #PARALLEL HACK
                    if(view_tuple == [1]): #This is only the case when passing a single datapoint rather than a batch
                        candidate_outs[i] = candidate_outs[i].to(device) + self.dendrites_to_candidates[i][in_index,:].to(device) * outs[in_index]
                    else:
                        candidate_outs[i] = candidate_outs[i].to(device) + self.dendrites_to_candidates[i][in_index,:].view(view_tuple).to(device) * outs[in_index]

                if(GPA.dendrite_learn_mode):
                    candidate_outs[i] = pai_tagger(candidate_outs[i], self.dendrite_values[i].to(device))
                #import pdb; pdb.set_trace()
                candidate_nonlinear_outs[i] = GPA.pb_forward_function(candidate_outs[i]).to(device)
                    
                #candidate_nonlinear_outs chosen randomly, just generally saying dont do this during inference, only training.
                if(self.training):
                    #no it seems like this should be cleared on the main module so when its replicated it should work properly.
                    if(device.type=='cpu'):
                        device_index = 0
                    else:
                        device_index = device.index
                    if(GPA.debugging_memory_leak and len(self.dendrite_values[i].dendrite_outs[device_index]) != 0):
                        if(GPA.no_backward_workaround):
                            del self.dendrite_values[i].dendrite_outs[device_index][-1] 
                            # This may also be required for no_backward_workaround.  Found it earlier, but didn't have a noBackwards problem to debug with
                            #del self.dendrite_values[i].current_parent_d[device_index][-1]
                        else:
                            print("%s is in backwards graph multiple times.  This will cause a memory leak unless it is a recurrent layer.  Currently stacked (%d/%d) times" % (self.name, len(self.dendrite_values[0].dendrite_outs[0]), len(self.dendrite_values[0].current_parent_d[0])))
                            print('If this is coming up before a memory leak that happens anywhere other than the first batch of an epoch you NEED to debug this.')
                            print('Check the Memory Leak section of the debugging MD file.')
                            print('If this is just being printed but there is not a memory leak you can set GPA.debugging_memory_leak = False')
                            print('If you don\'t have any recurrent layers you can also clear this by in a more memory efficient way by setting GPA.no_backward_workaround = True')
                            print('If you set GPA.no_backward_workaround = True and it causes a IndexError: list index out of range error, that means you do have a recurrent layer')
                            #import pdb; pdb.set_trace()
                    if(GPA.dendrite_learn_mode):
                        self.dendrite_values[i].dendrite_outs[device_index].append(candidate_nonlinear_outs[i].detach().clone().to(device))
                        if(GPA.extra_verbose and candidate_nonlinear_outs[i].isnan().any()):
                            print('got candidate out nan')
                            import pdb; pdb.set_trace()
                candidate_non_zeroed[i] = candidate_nonlinear_outs[i].detach().clone().to(device)
                candidate_outs[i] = no_forward(candidate_nonlinear_outs[i])
        
        return outs, candidate_outs, candidate_nonlinear_outs, candidate_non_zeroed
    

from packaging import version

if version.parse(torch.__version__) >= version.parse("2.4.0"):
    from torch.amp import custom_fwd, custom_bwd
else:
    from torch.cuda.amp import custom_fwd, custom_bwd

def pai_tagger(inp, Values):
    class Tagger(torch.autograd.Function):
        #@staticmethod  Eventually for best practices this should be added back, but it casues problems with compiled version
        @custom_fwd(device_type='cuda', cast_inputs=torch.float32)
        def forward(ctx, inp):
            return inp
        
        #@staticmethod Eventually for best practices this should be added back, but it casues problems with compiled version
        @custom_bwd(device_type='cuda')
        def backward(ctx, grad_out):
            yolo_testing = False

            with torch.no_grad():
                saved_values = Values
                if(GPA.extra_verbose):
                    print('%s calling Dendrite backward' % saved_values.layer_name)
                    
                if(saved_values.layer_name == '.layers.29' and yolo_testing):
                    GPA.extra_verbose = True

                if(saved_values.locked):
                    return grad_out*0, None

                math_tuple = []
                view_tuple = []
                for i in range(len(grad_out.size())):
                    if i == Values.this_node_index:
                        view_tuple.append(-1)
                        continue
                    math_tuple.append(i)
                    view_tuple.append(1)

                eps = 0.00000001
                if(grad_out.device.type=='cpu'):
                    device_index = 0
                else:
                    device_index = grad_out.device.index
                if (len(saved_values.dendrite_outs[device_index]) == 0):
                    print('Dendrite does not have output Value for layer %s' % saved_values.layer_name)
                    print('This is caused by your model being in eval mode when you call loss.backwards()')
                    import pdb; pdb.set_trace()
                last_dendrite_outs = saved_values.dendrite_outs[device_index][-1].detach().clone().to(grad_out.device)
                last_parent_d = saved_values.current_parent_d[device_index][-1].detach().clone().to(grad_out.device)
                direction = saved_values.prev_dendrite_candidate_correlation.sign()
                temp_reshape_direction = direction.view(view_tuple)
                current_correlations = last_dendrite_outs * (last_parent_d)
                
                #shouldn't this be the average?  its * all of the current outputs and parent errors. why would it sum them before subtracting them from the average output * the average errors.
                #retain all PAI is currently broken. doesn't seem to actually work and also messages up saving     graphs.

                #looks lke this is worse, but not sure why.  Switch back to the original and move on.                
                # if every coming back to this remember to chance cor calculation to just be this later
                #current_correlations = (last_dendrite_outs.to(last_parent_d.device)-aveOut) * (last_parent_d)
                #current_correlations = current_correlations.mean(math_tuple)

                #can also try one where it switches to mean if the sum is > 1. or allow it to be set by layer manually
                if(GPA.correlations_by_mean):
                    current_correlations = current_correlations.mean((math_tuple))
                else:
                    current_correlations = current_correlations.sum((math_tuple))
                    
                #got rid of averagedsq because doing a proportional scaling later so this scaling doesnt matter.
                if(GPA.formula_type == 0):
                    grad_in = -(grad_out.detach() * (temp_reshape_direction))# / ((saved_values.parents_average_d_sq + eps))
                elif(GPA.formula_type == 1):
                    grad_in = -(grad_out.detach() * current_correlations.view(view_tuple) * (temp_reshape_direction))# / ((saved_values.parents_average_d_sq + eps))
                #this doesnt work, the second gradin is just the same since its average and not actual sum
                elif(GPA.formula_type == 2):
                    grad_in = -(grad_out.detach() * current_correlations.view(view_tuple) * (temp_reshape_direction))# / ((saved_values.parents_average_d_sq + eps))
                    grad_in /= (grad_out.pow(2) * current_correlations.view(view_tuple).pow(2)).sqrt()
                elif(GPA.formula_type == 3):
                    grad_in = -(grad_out.detach() * (last_dendrite_outs - saved_values.prev_dendrite_candidate_average.view(view_tuple)) * (temp_reshape_direction))
                # same as 2
                elif(GPA.formula_type == 4):
                    grad_in = -(grad_out.detach() * (last_dendrite_outs - saved_values.prev_dendrite_candidate_average.view(view_tuple)) * (temp_reshape_direction))
                    grad_in /= (grad_out.pow(2) * (last_dendrite_outs - saved_values.prev_dendrite_candidate_average.view(view_tuple)).pow(2)).sqrt()

                #print('top')
                #print(saved_values.top_dendrite_candidate_averages)
                #print('ave')
                #print(saved_values.prev_dendrite_candidate_average)

                #adjust correlations

                saved_values.top_dendrite_candidate_averages.copy_(last_dendrite_outs.mean((math_tuple)))
                        
                saved_values.prev_dendrite_candidate_average *= 0.99
                saved_values.prev_dendrite_candidate_average += saved_values.top_dendrite_candidate_averages * 0.01


                if(GPA.extra_verbose):
                    print('new top')
                    print(saved_values.top_dendrite_candidate_averages)
                    print('new ave')
                    print(saved_values.prev_dendrite_candidate_average)
                    print('parentsAverageD')
                    print(saved_values.parents_average_d_vector)
                    print('last_dendrite_outs')
                    print(last_dendrite_outs)
                    print('last_parent_d')
                    print(last_parent_d)
                    print('current_correlations')
                    print(current_correlations)
                #if(not GPA.using_pia_data_parallel):
                if(True):
                    #TODO: Should this use top_dendrite_candidate_averages until initialized has completed?
                    cor = current_correlations - (saved_values.prev_dendrite_candidate_average * saved_values.parents_average_d_vector) # / net['layers'][l]['sumSqError'][j]
                    if(GPA.extra_verbose):
                        print('prev')
                        print(saved_values.prev_dendrite_candidate_correlation)
                        print('cor')
                        print(cor)
                        print('current_correlations')
                        print(current_correlations)
                    saved_values.prev_dendrite_candidate_correlation *= 0.99
                    saved_values.prev_dendrite_candidate_correlation += cor * 0.01
                    if(GPA.extra_verbose):
                        print('next prev')
                        print(saved_values.prev_dendrite_candidate_correlation)
                        if((saved_values.parents_average_d_vector).isnan().any()
                           or (saved_values.prev_dendrite_candidate_average).isnan().any()
                           or (saved_values.top_dendrite_candidate_averages).isnan().any()
                           or (current_correlations).isnan().any()):
                            print('got a nan in correlation score')
                            import pdb; pdb.set_trace()
                        
                    temp_abs = saved_values.prev_dendrite_candidate_correlation.detach().abs()
                    
                    #best score is the max score of the previous best score and the current recently averaged correlation
                    
                    [best_score, temp_best_indices] =  torch.max(torch.cat((saved_values.best_score.unsqueeze(0),temp_abs.unsqueeze(0)), 0),0)
                    saved_values.best_score.copy_(best_score)
                    
                    #print(saved_values.best_score)
                    #if that best score has improved enough or this is the very first iteration
                    if(((
                        (saved_values.best_score*(1.0-GPA.pai_improvement_threshold))-saved_values.previous_best_score).max()>0.00000001
                        and (saved_values.best_score - saved_values.previous_best_score).max() > GPA.pai_improvement_threshold_raw)

                        or saved_values.initialized.item() == 0):
                        
                        if(saved_values.best_score_improved_this_epoch[0] == 0 and GPA.verbose):
                            print('Score from %.16f to %.16f for %s with initialized %d' % (saved_values.previous_best_score.mean(), 
                                                                                            saved_values.best_score.mean(), 
                                                                                            saved_values.layer_name,
                                                                                            saved_values.initialized.item()))
                        # say that best score did improve this epoch and time step
                        saved_values.best_score_improved_this_epoch[0].copy_(torch.tensor(1))
                        #print('setting best score improved this timestep with')
                        #print(saved_values.best_score)
                        #print(saved_values.previous_best_score)
                        #print(saved_values.initialized.item())
                        saved_values.best_score_improved_this_time_step[0].copy_(torch.tensor(1))
                        #set the indexes of the best candidate
                        saved_values.indexes_of_best.copy_(temp_best_indices)
                        
                        ##check where temp_abs = best_score and save the weights for those candidates in forward for the layer next iteration
                            #this is where that saveBest function was maybe called?
                        [values,indexes] = torch.max(saved_values.indexes_of_best,0)
                        saved_values.nodes_best_improved_this_epoch += saved_values.indexes_of_best
                        #only replace the ones that are bigger                            
                        saved_values.previous_best_score.copy_(torch.max(saved_values.best_score, saved_values.previous_best_score).detach())
                    else:
                        #print('setting best score improved this timestep with')
                        #print(saved_values.best_score)
                        #print(saved_values.previous_best_score)
                        #print(saved_values.initialized.item())
                        saved_values.best_score_improved_this_time_step[0].copy_(torch.tensor(0))
                        saved_values.indexes_of_best *= 0
                    if(saved_values.breaking.item()):
                        pdb.set_trace()
                #else: # if not new data parallel all of this is being done in gather
                    #saved_values.current_correlations_for_parallel = current_correlations
                    
                if(saved_values.initialized.item() < GPA.initial_correlation_batches):#*2?
                    #for the first 10 iterations average out the initial conditions a little bit
                    #at the beginning have it equal the actual average, not the abs average
                    #this is because the best is the abs of running best, but running best is average of a bunch of positives and negatives, so to just initialize as a single value it it a high positive or negative
                
                    saved_values.candidate_grad_average_for_scaling *= saved_values.initialized
                    saved_values.candidate_grad_average_for_scaling += grad_in.abs().mean(math_tuple)
                    saved_values.candidate_grad_average_for_scaling /= (saved_values.initialized + 1.0)
                    saved_values.main_grad_average_for_scaling *= saved_values.initialized
                    saved_values.main_grad_average_for_scaling += last_parent_d.abs().mean(math_tuple)
                    saved_values.main_grad_average_for_scaling /= (saved_values.initialized + 1.0)

                    #if(not GPA.using_pia_data_parallel):
                    if(True):
                        saved_values.prev_dendrite_candidate_average *= saved_values.initialized
                        saved_values.prev_dendrite_candidate_average += saved_values.top_dendrite_candidate_averages
                        saved_values.prev_dendrite_candidate_average /= saved_values.initialized + 1.0
                        #print('init update prev_dendrite_candidate_average')
                        #print(saved_values.prev_dendrite_candidate_average)

                        cor = current_correlations - (saved_values.prev_dendrite_candidate_average * saved_values.parents_average_d_vector) # / net['layers'][l]['sumSqError'][j]
                        #print('init update cor')
                        #print(cor)

                        saved_values.prev_dendrite_candidate_correlation *= saved_values.initialized
                        saved_values.prev_dendrite_candidate_correlation += cor
                        saved_values.prev_dendrite_candidate_correlation /= saved_values.initialized + 1.0
                        #print('init update prev')
                        #print(saved_values.prev_dendrite_candidate_correlation)
                    #else:
                        #saved_values.current_correlations_for_parallel.copy_(current_correlations)
                    #and other values should be zeroed so they dont effect things during this initialization step
                    saved_values.best_score.copy_(saved_values.best_score.detach() * 0)
                    saved_values.previous_best_score.copy_(saved_values.previous_best_score.detach() * 0)
                    saved_values.initialized += 1.0
                    #print('initialized')
                    #print(saved_values.initialized.item())
                    scalar = 0.0000000
                else:
                    '''
                    if this candidate is getting errors so low that the average at this point is 0 it is likely because vanishing gradient has died so theres not much to do here anyway
                    just set scalar to 0 and move on.  TODO: see if there is a better way to to this?  When it was caught with with autograd.detect_anomaly(): around forward->backward .normal_pass_average_d was actually
                    just a super small number but not exactly 0.  this means there is some amount of error it just is getting deleted after averaging because of float resolution.
                    '''
                    if(saved_values.candidate_grad_average_for_scaling.mean().item() == 0):
                        #pdb.set_trace()
                        scalar = 0.0
                    else:
                        #saved_values.candidate_grad_average_for_scaling = grad_in.abs().mean(math_tuple) * 0.001 + saved_values.candidate_grad_average_for_scaling * 0.999
                        #grad_in = (grad_in * (saved_values.parents_average_d_vector.abs().mean()/saved_values.candidate_grad_average_for_scaling.abs().mean())) / saved_values.current_parent_d.abs().std()#.view(1,-1,1,1))
                        #scalar = saved_values.parents_average_d_vector.abs().mean()/saved_values.candidate_grad_average_for_scaling.abs().mean()
                        scalar = saved_values.main_grad_average_for_scaling.mean()/saved_values.candidate_grad_average_for_scaling.mean()
                        #print('\n\n%s scaler ended up as ' % saved_values.layer_name)
                        #print(scalar)
                        #print('with')
                        #print(saved_values.parents_average_d_mags.mean())
                        #print('from')
                        #print(saved_values.main_grad_average_for_scaling.mean())
                        #print('and')
                        #print(saved_values.candidate_grad_average_for_scaling.mean())
                        
                        #scalar = (1/saved_values.parents_average_d_sq)
                        #scalar = 1 seems to not make things die.  gotta figure out a way to do this scalar reasonably.  Why would this not work if its scaling it to the same magnitude as the main gradient is learning?
                        #scalar = 1
                if(GPA.doing_thing):
                    scalar /= saved_values.parent_max_mean_act.item()

                if(saved_values.layer_name == '.layers.29' and yolo_testing):
                    GPA.extra_verbose = False


                grad_in = grad_in * scalar#.view(1,-1,1,1))
                del saved_values.current_parent_d[device_index][-1]
                del saved_values.dendrite_outs[device_index][-1]
                if(GPA.extra_verbose):
                   print('%s completing Dendrite backward' % saved_values.layer_name)
            
                return grad_in, None
    
            
    return Tagger.apply(inp)


def grad_killer(inp):
    class Killer(torch.autograd.Function):
        @staticmethod
        def forward(ctx, inp):
            #print('forward called')
            return inp
        @staticmethod
        def backward(ctx, grad_out):
            #print('backward called')
            return grad_out * 0, None
    return Killer.apply(inp)


def no_forward(inp):
    class no_forward(torch.autograd.Function):
        @staticmethod
        def forward(ctx, inp):
            return inp * 0
        @staticmethod
        def backward(ctx, grad_out):
            return grad_out     
    return no_forward.apply(inp)
### END CLOSED ONLY
        
class DendriteValueTracker(nn.Module):
    def __init__(self, initialized, activation_function_value, name, input_dimensions, out_channels=-1):
        super(DendriteValueTracker, self).__init__()
        
        self.layer_name = name
        
        for val_name in dendrite_init_values:
            self.register_buffer(val_name, torch.zeros(1, device=GPA.device, dtype=GPA.d_type))
        self.initialized[0] = initialized
        self.activation_function_value = activation_function_value
        self.register_buffer('this_input_dimensions', input_dimensions.clone().detach())
        if((self.this_input_dimensions == 0).sum() != 1):
            print('3 need exactly one 0 in the input dimensions: %s' % self.layer_name)
            print(self.this_input_dimensions)
            sys.exit(-1)
        self.register_buffer('this_node_index', (input_dimensions == 0).nonzero(as_tuple=True)[0])
        if(out_channels != -1):
            self.setup_arrays(out_channels)   
        else:
            self.out_channels = -1

    def print(self):
        total_string = 'Value Tracker:'
        for val_name in dendrite_init_values:
            total_string += '\t%s:\n\t\t' % val_name
            total_string += getattr(self,val_name).__repr__()
            total_string += '\n'
        for val_name in dendrite_tensor_values:
            if(not getattr(self,val_name,None) is None):
                total_string += '\t%s:\n\t\t' % val_name
                total_string += getattr(self,val_name).__repr__()
                total_string += '\n'
        print(total_string)
    
    def set_this_input_dimensions(self, new_input_dimensions):
        if type(new_input_dimensions) is list:
            new_input_dimensions = torch.tensor(new_input_dimensions)
        delattr(self, 'this_input_dimensions')
        self.register_buffer('this_input_dimensions', new_input_dimensions.detach().clone()) 
        if (new_input_dimensions == 0).sum() != 1:
            print('4 need exactly one 0 in the input dimensions: %s' % self.layer_name)
            print(new_input_dimensions)
            sys.exit(-1)
        self.this_node_index.copy_((new_input_dimensions == 0).nonzero(as_tuple=True)[0][0])

    def set_out_channels(self, shape_values):
        if(type(shape_values) == torch.Size):
            self.out_channels = int(shape_values[self.this_node_index])
        else:
            self.out_channels = int(shape_values[self.this_node_index].item())

    def setup_arrays(self, out_channels):
        self.out_channels = out_channels
        for val_name in dendrite_tensor_values:
            self.register_buffer(val_name, torch.zeros(out_channels, device=GPA.device, dtype=GPA.d_type))
 
        for name in value_tracker_arrays:
            # if its not copying then just make arrays so they can get deleted every time
            #if(not GPA.using_pia_data_parallel):
            setattr(self,name,{})
            count = 1
            if torch.cuda.device_count() > count:
                count = torch.cuda.device_count()
            for i in range(count):
                getattr(self,name)[i] = []
            #else: # if it is copying make parameter lists so they are separtae and deleiton is not required
                #setattr(self,name,torch.nn.ParameterList())

        #parent values
        for val_name in dendrite_single_values:
            self.register_buffer(val_name, torch.zeros(1, device=GPA.device, dtype=GPA.d_type))            
        
    def reinitialize_for_pai(self, initialized):
        if(self.out_channels == -1):
            print('You have a converted module that was never initialized')
            print('This likely means it not being added to the autograd graph')
            print('Check your forward function that it is actually being used')
            print('If its not you should really delete it, but you can also add')
            print('the name below to GPA.module_ids_to_track to not convert it')
            print(self.layer_name)
            print('with:')
            print('GPA.module_names_to_track += [\'' + self.layer_name + '\']')
            print('This can also happen while testing_dendrite_capacity if you')
            print('run a validation cycle and try to add Dendrites before doing any training.\n')
            
        self.initialized[0] = initialized
        for val_name in dendrite_re_init_values:
            if((not val_name in non_live_skip_values) or GPA.learn_dendrites_live):
                setattr(self,val_name,getattr(self,val_name) * 0)

        if(GPA.doing_thing):
            self.parent_max_mean_act.copy_(self.normal_pass_max_mean_act.detach().clone())
            self.parent_max_mean_act.requires_grad = False
        #self.parents_average_d_mags.copy_(self.normal_pass_average_d_mags.double().detach().clone())
        self.parents_average_d_vector.copy_(self.normal_pass_average_d.detach().clone())
        #self.parents_average_d_sq.copy_(self.normal_pass_average_d_sq.double().mean().detach().clone())
        self.parents_average_d_vector.requires_grad = False
        #self.parents_average_d_sq.requires_grad = False
        #self.parents_average_d_mags.requires_grad = False
        