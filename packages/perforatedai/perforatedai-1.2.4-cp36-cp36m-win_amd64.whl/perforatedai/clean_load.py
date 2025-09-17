from perforatedai import globals_perforatedai as GPA
from perforatedai import modules_perforatedai as PA
from perforatedai import models_perforatedai as MPA
from perforatedai import utils_perforatedai as UPA
from perforatedai import module_layer_tracker_perforatedai as TPA

from safetensors.torch import load_file
import copy

import torch.nn as nn
import torch
import pdb


'''
import modules_perforatedai as PA
import utils_perforatedai as UPA
import cleanPAI as CPAI

net = UPA.load_system('sigmoid_linear', 'system') 
net = CPAI.obfusicate_network(net)

import torch
torch.save(net, 'temp/temp.pt')

import clean_load as CL
import torch

net = torch.load('temp/temp.pt')
net = CL.refresh_net(net)

import torch
net.forward(torch.ones(128,1,29,29).to('cuda'))




import modules_perforatedai as PA
import utils_perforatedai as UPA
import cleanPAI as CPAI
from transformers.models.wav2vec2.modeling_wav2vec2 import *

net = UPA.load_system('temp', 'system')    
net = CPAI.obfusicate_network(net)
import torch
torch.save(net, 'temp/temp.pt')

import clean_load as CL
import torch

net = torch.loadB('temp/temp.pt')
net = CL.refresh_net(net)

import torch
net.forward(torch.ones(8,16000).to('cuda'))
'''

#function to convert layers which had to be customized back into their original form. eg Wav2Vec2Projector back to just using a regular projector and not wprojector

#from now on when creating a module to replace, also need to make a backward replacement function to put things back.

from threading import Thread


doing_threading = False
loaded_full_print = False

class PAIModulePyThread(nn.Module):
    def __init__(self, original_module):
        super(PAIModulePyThread, self).__init__()
        self.layer_array = original_module.layer_array
        self.processor_array = original_module.processor_array
        self.skip_weights = original_module.skip_weights
        self.register_buffer('node_index', original_module.node_index.clone().detach())
        self.register_buffer('module_id', original_module.module_id.clone().detach())
        self.register_buffer('num_cycles', original_module.num_cycles)
        self.register_buffer('view_tuple', original_module.view_tuple)

    #this was to hide that modules are wrapped but now thats part of instructions
    '''
    def __str__(self):
        if(loaded_full_print):
            total_string = 'PAILayer(\n\t'
            total_string += self.layer_array[-1].__str__().replace('\n','\n\t')
            total_string += '\n)'
        else:
            total_string = 'PAILayer('
            total_string += self.layer_array[-1].__class__.__name__
            total_string += ')'
        return total_string
    def __repr__(self):
        return self.__str__()
    '''
    def process_and_forward(self, *args2, **kwargs2):
        c = args2[0]
        dendrite_outs = args2[1]
        args2 = args2[2:]
        if(self.processor_array[c] != None):
            args2, kwargs2 = self.processor_array[c].pre(*args2, **kwargs2)
        out_values = self.layer_array[c](*args2, **kwargs2)
        if(self.processor_array[c] != None):
            out = self.processor_array[c].post(out_values)
        else:
            out = out_values
        dendrite_outs[c] = out
    
    def process_and_pre(self, *args, **kwargs):
        dendrite_outs = args[0]
        args = args[1:]
        out = self.layer_array[-1].forward(*args, **kwargs)
        if not self.processor_array[-1] is None:
            out = self.processor_array[-1].pre(out)
        dendrite_outs[len(self.layer_array)-1] = out
        
    def forward(self, *args, **kwargs):
        #this is currently false anyway, just remove the doing multi idea
        doing_multi = doing_threading
        dendrite_outs = [None] * len(self.layer_array)
        threads = {}
        for c in range(0,len(self.layer_array)-1):
            args2, kwargs2 = args, kwargs
            if(doing_multi):
                threads[c] = Thread(target=self.process_and_forward, args=(c, dendrite_outs, *args), kwargs=kwargs)
            else:
                self.process_and_forward(c, dendrite_outs, *args2, **kwargs2)
        if(doing_multi):
            threads[len(self.layer_array)-1] = Thread(target=self.process_and_pre, args=(dendrite_outs, *args), kwargs=kwargs)
        else:
            self.process_and_pre(dendrite_outs, *args, **kwargs)
        if(doing_multi):
            for i in range(len(dendrite_outs)):
                threads[i].start()
            for i in range(len(dendrite_outs)):
                threads[i].join()
        for out_index in range(0,len(self.layer_array)):
            current_out = dendrite_outs[out_index]
            if(len(self.layer_array) > 1):
                for in_index in range(0,out_index):
                    current_out += self.skip_weights[out_index][in_index,:].view(self.view_tuple.tolist()).to(current_out.device) * dendrite_outs[in_index]    
                if(out_index < len(self.layer_array)-1):
                    current_out = GPA.pb_forward_function(current_out)
            dendrite_outs[out_index] = current_out
        if not self.processor_array[-1] is None:
            current_out = self.processor_array[-1].post(current_out)
        return current_out

'''
class PAIModuleJitThread(nn.Module):
    def __init__(self, original_module):
        super(PAIModuleJitThread, self).__init__()
        self.layer_array = nn.Sequential(*(original_module.layer_array))
        self.processor_array = original_module.processor_array
        self.skip_weights = original_module.skip_weights
        self.node_index = original_module.node_index
        self.view_tuple = []

    def process_and_forward(self, args2):
        c = args2[0]
        args2 = args2[1:]
        if(self.processor_array[c][1] != None):
            args2, kwargs2 = self.processor_array[c][1].pre(args2)
        out_values = self.layer_array[c](args2)
        if(self.processor_array[c][2] != None):
            out = self.processor_array[c][2].post(out_values)
        else:
            out = out_values
        return out
    
    def process_and_pre(self, args):
        out = self.layer_array[-1].forward(args)
        if not self.processor_array[-1][0] is None:
            out = self.processor_array[-1][0].pre(out)
        return out
    def forward(self, args):
        doing_multi = True
        dendrite_outs = {}            
        for c in range(0,len(self.layer_array)-1):
            args2 = args, 
            if(doing_multi):
                dendrite_outs[c] = torch.jit._fork(self.process_and_forward, c, args)
            else:
                dendrite_outs[c] = self.process_and_forward(c, args2)
        if(doing_multi):
            dendrite_outs[len(self.layer_array)-1] = torch.jit._fork(self.process_and_pre, args)
        else:
            dendrite_outs[len(self.layer_array)-1] = self.process_and_pre(args)
        if(doing_multi):
            for i in range(len(dendrite_outs)):
                dendrite_outs[i] = torch.jit._wait(dendrite_outs[i])
        for out_index in range(0,len(self.layer_array)):
            current_out = dendrite_outs[out_index]
            if(self.view_tuple == []):
                for dim in range(len(current_out.shape)):
                    if dim == self.node_index:
                        self.view_tuple.append(-1)
                        continue
                    self.view_tuple.append(1)
            if(len(self.layer_array) > 1):
                for in_index in range(0,out_index):
                    current_out += self.skip_weights[out_index][in_index,:].view(self.view_tuple).to(current_out.device) * dendrite_outs[in_index]    
                if(out_index < len(self.layer_array)-1):
                    current_out = GPA.pb_forward_function(current_out)
            dendrite_outs[out_index] = current_out
        if not self.processor_array[-1][3] is None:
            current_out = self.processor_array[-1][3].post(current_out)
        return current_out
    
class PAIModuleJitThread2(nn.Module):
    def __init__(self, original_module):
        super(PAIModuleJitThread2, self).__init__()
        self.layer_array = original_module.layer_array
        self.processor_array = original_module.processor_array
        self.skip_weights = original_module.skip_weights
        self.node_index = original_module.node_index
        self.view_tuple = []

    def process_and_forward(self, *args2, **kwargs2):
        c = args2[0]
        args2 = args2[1:]
        if(self.processor_array[c][1] != None):
            args2, kwargs2 = self.processor_array[c][1].pre(*args2, **kwargs2)
        out_values = self.layer_array[c](*args2, **kwargs2)
        if(self.processor_array[c][2] != None):
            out = self.processor_array[c][2].post(out_values)
        else:
            out = out_values
        return out
    
    def process_and_pre(self, *args, **kwargs):
        out = self.layer_array[-1].forward(*args, **kwargs)
        if not self.processor_array[-1][0] is None:
            out = self.processor_array[-1][0].pre(out)
        return out
    def forward(self, *args, **kwargs):
        doing_multi = True
        dendrite_outs = {}            
        for c in range(0,len(self.layer_array)-1):
            args2, kwargs2 = args, kwargs
            if(doing_multi):
                dendrite_outs[c] = torch.jit._fork(self.process_and_forward, c, *args, **kwargs)
            else:
                dendrite_outs[c] = self.process_and_forward(c, *args2, **kwargs2)
        if(doing_multi):
            dendrite_outs[len(self.layer_array)-1] = torch.jit._fork(self.process_and_pre, *args, **kwargs)
        else:
            dendrite_outs[len(self.layer_array)-1] = self.process_and_pre(*args, **kwargs)
        if(doing_multi):
            for i in range(len(dendrite_outs)):
                dendrite_outs[i] = torch.jit._wait(dendrite_outs[i])
        for out_index in range(0,len(self.layer_array)):
            current_out = dendrite_outs[out_index]
            if(self.view_tuple == []):
                for dim in range(len(current_out.shape)):
                    if dim == self.node_index:
                        self.view_tuple.append(-1)
                        continue
                    self.view_tuple.append(1)
            if(len(self.layer_array) > 1):
                for in_index in range(0,out_index):
                    current_out += self.skip_weights[out_index][in_index,:].view(self.view_tuple).to(current_out.device) * dendrite_outs[in_index]    
                if(out_index < len(self.layer_array)-1):
                    current_out = GPA.pb_forward_function(current_out)
            dendrite_outs[out_index] = current_out
        if not self.processor_array[-1][3] is None:
            current_out = self.processor_array[-1][3].post(current_out)
        return current_out
'''
'''
class PAIModule2(nn.Module):
    def __init__(self, original_module):
        super(PAIModule2, self).__init__()
        self.layer_array = original_module.layer_array
        self.processor_array = original_module.processor_array
        self.voting_layers = original_module.voting_layers
    def process_and_forward(*args2, **kwargs2):
        if(self.processor_array[c][1] != None):
            args2, kwargs2 = self.processor_array[c][1].pre(*args2, **kwargs2)
        out_values = self.layer_array[c](*args2, **kwargs2)
        if(self.processor_array[c][2] != None):
            outs = self.processor_array[c][2].post(out_values)
        else:
            outs = out_values
        return outs
    def forward(self, *args, **kwargs):
        dendrite_outs = {}            
        for c in range(0,len(self.layer_array)-1):
            args2, kwargs2 = args, kwargs
            dendrite_outs[c] = self.process_and_forward(c, *args2, **kwargs2)
        out = self.layer_array[-1](*args, **kwargs)
        if not self.processor_array[-1][0] is None:
            out = self.processor_array[-1][0].pre(out)
        dendrite_outs[len(self.layer_array)-1] = out
        for out_index in range(0,len(self.layer_array)):
            current_out = dendrite_outs[out_index]
            if(len(self.layer_array) > 1):
                for in_index in range(0,out_index):
                    current_out += self.voting_layers[out_index][in_index](dendrite_outs[in_index])
                if(out_index < len(self.layer_array)-1):
                    current_out = GPA.pb_forward_function(current_out)
            dendrite_outs[out_index] = current_out
        if not self.processor_array[-1][3] is None:
            current_out = self.processor_array[-1][3].post(current_out)
        return current_out
'''
'''
class PAIModuleOld(nn.Module):
    def __init__(self, original_module):
        super(PAIModuleOld, self).__init__()
        self.layer_array = original_module.layer_array
        self.processor_array = original_module.processor_array
        self.voting_layers = original_module.voting_layers
        
    def forward(self, *args, **kwargs):
        #pdb.set_trace()
        dendrite_outs = {}            
        for c in range(0,len(self.layer_array)-1):
            args2, kwargs2 = args, kwargs
            if(self.processor_array[c][1] != None):
                args2, kwargs2 = self.processor_array[c][1].pre(*args2, **kwargs2)
            out_values = self.layer_array[c](*args2, **kwargs2)
            if(self.processor_array[c][2] != None):
                dendrite_outs[c] = self.processor_array[c][2].post(out_values)
            else:
                dendrite_outs[c] = out_values
        try:
            out = self.layer_array[-1](*args, **kwargs)
        except:
            pdb.set_trace()
        if not self.processor_array[-1][0] is None:
            out = self.processor_array[-1][0].pre(out)
        dendrite_outs[len(self.layer_array)-1] = out
        for out_index in range(0,len(self.layer_array)):
            current_out = dendrite_outs[out_index]
            if(len(self.layer_array) > 1):
                for in_index in range(0,out_index):
                    current_out += self.voting_layers[out_index][in_index](dendrite_outs[in_index])
                if(out_index < len(self.layer_array)-1):
                    current_out = GPA.pb_forward_function(current_out)
            dendrite_outs[out_index] = current_out
        if not self.processor_array[-1][3] is None:
            current_out = self.processor_array[-1][3].post(current_out)
        return current_out
'''
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


'''
This is to set if want to try doing threading or not
'''

ModuleType = PAIModulePyThread
doing_threading = False

def make_module(module):
    #if(ModuleType is PAIModuleJitThread):
        #torch.jit.script(ModuleType(module))
    #else:
    return ModuleType(module)

def refresh_pai(net, depth, name_so_far, converted_list):
    if(GPA.verbose):
        print('CL calling convert on %s depth %d' % (net, depth))
        print('CL calling convert on %s: %s, depth %d' % (name_so_far, type(net).__name__, depth))
    if(type(net) is ModuleType):
        if(GPA.verbose):
            print('this is only being called because something in your model is pointed to twice by two different variables.  Highest thing on the list is one of the duplicates')
        return net
    all_members = net.__dir__()
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList) or issubclass(type(net),list):
        for submodule_id, layer in net.named_children():
            if(net != net.get_submodule(submodule_id)):
                converted_list += [ name_so_far + '[' + str(submodule_id) + ']']
                setattr(net,submodule_id,refresh_pai(net.get_submodule(submodule_id), depth + 1, name_so_far + '[' + str(submodule_id) + ']', converted_list))
            #else:
                #print('%s is a self pointer so skipping' % (name_so_far + '[' + str(submodule_id) + ']'))
            if (type(net.get_submodule(submodule_id)).__name__ == 'PAILayer'):
                #print('Seq sub is in conversion list so initing PAI for: %s' % name_so_far + '[' + str(submodule_id) + ']')
                setattr(net,submodule_id,make_module(get_pretrained_pai_var(net, submodule_id)))
    elif(type(net) in GPA.modules_to_skip):
        #print('skipping type for returning from call to: %s' % (name_so_far)) 
        return net
    else:
        for member in all_members:
            sub_name = name_so_far + '.' + member

            if(member == 'device' or member == 'dtype'):
                continue
            if(sub_name in GPA.module_names_to_not_save):
                continue
            if(name_so_far == ''):
                if(sub_name in GPA.module_names_to_not_save
                    or sub_name in converted_list):
                    if(GPA.verbose):
                        print('Skipping %s during save' % sub_name)
                    continue
           
            
            if issubclass(type(getattr(net,member,None)),nn.Module) or member == 'layer_array':
                converted_list += [sub_name]
                #pdb.set_trace()
                if(net != getattr(net,member)):
                    setattr(net,member,refresh_pai(getattr(net,member), depth+1, sub_name, converted_list))
                #else:
                    #print('%s is a self pointer so skipping' % (name_so_far + '.' + member))
            if (type(getattr(net,member,None)).__name__ == 'PAILayer'):
                #print('sub is in conversion list so initing PAI for: %s' % name_so_far + '.' + member)
                setattr(net,member,make_module(get_pretrained_pai_attr(net,member)))            
    #print('returning from call to: %s' % (name_so_far)) 
    if (type(net).__name__ == 'PAILayer'):
        net = make_module(net)
    #pdb.set_trace()
    return net


#putting pretrainedNormal, pretrained_dendrite as a flag here becqause might want to replace modules 
#pretraiend PAI is required isntead of just loading in case a system needs to do any specific instantiation stuff
#that PAI conflicts with and then convert network needs to be called after that is setup
def refresh_net(pretrained_dendrite):

    net = refresh_pai(pretrained_dendrite, 0, '', [])
    #del net.tracker_string
    return net
