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
import warnings
from perforatedai import globals_perforatedai as GPA
from perforatedai import modules_perforatedai as PA
from perforatedai import models_perforatedai as MPA
from perforatedai import check_license
from perforatedai import clean_load as CL
from perforatedai import blockwise_perferatedai as BPA
from perforatedai import module_layer_tracker_perforatedai as TPA

import copy

from safetensors.torch import load_file
from safetensors.torch import save_file


def initialize_pai(model, doing_pai=True, save_name='PAI', making_graphs=True, maximizing_score=True, num_classes=10000000000, values_per_train_epoch=-1, values_per_val_epoch=-1, zooming_graph=True):
    GPA.pai_tracker = TPA.module_layer_tracker_perforatedai(doing_pai=doing_pai,save_name=save_name)
    GPA.SAVE_NAME = save_name
    model = GPA.pai_tracker.initialize(model, doing_pai=doing_pai, save_name=save_name, making_graphs=making_graphs, maximizing_score=maximizing_score, num_classes=num_classes, values_per_train_epoch=-values_per_train_epoch, values_per_val_epoch=values_per_val_epoch, zooming_graph=zooming_graph)
    return model

## CLOSED ONLY
def check_requires_grad(module):
  for param in module.parameters():
    if param.requires_grad:
      return True
  return False

def debug_print_grad_modules(net, depth, name_so_far):
    print('%s: has req grads: %d' % (name_so_far, check_requires_grad(net)))
    all_members = net.__dir__()
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submodule_id, layer in net.named_children():
            sub_name = name_so_far + '.' + str(submodule_id)
            if(net != net.get_submodule(submodule_id)):
                debug_print_grad_modules(net.get_submodule(submodule_id), depth + 1, sub_name)
    else:
        for member in all_members:
            sub_name = name_so_far + '.' + member
            try:
                getattr(net,member,None)
            except:
                continue
            if issubclass(type(getattr(net,member,None)),nn.Module):
                #pdb.set_trace()
                if(net != getattr(net,member)):
                    debug_print_grad_modules(getattr(net,member), depth+1, sub_name)
### END CLOSED ONLY

def get_pai_modules(net, depth):
    #print('calling get params on %s, depth %d' % (type(net).__name__, depth))
    all_members = net.__dir__()
    this_list = []
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submodule_id, layer in net.named_children():
            #if there is a self pointer ignore it
            if net.get_submodule(submodule_id) is net:
                continue
            if type(net.get_submodule(submodule_id)) is PA.PAINeuronModule:
                this_list = this_list + [net.get_submodule(submodule_id)]

            else:
                #print('sub list not one so continuing')
                this_list = this_list + get_pai_modules(net.get_submodule(submodule_id), depth + 1)            
    else:
        for member in all_members:        
            #if(type(net).__name__ == 'ConvModule'):
                #pdb.set_trace()
            if getattr(net,member,None) is net:
                continue
            if type(getattr(net,member,None)) is PA.PAINeuronModule:
                #print('sub is one so converting')
                this_list = this_list + [getattr(net,member)]
                #print(this_list)            
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                this_list = this_list + get_pai_modules(getattr(net,member), depth+1)
            #else:
                #print('not calling convert on %s depth %d' % (member, depth))            
            
    #print('finish depth %d' % depth)
    #print(this_list)
    return this_list

def get_tracked_modules(net, depth):
    #print('calling get params on %s, depth %d' % (type(net).__name__, depth))
    all_members = net.__dir__()
    this_list = []
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submodule_id, layer in net.named_children():
            #if there is a self pointer ignore it
            if net.get_submodule(submodule_id) is net:
                continue
            if type(net.get_submodule(submodule_id)) is PA.TrackedNeuronLayer:
                this_list = this_list + [net.get_submodule(submodule_id)]

            else:
                #print('sub list not one so continuing')
                this_list = this_list + get_tracked_modules(net.get_submodule(submodule_id), depth + 1)            
    else:
        for member in all_members:        
            #if(type(net).__name__ == 'ConvModule'):
                #pdb.set_trace()
            if getattr(net,member,None) is net:
                continue
            if type(getattr(net,member,None)) is PA.TrackedNeuronLayer:
                #print('sub is one so converting')
                this_list = this_list + [getattr(net,member)]
                #print(this_list)            
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                this_list = this_list + get_tracked_modules(getattr(net,member), depth+1)
            #else:
                #print('not calling convert on %s depth %d' % (member, depth))            
            
    #print('finish depth %d' % depth)
    #print(this_list)
    return this_list 

def get_pai_module_params(net, depth):
    #print('calling get params on %s, depth %d' % (type(net).__name__, depth))
    all_members = net.__dir__()
    this_list = []
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submodule_id, layer in net.named_children():
            if type(net.get_submodule(submodule_id)) is PA.PAINeuronModule:
                #print('sub list is one so converting')
                for param in net.get_submodule(submodule_id).parameters():
                    if(param.requires_grad):
                        this_list = this_list + [param]
                #print(this_list)

            else:
                #print('sub list not one so continuing')
                this_list = this_list + get_pai_module_params(net.get_submodule(submodule_id), depth + 1)            
    else:
        for member in all_members:
            if(getattr(net,member,None) == net):
                continue  
            #if(type(net).__name__ == 'ConvModule'):
                #pdb.set_trace()
            if type(getattr(net,member,None)) is PA.PAINeuronModule:
                #print('sub is one so converting')
                for param in getattr(net,member).parameters():
                    if(param.requires_grad):
                        this_list = this_list + [param]
                #print(this_list)            
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                this_list = this_list + get_pai_module_params(getattr(net,member), depth+1)
            #else:
                #print('not calling convert on %s depth %d' % (member, depth))            
            
    #print('finish depth %d' % depth)
    #print(this_list)
    return this_list

def get_pai_network_params(net):
    param_list = get_pai_module_params(net, 0)
    #pdb.set_trace()
    return param_list


def replace_predefined_modules(start_module,  pretrained_dendrite):
    index = GPA.modules_to_replace.index(type(start_module))
    return GPA.replacement_modules[index](start_module)


def get_pretrained_pai_attr(pretrained_dendrite, member):
    if(pretrained_dendrite is None):
        return None
    else:
        return getattr(pretrained_dendrite,member)

def get_pretrained_pai_var(pretrained_dendrite, submodule_id):
    if(pretrained_dendrite is None):
        return None
    else:
        return pretrained_dendrite.get_submodule(submodule_id)

def convert_module(net,  pretrained_dendrite, depth, name_so_far, converted_list, converted_names_list):
    if(GPA.verbose):
        print('calling convert on %s depth %d' % (net, depth))
        print('calling convert on %s: %s, depth %d' % (name_so_far, type(net).__name__, depth))
    if((type(net) is PA.PAINeuronModule)
       or type(net) is PA.TrackedNeuronLayer):
        if(GPA.verbose):
            print('This is only being called because something in your model is pointed to twice by two different variables.  Highest thing on the list is one of the duplicates')
        return net
    all_members = net.__dir__()
    if(GPA.extra_verbose):
        print('all members:')
        for member in all_members:
            print(' - %s' % member)
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submodule_id, layer in net.named_children():
            sub_name = name_so_far + '.' + str(submodule_id)
            if(sub_name in GPA.module_ids_to_track):
                if(GPA.verbose):
                    print('Seq ID is in track IDs: %s' % sub_name)
                setattr(net,submodule_id,PA.tracked_neuron_layer(net.get_submodule(submodule_id), sub_name))
                continue
            if(sub_name in GPA.module_ids_to_convert):
                if(GPA.verbose):
                    print('Seq ID is in convert IDs: %s' % sub_name)
                setattr(net,submodule_id,PA.pai_neuron_layer(net.get_submodule(submodule_id), sub_name))
                continue
            if type(net.get_submodule(submodule_id)) in GPA.modules_to_replace:
                if(GPA.verbose):
                    print('Seq sub is in replacement module so replacing: %s' % sub_name)
                setattr(net,submodule_id,replace_predefined_modules(net.get_submodule(submodule_id), get_pretrained_pai_var(pretrained_dendrite, submodule_id)))
            if ((type(net.get_submodule(submodule_id)) in GPA.modules_to_track)
                or
                (type(net.get_submodule(submodule_id)).__name__ in GPA.module_names_to_track)):
                if(GPA.verbose):
                    print('Seq sub is in tracking list so initiating tracked for: %s' % sub_name)
                setattr(net,submodule_id,PA.TrackedNeuronLayer(net.get_submodule(submodule_id),sub_name))
            elif (type(net.get_submodule(submodule_id)) in GPA.modules_to_convert
                or
                type(net.get_submodule(submodule_id)).__name__ in GPA.module_names_to_convert
                or (sub_name in GPA.module_ids_to_convert)):
                if(GPA.verbose):
                    print('Seq sub is in conversion list so initiating PAI for: %s' % sub_name)
                if(issubclass(type(net.get_submodule(submodule_id)), torch.nn.modules.batchnorm._BatchNorm) or issubclass(type(net.get_submodule(submodule_id)), torch.nn.modules.instancenorm._InstanceNorm) or
                issubclass(type(net.get_submodule(submodule_id)), torch.nn.modules.normalization.LayerNorm)):
                #and GPA.internal_batch_norm:
                    print('You have an unwrapped normalization layer, this is not recommended: ' + name_so_far)
                    pdb.set_trace()    
                setattr(net,submodule_id,PA.PAINeuronModule(net.get_submodule(submodule_id), sub_name, pretrained_dendrite=get_pretrained_pai_var(pretrained_dendrite, submodule_id)))
            else:
                if(net != net.get_submodule(submodule_id)):
                    converted_list += [id(net.get_submodule(submodule_id))]
                    converted_names_list += [sub_name]
                    setattr(net,submodule_id,convert_module(net.get_submodule(submodule_id),  get_pretrained_pai_var(pretrained_dendrite, submodule_id), depth + 1, sub_name, converted_list, converted_names_list))
                #else:
                    #print('%s is a self pointer so skipping' % (name_so_far + '[' + str(submodule_id) + ']'))
    elif(type(net) in GPA.modules_to_skip):
        #print('skipping type for returning from call to: %s' % (name_so_far)) 
        return net
    else:
        for member in all_members:
            sub_name = name_so_far + '.' + member
            if(sub_name in GPA.module_ids_to_track):
                if(GPA.verbose):
                    print('Seq ID is in track IDs: %s' % sub_name)
                setattr(net,member,PA.tracked_neuron_layer(getattr(net,member),sub_name))
                continue
            if(sub_name in GPA.module_ids_to_convert):
                if(GPA.verbose):
                    print('Seq ID is in convert IDs: %s' % sub_name)
                setattr(net,member,PA.pai_neuron_layer(getattr(net,member),sub_name))
                continue
            if(id(getattr(net,member,None)) == id(net)):
                if(GPA.verbose):
                    print('Seq sub is a self pointer: %s' % sub_name)
                continue
            if(sub_name in GPA.module_names_to_not_save):
                if(GPA.verbose):
                    print('Skipping %s during convert' % sub_name)
                else:
                    if(sub_name == '.base_model'):
                        print('By default skipping base_model.  See \"Safetensors Errors\" section of customization.md to include it.')
                continue
            if(id(getattr(net,member,None)) in converted_list):
                print('The following module has a duplicate pointer within your model: %s' % sub_name)
                print('It is shared with: %s' % converted_names_list[converted_list.index(id(getattr(net,member,None)))])
                print('One of these must be added to GPA.module_names_to_not_save (with the .)')
                sys.exit(0)

            #if(type(net).__name__ == 'ConvModule'):
            # Torch Lightning throws an error when trying to get variables that aren't set yet.  If an error is thrown, just continue.
            try:
                getattr(net,member,None)
            except:
                continue
                
            if type(getattr(net,member,None)) in GPA.modules_to_replace:
                if(GPA.verbose):
                    print('sub is in replacement module so replacing: %s' % sub_name)
                setattr(net,member,replace_predefined_modules(getattr(net,member,None),  get_pretrained_pai_attr(pretrained_dendrite, member)))
            if (type(getattr(net,member,None)) in GPA.modules_to_track
                or
                type(getattr(net,member,None)).__name__ in GPA.module_names_to_track
                or sub_name in GPA.module_ids_to_track):
                if(GPA.verbose):
                    print('sub is in tracking list so initiating tracked for: %s' % sub_name)
                setattr(net,member,PA.TrackedNeuronLayer(getattr(net,member),sub_name))
            elif (type(getattr(net,member,None)) in GPA.modules_to_convert
                or
                type(getattr(net,member,None)).__name__ in GPA.module_names_to_convert
                or (sub_name in GPA.module_ids_to_convert)):
                if(GPA.verbose):
                    print('sub is in conversion list so initiating PAI for: %s' % sub_name)
                setattr(net,member,PA.PAINeuronModule(getattr(net,member),sub_name, pretrained_dendrite=get_pretrained_pai_attr(pretrained_dendrite,member)))
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                #pdb.set_trace()
                if(net != getattr(net,member)):
                    converted_list += [id(getattr(net,member))]
                    converted_names_list += [sub_name]
                    setattr(net,member,convert_module(getattr(net,member),  get_pretrained_pai_attr(pretrained_dendrite,member), depth+1, sub_name, converted_list, converted_names_list))
                #else:
                    #print('%s is a self pointer so skipping' % (sub_name))

            if (issubclass(type(getattr(net,member,None)), torch.nn.modules.batchnorm._BatchNorm) or issubclass(type(getattr(net,member,None)), torch.nn.modules.instancenorm._InstanceNorm) or
                 issubclass(type(getattr(net,member,None)), torch.nn.modules.normalization.LayerNorm)):
                if(not GPA.unwrapped_modules_confirmed):
                    print('potentially found a batchNorm Layer that wont be converted2, this is not recommended: %s' % (sub_name))
                    print('Set GPA.unwrapped_modules_confirmed to True to skip this next time')
                    print('Type \'net\' + enter to inspect your network and see what the module type containing this layer is.')
                    print('Then do one of the following:')
                    print(' - Add the module type to GPA.module_names_to_convert to wrap it entirely')
                    print(' - If the norm layer is part of a sequential wrap it and the previous layer in a PAISequential')
                    print(' - If you do not want to add dendrites to this module add tye type to GPA.module_names_to_track')
                    pdb.set_trace()
            else:
                # don't print private variables with _.  just makes it harder to read
                if(GPA.verbose):
                    if(member[0] != '_' or GPA.extra_verbose == True):
                        print('not calling convert on %s depth %d' % (member, depth))            
    if(GPA.verbose):
        print('returning from call to: %s' % (name_so_far)) 
    #pdb.set_trace()
    return net


#putting pretrainedNormal, pretrained_dendrite as a flag here because might want to replace modules 
#pretrained PAI is required instead of just loading in case a system needs to do any specific instantiation stuff
#that PAI conflicts with and then convert network needs to be called after that is setup
#update later - i dont understand the above comment.  I think these were added when duplicating the main module rather than just adding it by reference. why would you ever want to load a pretrained PAI but then convert something else?
def convert_network(net, pretrained_dendrite = None, layer_name=''):

    license_file = './license.yaml'
    status = check_license.valid_license(license_file)

    if not status:
        print("License Invalid. Quiting...")
        sys.exit(1)

    #if youre loading from a pretrained PAI make sure to reset the tracker to be this ones, otherwise it will load the other ones 
    #now that we are loading the tracker based on the state buffer it doesn't need to be reinitialized
    #if(not pretrained_dendrite is None):
        #GPA.reInitPAI = True
    if type(net) in GPA.modules_to_replace:
        net = replace_predefined_modules(net,  pretrained_dendrite)
    if((type(net) in GPA.modules_to_convert) or
        (type(net).__name__ in GPA.module_names_to_convert)):
        if(layer_name == ''):
            print('converting a single layer without a name, add a layer_name param to the call')
            sys.exit(-1)
        net = PA.PAINeuronModule(net, layer_name, pretrained_dendrite=pretrained_dendrite)
    else:
        net = convert_module(net,  pretrained_dendrite, 0, '', [], [])
    #pdb.set_trace()
    missed_ones = []
    tracked_ones = []
    for name, param in net.named_parameters():
        wrapped = 'wrapped' in param.__dir__()
        if(wrapped):
            if(GPA.verbose):
                print('param %s is now wrapped' % (name))
        else:
            tracked = 'tracked' in param.__dir__()
            if(tracked):
                tracked_ones.append(name)
            else:
                missed_ones.append(name)
    if((len(missed_ones) != 0 or len(tracked_ones) != 0) 
       and GPA.unwrapped_modules_confirmed == False):
        print('\n------------------------------------------------------------------')
        print('The following params are not wrapped.\n------------------------------------------------------------------')
        for name in tracked_ones:
            print(name)
        print('\n------------------------------------------------------------------')
        print('The following params are not tracked or wrapped.\n------------------------------------------------------------------')
        for name in missed_ones:
            print(name)
        print('\n------------------------------------------------------------------')
        print('Modules that are not wrapped will not have Dendrites to optimize them')
        print('Modules that are not tracked can cause errors and is NOT recommended')
        print('Any modules in the second list should be added to module_names_to_track')
        print('Any parameters in the second list can be ignored')
        '''
        Parameters cause a problem with the __getattr__ function.  They also aren't modules, so calling model.param * x for example will cause a problem since its not a forward function.
        '''
        print('------------------------------------------------------------------\nType \'c\' + enter to continue the run to confirm you do not want them to be refined')
        print('Set GPA.unwrapped_modules_confirmed to True to skip this next time')
        print('Type \'net\' + enter to inspect your network and see what the module types of these values are to add them to PGB.module_names_to_convert')
        import pdb; pdb.set_trace()
        #TODO: could also print here the type of the missed ones to find what types should be converted
        print('confirmed')
    net.register_buffer('tracker_string', torch.tensor([]))
    if(pretrained_dendrite):
        GPA.pai_tracker.reset_layer_vector(net,False)
    return net


'''
def string_to_tensor(string):
    ords = list(map(ord, string))
    return torch.tensor(ords)
    
def string_from_tensor(string_tensor):
    # Convert tensor to python list.
    ords = string_tensor.tolist()
    # Convert ordinal values to characters and join them into a string.
    return "".join(map(chr, ords))
'''

def string_to_tensor(string):
    ords = list(map(ord, string))
    ords = torch.tensor(ords)
    #needs to be over 100 or else when dividing by 100 in string_from_tensor can get div by 0
    increment = torch.randint(low=101, high=32767, size=[1])
    ords = ords * increment
    offset = torch.randint(low=0, high=99, size=[1])
    ords = torch.cat((ords, increment*100+offset))
    return ords
    
def string_from_tensor(string_tensor):
    # Convert tensor to python list.
    ords = string_tensor.tolist()
    increment = int(ords[-1]/100)
    ords = (torch.tensor(ords[:-1])/increment).int()
    to_return = ''
    while(len(ords) != 0):
        remaining_ords = ords[100000:]
        ords = ords[:100000]
        to_append = ''.join(map(chr, ords))
        to_return = to_return + to_append
        ords = remaining_ords
    # Convert ordinal values to characters and join them into a string.
    return to_return

def save_system(net, folder, name):
    if(GPA.verbose):
        print('saving system %s' % name)
    temp = string_to_tensor(GPA.pai_tracker.to_string())
    if hasattr(net, 'tracker_string'):
        net.tracker_string = string_to_tensor(GPA.pai_tracker.to_string()).to(next(net.parameters()).device)
    else:
        net.register_buffer('tracker_string', string_to_tensor(GPA.pai_tracker.to_string()).to(next(net.parameters()).device))
    oldList = GPA.pai_tracker.neuron_module_vector
    GPA.pai_tracker.neuron_module_vector = []
    save_net(net, folder, name)
    GPA.pai_tracker.neuron_module_vector = oldList
    #also save a cleaned copy at every point
    pia_save_system(net, folder, name)

def load_system(net, folder, name, load_from_restart = False, switch_call=False, load_from_manual_save=False):
    if(GPA.verbose):
        print('loading system %s' % name)
    net = load_net(net, folder,name)
    GPA.pai_tracker.reset_layer_vector(net,load_from_restart)

    GPA.pai_tracker.from_string(string_from_tensor(net.tracker_string))
    #always reset the timer, this should get rid of those epochs that take crazy long becuse they are using an old time
    GPA.pai_tracker.saved_time = time.time()
    
    GPA.pai_tracker.loaded=True
    #always reset this to 0 so networks will know if they are continuing to improve. dont need to reset running accuracy for this and dont 
    GPA.pai_tracker.member_vars['current_best_validation_score'] = 0
    GPA.pai_tracker.member_vars['epoch_last_improved'] = GPA.pai_tracker.member_vars['num_epochs_run']
    if(GPA.verbose):
        print('after loading epoch last improved is %d mode is %c' % (GPA.pai_tracker.member_vars['epoch_last_improved'], GPA.pai_tracker.member_vars['mode']))
    # Saves take place before the final call to start Epoch
    # so when loading from that point must start with a start_epoch
    # unless there was a manual save outside of the add validation score functions
    if (not switch_call) and (not load_from_manual_save):
        GPA.pai_tracker.start_epoch(internal_call=True)
    return net

    
def save_net(net, folder, name):
    #if running a DDP only save with first thread
    if('RANK' in os.environ):
        if(int(os.environ["RANK"]) != 0):
            return
    #if(not do_not_save_locally or (not (folder[:5] == '/tmp/'))):
        #print('saving extra things function is for internal use only')
        #sys.exit()
    #print('calling save: %s' % name)
    #GPA.pai_tracker.archive_layer()
    if not os.path.isdir(folder):
        os.makedirs(folder)
    save_point = folder + '/'
    if not os.path.isdir(save_point):
        os.mkdir(save_point)
    #net.pai_tracker = GPA.pai_tracker
    for param in net.parameters(): param.data = param.data.contiguous()
    if(GPA.using_safe_tensors):
        save_file(net.state_dict(), save_point + name + '.pt')
    else:
        torch.save(net, save_point + name + '.pt')
    #this is needed because archive taggers deletes everything because tagger objects cant be pickled


### CLOSED ONLY

#add a flag to ignore all warnings
def add_future_warning():
    warnings.filters.insert(0,('ignore', None, Warning, None, 0))

#delete the warning we just set
def remove_future_warning():
    del warnings.filters[0]
### END CLOSED ONLY

def load_net(net, folder, name):
    save_point = folder + '/'
    if(GPA.using_safe_tensors):
        state_dict = load_file(save_point + name + '.pt')
    else:
        add_future_warning()
        #Different versions of torch require this change
        try:
            state_dict = torch.load(save_point + name + '.pt', map_location=torch.device('cpu'), weights_only=False).state_dict()
        except:
            state_dict = torch.load(save_point + name + '.pt', map_location=torch.device('cpu')).state_dict()
        remove_future_warning()
    return load_net_from_dict(net, state_dict)
    
def load_net_from_dict(net, state_dict):
    pai_modules = get_pai_modules(net,0)
    if(pai_modules == []):
        print('PAI load_net and load_system uses a state_dict so it must be called with a net after convert_network has been called')
        sys.exit()
    for module in pai_modules:
        #Set up name to be what will be saved in the state dict
        module_name = module.name
        #this should always be true
        if module_name[0] == '.':
            #strip "."
            module_name = module_name[1:]
        # if it was a dataparallel it will also have a module at the start
        if module_name[:6] == 'module':
            #strip the "module."
            module_name = module_name[7:]
        # if there were no cycles then assume the arrays need to be initialized
        #if module.dendrite_module.num_cycles == 0:
        module.clear_dendrites()
        for tracker in module.dendrite_module.dendrite_values:
            try:
                tracker.setup_arrays(len(state_dict[module_name + '.dendrite_module.dendrite_values.0.top_dendrite_candidate_averages']))
            except Exception as e:
                print(e)
                print('When missing this value it typically means you converted a module but didn\'t actually use it in your forward and backward pass')
                print('module was: %s' % module_name)
                print('check your model definition and forward function and ensure this module is being used properly')
                print('or add it to GPA.module_ids_to_track to leave it out of conversion')
                print('This can also occur if you are only fine tuning some of the network, just add the modules that are being fine tuned.')
                print('Additionally this can happen if you adjusted your model definition after calling initialize_pai')
                print('for example with torch.compile.  If the module name printed above does not contain all modules leading to the main definition')
                print('this is likely the case for your problem. Fix by calling initialize_pai after all other model initialization steps')
                
                import pdb; pdb.set_trace()
                
        #then also perform as many cycles as the state dict has
        num_cycles = int(state_dict[module_name + '.dendrite_module.num_cycles'].item())
        if(num_cycles > 0):
            simulate_cycles(module, num_cycles, doing_pai = True)    
    #net.classifier.classifier[0].dendrite_module.dendrite_values[0].this_node_index
    if hasattr(net, 'tracker_string'):
        net.tracker_string = state_dict['tracker_string']
    else:
        net.register_buffer('tracker_string', state_dict['tracker_string'])
    net.load_state_dict(state_dict)
    net.to(GPA.device)
    return net

def pia_save_system(net, folder, name):
    #print('saving system %s' % name)
    net.member_vars = {}
    for memberVar in GPA.pai_tracker.member_vars:
        if memberVar == 'scheduler_instance' or memberVar == 'optimizer_instance':
            continue
        net.member_vars[memberVar] = GPA.pai_tracker.member_vars[memberVar]
    pai_save_net(net, folder, name)

def deep_copy_pai(net):
    GPA.pai_tracker.clear_all_processors()
    return copy.deepcopy(net)

### CLOSED ONLY

#This returns a clean version of the network for parameter counting and inference
def clean_net(net):
    net2 = BPA.blockwise_network(net)
    net2 = deep_copy_pai(net2)
    net2 = CL.refresh_net(net2)
    return net2

def pai_save_net(net, folder, name):
    #if running a DDP only save with first thread
    if('RANK' in os.environ):
        if(int(os.environ["RANK"]) != 0):
            return

    #print('calling save: %s' % name)
    #GPA.pai_tracker.archive_layer()
    #These deep copys are required or the real model will also have its layers replaced
    net = deep_copy_pai(net)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    save_point = folder + '/'
    if not os.path.isdir(save_point):
        os.mkdir(save_point)
    net = BPA.blockwise_network(net)
    net = deep_copy_pai(net)
    net = CL.refresh_net(net)
    #for _pai versions tracker_string is not needed
    del net.tracker_string
    for param in net.parameters(): param.data = param.data.contiguous()

    if(GPA.using_safe_tensors):
        save_file(net.state_dict(), save_point + name + '_pai.pt')
    else:
        torch.save(net, save_point + name + '_pai.pt')

### END CLOSED ONLY

def simulate_cycles(module, num_cycles, doing_pai):
    check_skipped = GPA.checked_skipped_modules
    if(doing_pai == False):
        return
    GPA.checked_skipped_modules = True
    mode = 'n'
    for i in range(num_cycles):
        if(mode == 'n'):
            module.set_mode('p')
            module.create_new_dendrite_module()
            mode = 'p'
        else:
            module.set_mode('n')
            mode = 'n'
    GPA.checked_skipped_modules = check_skipped

def count_params(net):
    if(not GPA.count_training_params):
        net = deep_copy_pai(net)
        cleaned = clean_net(net)
    parameters = list(cleaned.parameters())
    unique_params = {p.data_ptr(): p for p in parameters}.values()
    return sum(p.numel() for p in unique_params)
    
def change_learning_modes(net, folder, name, doing_pai):    
    if(doing_pai == False):
        #do keep track of times it switched here so other things work out
        #this is so that if you set doing_pai to be false it still does learning rate restart
        GPA.pai_tracker.member_vars['switch_epochs'].append(GPA.pai_tracker.member_vars['num_epochs_run'])
        GPA.pai_tracker.member_vars['last_switch'] = GPA.pai_tracker.member_vars['switch_epochs'][-1]
        GPA.pai_tracker.reset_vals_for_score_reset()
        return net
    if(GPA.pai_tracker.member_vars['mode'] == 'n'):
        current_epoch = GPA.pai_tracker.member_vars['num_epochs_run']
        overwritten_epochs = GPA.pai_tracker.member_vars['overwritten_epochs']
        overwritten_extra = GPA.pai_tracker.member_vars['extra_scores']
        if(GPA.drawing_pai):
            overwritten_val = GPA.pai_tracker.member_vars['accuracies']
        else:
            overwritten_val = GPA.pai_tracker.member_vars['n_accuracies']
        #preloadPAIs = GPA.pai_tracker.member_vars['num_dendrites_added']
        '''
        The only reason that retain_all_dendrites should ever be used is to test GPU memory and 
        configuration.  So just dont load the best system which will be the previous best 
        if this didn't improve things
        '''
        if(not GPA.retain_all_dendrites):
            if(not GPA.silent):
                print('Importing best Model for switch to PA...')
            net = load_system(net, folder, name, switch_call=True)
        else:
            if(not GPA.silent):
                print('Not importing new model since retaining all PAI')
        GPA.pai_tracker.set_dendrite_training() #### MW - I THINK THIS IS WHAT YOU WANT IT CHANGED TO
        GPA.pai_tracker.member_vars['overwritten_epochs'] = overwritten_epochs
        GPA.pai_tracker.member_vars['overwritten_epochs'] += current_epoch - GPA.pai_tracker.member_vars['num_epochs_run']
        GPA.pai_tracker.member_vars['total_epochs_run'] = GPA.pai_tracker.member_vars['num_epochs_run'] + GPA.pai_tracker.member_vars['overwritten_epochs']
        
        if(GPA.save_old_graph_scores):
            GPA.pai_tracker.member_vars['overwritten_extras'].append(overwritten_extra)
            GPA.pai_tracker.member_vars['overwritten_vals'].append(overwritten_val)
        else:
            GPA.pai_tracker.member_vars['overwritten_extras'] = [overwritten_extra]
            GPA.pai_tracker.member_vars['overwritten_vals'] = [overwritten_val]
        if(GPA.drawing_pai):
            GPA.pai_tracker.member_vars['n_switch_epochs'].append(GPA.pai_tracker.member_vars['num_epochs_run'])
        else:
            #append the last switch minus the length of this epoch set
            if(len(GPA.pai_tracker.member_vars['switch_epochs']) == 0):
                #add the first switch
                GPA.pai_tracker.member_vars['n_switch_epochs'].append(GPA.pai_tracker.member_vars['num_epochs_run'])
            else:
                #lastImprovedPoint = (len(self.member_vars['n_accuracies'])-1) - (self.member_vars['num_epochs_run']-self.member_vars['num_epochs_run'])
                GPA.pai_tracker.member_vars['n_switch_epochs'].append(GPA.pai_tracker.member_vars['n_switch_epochs'][-1] + ((GPA.pai_tracker.member_vars['num_epochs_run'])-(GPA.pai_tracker.member_vars['switch_epochs'][-1])))
            
        GPA.pai_tracker.member_vars['switch_epochs'].append(GPA.pai_tracker.member_vars['num_epochs_run'])
        GPA.pai_tracker.member_vars['last_switch'] = GPA.pai_tracker.member_vars['switch_epochs'][-1]
    else:
        if(not GPA.silent):
            print('Switching back to N...')
        setBest = GPA.pai_tracker.member_vars['current_n_set_global_best']
        GPA.pai_tracker.set_neuron_training() #### MW - I THINK THIS IS WHAT YOU WANT IT CHANGED TO
        #append the last switch minus the length of this epoch set
        if(len(GPA.pai_tracker.member_vars['p_switch_epochs']) == 0):
            #need to account for the first one starting at 0
            GPA.pai_tracker.member_vars['p_switch_epochs'].append(((GPA.pai_tracker.member_vars['num_epochs_run']-1)-(GPA.pai_tracker.member_vars['switch_epochs'][-1])))
        else:
            GPA.pai_tracker.member_vars['p_switch_epochs'].append(GPA.pai_tracker.member_vars['p_switch_epochs'][-1] + ((GPA.pai_tracker.member_vars['num_epochs_run'])-(GPA.pai_tracker.member_vars['switch_epochs'][-1])))
        GPA.pai_tracker.member_vars['switch_epochs'].append(GPA.pai_tracker.member_vars['num_epochs_run'])
        GPA.pai_tracker.member_vars['last_switch'] = GPA.pai_tracker.member_vars['switch_epochs'][-1]
        #if want to retain all PAI or learning PAILive and this last one did in fact improve global score
        if(GPA.retain_all_dendrites or (GPA.learn_dendrites_live and setBest)):
            if(not GPA.silent):
                print('Saving model before starting normal training to retain PAINodes regardless of next N Phase results')
            save_system(net, folder, name)
        #if its just doing P for learn PAI live then switch back immediately
        if(GPA.no_extra_n_modes):
            net = change_learning_modes(net, folder, name, doing_pai)
            
    GPA.pai_tracker.member_vars['param_counts'].append(count_params(net))
    
    return net



