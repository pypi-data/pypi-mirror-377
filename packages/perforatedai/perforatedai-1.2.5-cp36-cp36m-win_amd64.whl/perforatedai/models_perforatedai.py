import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F
import torchvision.models.resnet as resnetPT
import math
import pdb
from itertools import chain
from perforatedai import globals_perforatedai as GPA

#if you are using a custom file include like this
import sys
#sys.path.append('/home/rbrenner/PerferatedBackpropagation/examples/FixRes')
#import Res as resnetPT


'''
to use this for sequentials just wrap it.  EG:

nn.Linear(2 * hidden_dim, 512),
nn.LayerNorm(512),
>>
MPA.layer(Batch(nn.Linear(2 * hidden_dim, 512),
nn.LayerNorm(512)),
'''


'''
class Squeezer(torch.nn.Module):
    def __init__(self):
        super(Squeezer, self).__init__()
    def forward(self, x):
        return x.squeeze(0)
'''
'''
class gruBatch(nn.Sequential):
        def __init__(self, gru, bnLayer):
            super(gruBatch, self).__init__()
            self.gru = gru
            self.bnLayer = bnLayer
        def forward(self, x, h):
            x, h = self.gru(x, h)
            x = self.bnLayer(x)
            return x, h
'''
'''
class layerBatchIdentity(nn.Sequential):
        def __init__(self, linLayer, bnLayer, otherLayer = None):
            super(layerBatchIdentity, self).__init__()
            if(otherLayer is None):
                self.model = nn.Sequential(
                    linLayer,bnLayer)
            else:
                self.model = nn.Sequential(
                    linLayer,bnLayer,otherLayer)
        def forward(self, x, identity):
            return self.model(x) + identity['identity']
'''
# General multi output processor for any number that ignores later ones
class MultiOutputProcessor():
    def post_n1(self, *args, **kwargs):
        out = args[0][0]
        extra_out = args[0][1:]
        self.extra_out = extra_out
        return out
    def post_n2(self, *args, **kwargs):
        out = args[0]
        if(type(self.extra_out) == tuple):
            return (out,) + self.extra_out
        else:
            return (out,) + (self.extra_out,)
    def pre_d(self, *args, **kwargs):
        return args, kwargs
    def post_d(self, *args, **kwargs):
        out = args[0][0]
        return out
    def clear_processor(self):
        if hasattr(self, 'extra_out'):
            delattr(self, 'extra_out')


#two transformers functions
class Wav2Vec2FeatureProjectionProcessor():
    # main forward returns hidden and norm hidden.  we want PAI to just work with hidden
    def post_n1(self, *args, **kwargs):
        hidden_states = args[0][0]
        norm_hidden_states= args[0][1]
        self.norm_hidden_states = norm_hidden_states
        return hidden_states
    
    #This function is called right before passing final value forward, should return everything that gets returned from main module
    def post_n2(self, *args, **kwargs):
        hidden_states = args[0]
        return hidden_states, self.norm_hidden_states
    
    #nothing is done for pre_d just pass it the same values
    def pre_d(self, *args, **kwargs):
        return args, kwargs
        
    #for post processing just ignore the norm hidden states part
    def post_d(self, *args, **kwargs):
        hidden_states = args[0][0]
        return hidden_states
    
    def clear_processor(self):
        if hasattr(self, 'norm_hidden_states'):
            delattr(self, 'norm_hidden_states')
        

#this just wraps the tensor as part 1 of a tuple for some reason??
class Wav2Vec2EncoderLayerProcessor():
    #remove the tuple
    def post_n1(self, *args, **kwargs):
        out = args[0][0]
        return out
    
    #add the tuple back
    def post_n2(self, *args, **kwargs):
        out = args[0]
        return (out,)
    
    #nothing is done for pre_d just pass it the same values
    def pre_d(self, *args, **kwargs):
        return args, kwargs
    
    #remove the tuple
    def post_d(self, *args, **kwargs):
        out = args[0][0]
        return out

#LSTMCellProcessor defined here to use as example of how to setup processing functions.
#Even though this is one class, what really happens is that the main module has one instance, which will use post_n1 and post_n2 and then each new Dendrite node gets a unique separate individual instance to use pre_d and post_d
class LSTMCellProcessor():
    #The neuron does eventually need to return h_t and c__t, but h_t gets modified py the Dendrite
    #nodes first so it needs to be extracted in post_n1, and then gets added back in post_n2
    #post_n1 is called right after the main module is called before any Dendrite processing.  It should return only the part of the output that you want to do Dendrite learning for.  
    def post_n1(self, *args, **kwargs):
        h_t = args[0][0]
        c_t = args[0][1]
        #store the cell state temporarily and just use the hidden state to do Dendrite functions
        self.c_t_n = c_t
        return h_t
    #post_n2 is called right before passing final value forward, should return everything that gets returned from main module
    #h_t at this point has been modified with Dendrite processing
    def post_n2(self, *args, **kwargs):
        h_t = args[0]
        return h_t, self.c_t_n
    #input to pre_d will be (input, (h_t, c_t))
    #pre_d does filtering to make sure Dendrite is getting the right input.  This typically would be done in the training loop.  For example, with an LSTM this is where you check if its the first iteration or not and either pass the Dendrite the regular args to the neuron or pass the Dendrite its own internal state.
    def pre_d(self, *args, **kwargs):
        h_t = args[1][0]
        #if its the initial step then just use the normal input and zeros
        if(h_t.sum() == 0):
            return args, kwargs
        #if its not the first one then return the input it got with its own h_t and c_t to replace parents
        else:
            return (args[0], (self.h_t_d, self.c_t_d)), kwargs
        
    #For post processing post_d just getting passed the output, which is (h_t,c_t). Then it wants to only pass along h_t as the output for the function to be passed to the parent while retaining both h_t and c_t.  post_d saves what needs to be saved for next time and passes forward only the Dendrite part that will be added to the parent
    def post_d(self, *args, **kwargs):
        h_t = args[0][0]
        c_t = args[0][1]
        self.h_t_d = h_t
        self.c_t_d = c_t
        return h_t
    def clear_processor(self):
        if hasattr(self, 'h_t_d'):
            delattr(self, 'h_t_d')
        if hasattr(self, 'c_t_d'):
            delattr(self, 'c_t_d')
        if hasattr(self, 'c_t_n'):
            delattr(self, 'c_t_n')

# Similar to the above but for GRU
class GRUProcessor():
    def post_n1(self, *args, **kwargs):
        output = args[0][0]
        h_t = args[0][1]
        self.h_t = h_t
        return output
    def post_n2(self, *args, **kwargs):
        output = args[0]
        return output, self.h_t
    def pre_d(self, *args, **kwargs):
        if(len(args) == 1 or args[1].sum() == 0):
            return args, kwargs
        else:
            return (args[0], self.h_t_d), kwargs
    def post_d(self, *args, **kwargs):
        output = args[0][0]
        h_t_d = args[0][1]
        self.h_t_d = h_t_d
        return output
    def clear_processor(self):
        if hasattr(self, 'h_t'):
            del self.h_t
        if hasattr(self, 'h_t_d'):
            del self.h_t_d
 
# Similar to the above but for GRU
class GRUCellProcessor():
    def post_n1(self, *args, **kwargs):
        return args[0]
    def post_n2(self, *args, **kwargs):
        return args[0]
    def pre_d(self, *args, **kwargs):
        if(len(args) == 1 or args[1].sum() == 0):
            return args, kwargs
        else:
            return args[0], self.h_t_d
    def post_d(self, *args, **kwargs):
        h_t_d = args[0]
        self.h_t_d = h_t_d
        return h_t_d
    def clear_processor(self):
        if hasattr(self, 'h_t'):
            del self.h_t
        if hasattr(self, 'h_t_d'):
            del self.h_t_d

#This LSTM processor works as above but operates with the final hidden state being passed rather than output
class LSTMProcessorReturnHidden():
    def post_n1(self, *args, **kwargs):
        self.output = args[0][0]
        hidden = args[0][1][0]
        self.cell = args[0][1][1]
        return hidden
    def post_n2(self, *args, **kwargs):
        hidden = args[0]
        return self.output, (hidden, self.cell)
    def pre_d(self, *args, **kwargs):
        hidden = args[1][0]
        if(hidden.sum() == 0):
            return args, kwargs
        else:
            return (args[0], (self.dendrite_hidden, self.dendrite_cell)), {}
        
    def post_d(self, *args, **kwargs):
        output = args[0][0]
        hidden = args[0][1][0]
        cell = args[0][1][1]
        self.dendrite_hidden = hidden
        self.dendrite_cell = cell
        return hidden
    def clear_processor(self):
        if hasattr(self, 'c_t_n'):
            del self.c_t_n
        if hasattr(self, 'h_t_d'):
            del self.h_t_d
        if hasattr(self, 'c_t_d'):
            del self.c_t_d

'''
class GRUProcessor():
    #Post processing does eventually need to return h_t and c__t, but h_t gets modified py the PAI nodes first so it needs to be extracted in post 1, and then gets added back in post 2
    def post_n1(self, *args, **kwargs):
        h_t = args[0][0]
        c_t = args[0][1]
        #store the cell state temporarily and just use the hidden state to do PAI functions
        self.c_t_n = c_t
        return h_t
    def post_n2(self, *args, **kwargs):
        h_t = args[0]
        return h_t, self.c_t_n
    #Pass in an extra argument for if its the first input to use the original val and not the internal val
    def pre_d(self, *args, **kwargs):
        c_t = args[0][0]
        h_t = args[1][0]
        first = args[2]
        if first:
            return args, kwargs
        #if its not the first one then return the input it got with its own c_t to replace parents
        else:
            return (args[0], self.c_t_d,first),{}
    #for post processing its just getting passed the output, which is (h_t,c_t). Then it wants to just pass along h_t as the output for the function to be passed to the parent while retaining both
    def post_d(self, *args, **kwargs):
        h_t = args[0][0]
        c_t = args[0][1]
        self.c_t_d = c_t
        return h_t
'''

class MyBatchNorm1d(nn.BatchNorm1d):
    def __init__(self, num_features, eps=1e-5, momentum=0.1,
                 affine=True, track_running_stats=True):
        super(MyBatchNorm1d, self).__init__(
            num_features, eps, momentum, affine, track_running_stats)

    def forward(self, input):
        self._check_input_dim(input)

        exponential_average_factor = 0.0

        if self.training and self.track_running_stats:
            if self.num_batches_tracked is not None:
                self.num_batches_tracked += 1
                if self.momentum is None:  # use cumulative moving average
                    exponential_average_factor = 1.0 / float(self.num_batches_tracked)
                else:  # use exponential moving average
                    exponential_average_factor = self.momentum

        # calculate running estimates
        if self.training:
            self.mean = input.mean([0])
            # use biased var in train
            self.var = input.var([0], unbiased=False)
            self.n = input.numel() / input.size(1)
            with torch.no_grad():
                self.running_mean = exponential_average_factor * self.mean\
                    + (1 - exponential_average_factor) * self.running_mean
                # update running_var with unbiased var
                self.running_var = exponential_average_factor * self.var * self.n / (self.n - 1)\
                    + (1 - exponential_average_factor) * self.running_var
        else:
            self.mean = self.running_mean
            self.var = self.running_var

        input = (input - self.mean[None, :]) / (torch.sqrt(self.var[None, :] + self.eps))
        if self.affine:
            input = input * self.weight[None, :] + self.bias[None, :]

        return input

    def foward_pai(self, input):
        self._check_input_dim(input)
        temp_mean = self.mean.detach().clone()
        temp_var = self.var.detach().clone()
        temp_weight = self.weight.detach().clone()
        temp_bias = self.bias.detach().clone()
        input = (input - temp_mean[None, :]) / (torch.sqrt(temp_var[None, :] + self.eps))
        if self.affine:
            input = input * temp_weight[None, :] + temp_bias[None, :]

        return input


class SequentialWithExtra(nn.Sequential):
    def forward(self, input, extra):
        for module in self:
            input = module(input, extra)
        return input

'''
class BasicBlockPAI(nn.Module):
    expansion = 1

    ' ' '
    this inits from scratch, but really can just call with a nn one so do that every time
    def __init__(self, in_planes, planes, stride=1, down_sample=None, groups=1,
                 base_width=64, dilation=1, norm_layer=None):
        super(BasicBlockPAI, self).__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        if groups != 1 or base_width != 64:
            raise ValueError('BasicBlockPAI only supports groups=1 and base_width=64')
        if dilation > 1:
            raise NotImplementedError("Dilation > 1 not supported in BasicBlockPAI")
        # Both self.conv1 and self.down_sample layers down_sample the input when stride != 1
        self.relu = nn.ReLU(inplace=True)
        self.down_sample = down_sample
        self.stride = stride

        self.b1 = nn.Sequential(
                resnetPT.conv3x3(in_planes, planes, stride),
                norm_layer(planes)
            )
        self.b2 = SequentialWithExtra(
                resnetPT.conv3x3(planes, planes),
                norm_layer(planes)
            )
    ' ' '
    def __init__(self, other_block):
        super(BasicBlockPAI, self).__init__()
        # Both self.conv1 and self.down_sample layers down_sample the input when stride != 1
        self.relu = other_block.relu
        self.down_sample = other_block.down_sample
        self.stride = other_block.stride

        self.b1 = layerBatch(
                other_block.conv1,
                other_block.bn1
            )
        self.b2 = layerBatchIdentity(
                other_block.conv2,
                other_block.bn2
            )


    def forward(self, x):
        identity = x
        if self.down_sample is not None:
            identity = self.down_sample(x)

        out = self.b1(x)
        out = F.relu(out)

        out = self.b2.forward(out, {'identity':identity})

        out = F.relu(out)

        return out


class BottleneckPAI(nn.Module):
    expansion = 4
    ' ' '
    this inits from scratch, but really can just call with a nn one so do that every time

    def __init__(self, in_planes, planes, stride=1, down_sample=None, groups=1,
                 base_width=64, dilation=1, norm_layer=None):
        super(BottleneckPAI, self).__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        width = int(planes * (base_width / 64.)) * groups
        # Both self.conv2 and self.down_sample layers down_sample the input when stride != 1
        
        self.b1 = nn.Sequential(
            resnetPT.conv3x3(in_planes, width),
            norm_layer(width)
        )
        self.b2 = nn.Sequential(
            resnetPT.conv3x3(width, width, stride, groups, dilation),
            norm_layer(width)
        )
        self.b3 = SequentialWithExtra(
            resnetPT.conv3x3(width, planes * self.expansion),
            norm_layer(planes * self.expansion)
        )

        self.relu = nn.ReLU(inplace=True)
        self.down_sample = down_sample
        self.stride = stride
    ' ' '
    def __init__(self, other_bottleneck):
        super(BottleneckPAI, self).__init__()
        self.b1 = layerBatch(
            other_bottleneck.conv1,
            other_bottleneck.bn1
        )
        self.b2 = layerBatch(
            other_bottleneck.conv2,
            other_bottleneck.bn2
        )
        self.b3 = layerBatchIdentity(
            other_bottleneck.conv3,
            other_bottleneck.bn3
        )

        self.relu = other_bottleneck.relu
        self.down_sample = other_bottleneck.down_sample
        self.stride = other_bottleneck.stride

    def forward(self, x):
        identity = x
        out = self.b1(x)
        out = F.relu(out)

        out = self.b2(out)
        out = F.relu(out)

        if self.down_sample is not None:
            identity = self.down_sample(x)

        out = self.b3.forward(out, {'identity':identity})

        #out += identity
        out = F.relu(out)

        return out
'''

#this just turns layer batch into a sequential thing, hasnt been tested with the basic block and bottle neck thing like this, but with them just being coverted directly now it shouldnt matter
class ResNetPAI(nn.Module):
    def __init__(self, other_res_net):
        super(ResNetPAI, self).__init__()
        
        self._norm_layer = other_res_net._norm_layer

        self.in_planes = other_res_net.in_planes
        self.dilation = other_res_net.dilation
        self.groups = other_res_net.groups
        self.base_width = other_res_net.base_width
        self.b1 = GPA.PAISequential([
             other_res_net.conv1,
             other_res_net.bn1]
        )

        self.relu = other_res_net.relu
        self.max_pool = other_res_net.max_pool
        for i in range(1,5):
            setattr(self, 'layer' + str(i), self._make_layer_pb(getattr(other_res_net,'layer' + str(i)),other_res_net, i))
        self.avg_pool = other_res_net.avg_pool
        self.fc = other_res_net.fc

    #this might not be needed now that the blocks are just being converted
    def _make_layer_pb(self, other_block_set,other_res_net, blockID):

        layers = []
        for i in range(len(other_block_set)):
            if(type(other_block_set[i]) == resnetPT.BasicBlock):
                layers.append((other_block_set[i]))
            elif(type(other_block_set[i]) == resnetPT.Bottleneck):
                layers.append((other_block_set[i]))
            else:
                print('your resnet uses a block type that has not been accounted for.  customization might be required')
                print(type(getattr(other_res_net,'layer' + str(blockID))))
                pdb.set_trace()
        return nn.Sequential(*layers)

    def _forward_impl(self, x):
        # See note [TorchScript super()]
        x = self.b1(x)
        x = F.relu(x)
        x = self.max_pool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avg_pool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x

    def forward(self, x):
        return self._forward_impl(x)


class PAILSTMCell(nn.Module):
    #debugging init
    def __init__(self, input_size, hidden_size, bias = True,
              init_mode = 0,
              weight_ih=[], weight_hh=[], bias_ih=[], bias_hh=[]):
        super(PAILSTMCell, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.x2h = nn.Linear(self.input_size, 4 * self.hidden_size, bias=self.bias)
        self.h2h = nn.Linear(self.hidden_size, 4 * self.hidden_size, bias=self.bias)
        with torch.no_grad():
            fromCell = False
            if(fromCell):
                self.x2h.weight.data.copy_(LSTMCell.x2h.weight.detach().clone())
                self.x2h.bias.data.copy_(LSTMCell.x2h.bias.detach().clone())
                self.h2h.weight.data.copy_(LSTMCell.h2h.weight.detach().clone())
                self.h2h.bias.data.copy_(LSTMCell.h2h.bias.detach().clone())
            elif(init_mode != 0):
                self.x2h.weight.data.copy_(weight_ih.detach().clone())
                self.x2h.bias.data.copy_(bias_ih.detach().clone())
                self.h2h.weight.data.copy_(weight_hh.detach().clone())
                self.h2h.bias.data.copy_(bias_hh.detach().clone())
#### ????? 
        self.ingate = nn.Linear(self.input_size+self.hidden_size, self.hidden_size, bias=self.bias)
        self.forgetgate = nn.Linear(self.input_size+self.hidden_size, self.hidden_size, bias=self.bias)
        self.cellgate = nn.Linear(self.input_size+self.hidden_size, self.hidden_size, bias=self.bias)
        self.outgate = nn.Linear(self.input_size+self.hidden_size, self.hidden_size, bias=self.bias)            
        
        ingate_weights_in, forgetgate_weights_in, cellgate_weights_in, outgate_weights_in = self.x2h.weight.chunk(4, 0)
        ingate_bias_in, forgetgate_bias_in, cellgate_bias_in, outgate_bias_in = self.x2h.bias.chunk(4, 0)
        ingate_weights_h, forgetgate_weights_h, cellgate_weights_h, outgate_weights_h = self.h2h.weight.chunk(4, 0)
        ingate_bias_h, forgetgate_bias_h, cellgate_bias_h, outgate_bias_h = self.h2h.bias.chunk(4, 0)

        self.ingate.weight.data.copy_(torch.cat((ingate_weights_in, ingate_weights_h),1).detach().clone())
        self.ingate.bias.data.copy_(((ingate_bias_in + ingate_bias_h)).detach().clone())
        self.forgetgate.weight.data.copy_(torch.cat((forgetgate_weights_in, forgetgate_weights_h),1).detach().clone())
        self.forgetgate.bias.data.copy_(((forgetgate_bias_in + forgetgate_bias_h)).detach().clone())
        self.cellgate.weight.data.copy_(torch.cat((cellgate_weights_in, cellgate_weights_h),1).detach().clone())
        self.cellgate.bias.data.copy_(((cellgate_bias_in + cellgate_bias_h)).detach().clone())
        self.outgate.weight.data.copy_(torch.cat((outgate_weights_in, outgate_weights_h),1).detach().clone())
        self.outgate.bias.data.copy_(((outgate_bias_in + outgate_bias_h)).detach().clone())

        del self.x2h
        del self.h2h

    def reset_parameters(self):
        std = 1.0 / math.sqrt(self.hidden_size)
        for w in self.parameters():
            w.data.uniform_(-std, std)
    
    def forward(self, x, hidden):
        
        
        
        hx, cx = hidden
                
        ingate = self.ingate((x, hx), {'recurrent':True})
        forgetgate = self.forgetgate((x, hx), {'recurrent':True})
        cellgate = self.cellgate((x, hx), {'recurrent':True})
        outgate = self.outgate((x, hx), {'recurrent':True})
        
        
        ingate = F.sigmoid(ingate)
        forgetgate = F.sigmoid(forgetgate)
        cellgate = F.tanh(cellgate)
        outgate = F.sigmoid(outgate)
        

        cy = torch.mul(cx, forgetgate) +  torch.mul(ingate, cellgate)        

        hy = torch.mul(outgate, F.tanh(cy))
        
        return (hy, cy)




class PAILSTM(nn.Module):
    """Initialize a basic Conv LSTM cell.
    Args:
      shape: int tuple thats the height and width of the hidden states h and c()
      filter_size: int that is the height and width of the filters
      hidden_size: int thats the num of channels of the states, like hidden_size
      
    """
    def __init__(self, input_size, hidden_size,num_layers=1, toCopy=[]):
        super(PAILSTM, self).__init__()
        
        self.input_size=input_size
        self.hidden_size = hidden_size
        self.num_layers=num_layers
        cell_list=[]
        
        
        if(toCopy != []):
            cell_list.append(PAILSTMCell( self.input_size, self.hidden_size, bias=True, init_mode = 1, weight_ih=toCopy.weight_ih_l0, weight_hh=toCopy.weight_hh_l0, bias_ih=toCopy.bias_ih_l0, bias_hh=toCopy.bias_hh_l0
                                  
                                  ))#the first
        #one has a different number of input channels
        else:
            cell_list.append(PAILSTMCell( self.input_size, self.hidden_size, bias=True, init_mode = 0))
            
        for id_cell in range(1,self.num_layers):
            print('not setup for this yet.  if get here just need to also copy the _lX from toCopy with the getparam thing')
            pdb.set_trace()
            
            cell_list.append(PAILSTMCell(self.hidden_size, self.hidden_size))
        self.cell_list=nn.ModuleList(cell_list)      
    
    def forward(self, current_input, hidden_state):
        """
        args:
            hidden_state:list of tuples, one for every layer, each tuple should be hidden_layer_i,c_layer_i
            input is the tensor of shape seq_len,Batch,Chans,H,W
        """
        #current_input=input
        next_hidden=[]#hidden states(h and c)
        seq_len=current_input.size(0)

        
        for id_layer in range(self.num_layers):#loop for every layer

            hidden_c=hidden_state[id_layer]#hidden and c are images with several channels
            all_output = []
            output_inner = []            
            for t in range(seq_len):#loop for every step
                hidden_c=self.cell_list[id_layer](current_input,hidden_c)#cell_list is a list with different conv_lstms 1 for every layer

                output_inner.append(hidden_c)

            next_hidden.append(hidden_c)
            current_input = hidden_c[0]
    
        return next_hidden

class LSTMCell(nn.Module):
    '''
    def __init__(self, input_size, hidden_size, bias=True):
        super(LSTMCell, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.x2h = nn.Linear(input_size, 4 * hidden_size, bias=bias)
        self.h2h = nn.Linear(hidden_size, 4 * hidden_size, bias=bias)
        self.reset_parameters()
    '''
    def __init__(self, input_size, hidden_size, bias=True,
              #LSTMCell,
              weight_ih=[], weight_hh=[], bias_ih=[], bias_hh=[]):
        super(LSTMCell, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.x2h = nn.Linear(self.input_size, 4 * self.hidden_size, bias=self.bias)
        self.h2h = nn.Linear(self.hidden_size, 4 * self.hidden_size, bias=self.bias)
        with torch.no_grad():
            fromCell = False
            if(fromCell):
                self.x2h.weight.data.copy_(LSTMCell.x2h.weight.detach().clone())
                self.x2h.bias.data.copy_(LSTMCell.x2h.bias.detach().clone())
                self.h2h.weight.data.copy_(LSTMCell.h2h.weight.detach().clone())
                self.h2h.bias.data.copy_(LSTMCell.h2h.bias.detach().clone())
            else:
                self.x2h.weight.data.copy_(weight_ih.detach().clone())
                self.x2h.bias.data.copy_(bias_ih.detach().clone())
                self.h2h.weight.data.copy_(weight_hh.detach().clone())
                self.h2h.bias.data.copy_(bias_hh.detach().clone())


    def reset_parameters(self):
        std = 1.0 / math.sqrt(self.hidden_size)
        for w in self.parameters():
            w.data.uniform_(-std, std)
    
    def forward(self, x, hidden):
        hx, cx = hidden
        #x = x.view(-1, x.size(1))
        gates = self.x2h(x) + self.h2h(hx)
        gates = gates.squeeze()
        ingate, forgetgate, cellgate, outgate = gates.chunk(4, 1)
        
        ingate = F.sigmoid(ingate)
        forgetgate = F.sigmoid(forgetgate)
        cellgate = F.tanh(cellgate)
        outgate = F.sigmoid(outgate)
        

        cy = torch.mul(cx, forgetgate) +  torch.mul(ingate, cellgate)        
        hy = torch.mul(outgate, F.tanh(cy))
        
        return (hy, cy)


class LSTM(nn.Module):
    """Initialize a basic Conv LSTM cell.
    Args:
      shape: int tuple thats the height and width of the hidden states h and c()
      filter_size: int that is the height and width of the filters
      hidden_size: int thats the num of channels of the states, like hidden_size
      
    """
    def __init__(self, input_size, hidden_size,num_layers=1, toCopy=[]):
        super(LSTM, self).__init__()
        
        self.input_size=input_size
        self.hidden_size = hidden_size
        self.num_layers=num_layers
        cell_list=[]
        
        cell_list.append(LSTMCell( self.input_size, self.hidden_size, bias=True, weight_ih=toCopy.weight_ih_l0, weight_hh=toCopy.weight_hh_l0, bias_ih=toCopy.bias_ih_l0, bias_hh=toCopy.bias_hh_l0
                                  ))#the first
        #one has a different number of input channels
        
        for id_cell in range(1,self.num_layers):
            print('not setup for this yet.  if get here just need to also copy the _lX from toCopy with the getparam thing')
            pdb.set_trace()
            
            cell_list.append(LSTMCell(self.hidden_size, self.hidden_size))
        self.cell_list=nn.ModuleList(cell_list)      
    
    def forward(self, current_input, hidden_state):
        """
        args:
            hidden_state:list of tuples, one for every layer, each tuple should be hidden_layer_i,c_layer_i
            input is the tensor of shape seq_len,Batch,Chans,H,W
        """
        #current_input=input
        next_hidden=[]#hidden states(h and c)
        seq_len=current_input.size(0)
        
        for id_layer in range(self.num_layers):#loop for every layer
            hidden_c=hidden_state[id_layer]#hidden and c are images with several channels
            all_output = []
            output_inner = []            
            for t in range(seq_len):#loop for every step
                hidden_c=self.cell_list[id_layer](current_input,hidden_c)#cell_list is a list with different conv_lstms 1 for every layer
                output_inner.append(hidden_c)

            next_hidden.append(hidden_c)
            current_input = hidden_c[0]
    
        return next_hidden


def setup_values(net_values, replica_values):
    if(net_values.parallel_buffers_initialized.item() == 0):
        net_values.setup_arrays(replica_values.normal_pass_average_d.shape[0])
        print('setting up values')
        net_values.parallel_buffers_initialized[0] = 1
        net_values.layer_name = net_values.layer_name + 'mainOne'
        
value_tracker_arrays = ['current_parent_d', 'dendrite_outs']

def setup_all_value_tracker_arrays(net, ):
    all_members = net.__dir__()
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submodule_id in range(len(net)):
            #if there is a self pointer ignore it
            if net[submodule_id] is net:
                continue
            if type(net[submodule_id]).__name__ == 'PAINeuronModule':
                for name in value_tracker_arrays:
                    setattr(net[submodule_id].dendrite_module.dendrite_values[0],name,[])

            else:
                setup_all_value_tracker_arrays(net[submodule_id]) 
    else:
        for member in all_members:        
            if getattr(net,member,None) is net:
                continue
            if type(getattr(net,member,None)).__name__ == 'PAINeuronModule':
                for name in value_tracker_arrays:
                    setattr(getattr(net,member,None).dendrite_module.dendrite_values[0],name,[])
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                setup_all_value_tracker_arrays(getattr(net,member))
        


def get_pai_models_and_setup_arrays(net, replica_net, depth):
    #print('calling get params on %s, depth %d' % (type(net).__name__, depth))
    all_members = net.__dir__()
    this_list = []
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submodule_id in range(len(net)):
            #if there is a self pointer ignore it
            if net[submodule_id] is net:
                continue
            if type(net[submodule_id]).__name__ == 'PAINeuronModule':
                if( not replica_net is None):
                    setup_values(net[submodule_id].dendrite_module.dendrite_values[0], replica_net[submodule_id].dendrite_module.dendrite_values[0])
                this_list = this_list + [net[submodule_id]]
            else:
                #print('sub list not one so continuing')
                if not replica_net is None:
                    replica_net_pass = replica_net[submodule_id]
                else:
                    replica_net_pass = None
                this_list = this_list + get_pai_models_and_setup_arrays(net[submodule_id], replica_net_pass, depth + 1)            
    else:
        for member in all_members:        
            #if(type(net).__name__ == 'ConvModule'):
                #pdb.set_trace()
            if getattr(net,member,None) is net:
                continue
            if type(getattr(net,member,None)).__name__ == 'PAINeuronModule':
                if not replica_net is None:
                    setup_values(getattr(net,member).dendrite_module.dendrite_values[0], getattr(replica_net,member).dendrite_module.dendrite_values[0])
                #print('sub is one so converting')
                this_list = this_list + [getattr(net,member)]
                #print(this_list)            
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                if not replica_net is None:
                    replica_net_pass = getattr(replica_net,member)
                else:
                    replica_net_pass = None
                this_list = this_list + get_pai_models_and_setup_arrays(getattr(net,member), replica_net_pass, depth+1)
            #else:
                #print('not calling convert on %s depth %d' % (member, depth))            
            
    #print('finish depth %d' % depth)
    #print(this_list)
    return this_list 


def get_pai_modules(net, replica_net, depth):
    #print('calling get params on %s, depth %d' % (type(net).__name__, depth))
    all_members = net.__dir__()
    this_list = []
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submodule_id in range(len(net)):
            #if there is a self pointer ignore it
            if net[submodule_id] is net:
                continue
            if type(net[submodule_id]).__name__ == 'PAINeuronModule':
                this_list = this_list + [net[submodule_id]]
            else:
                #print('sub list not one so continuing')
                if not replica_net is None:
                    replica_net_pass = replica_net[submodule_id]
                else:
                    replica_net_pass = None
                this_list = this_list + get_pai_models_and_setup_arrays(net[submodule_id], replica_net_pass, depth + 1)            
    else:
        for member in all_members:        
            #if(type(net).__name__ == 'ConvModule'):
                #pdb.set_trace()
            if getattr(net,member,None) is net:
                continue
            if type(getattr(net,member,None)).__name__ == 'PAINeuronModule':
                #print('sub is one so converting')
                this_list = this_list + [getattr(net,member)]
                #print(this_list)            
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                if not replica_net is None:
                    replica_net_pass = getattr(replica_net,member)
                else:
                    replica_net_pass = None
                this_list = this_list + get_pai_models_and_setup_arrays(getattr(net,member), replica_net_pass, depth+1)
            #else:
                #print('not calling convert on %s depth %d' % (member, depth))            
            
    #print('finish depth %d' % depth)
    #print(this_list)
    return this_list 


'''

class PAIDataParallel(nn.DataParallel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gathered = 1
        self.initialized = 0
        self.average_over_time_list_n = ['normal_pass_average_d']
        self.average_list_p = ['top_dendrite_candidate_averages']
        self.average_list_p2 = ['candidate_grad_average_for_scaling', 'main_grad_average_for_scaling', 'initialized']
        GPA.using_pia_data_parallel = True
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.module, name)
    ' ''
    def forward(self, *inputs, **kwargs):
        #if(self.gathered == 0 and self.training == True):
            #print('PAIDataParallel did not call gather and training is true.')
            #import pdb; pdb.set_trace()
        #self.gathered = 0
        if not self.device_ids:
            return self.module(*inputs, **kwargs)
        for t in chain(self.module.parameters(), self.module.buffers()):
            if t.device != self.src_device_obj:
                raise RuntimeError("module must have its parameters and buffers "
                                "on device {} (device_ids[0]) but found one of "
                                "them on device: {}".format(self.src_device_obj, t.device))
        inputs, kwargs = self.scatter(inputs, kwargs, self.device_ids)
        if len(self.device_ids) == 1:
            return self.module(*inputs[0], **kwargs[0])
        self.replicas = self.replicate(self.module, self.device_ids[:len(inputs)])        
        #This is required because it clears the previous ones which are not getting cleared automatically
        #These arrays are the ones that get appended to in forward and cleared in backward
        #the backward seems to clear on the replicas but not on the main module so the new replicas just has them add up.
        for device_id in self.device_ids:
            setup_all_value_tracker_arrays(self.replicas[device_id])
        outputs = self.parallel_apply(self.replicas, inputs, kwargs)
        return self.gather(outputs, self.output_device)
        
    def gather_average(self, var_name, replica_pai_modules, module_pai_modules, module_id):
        ave = self.gather([getattr(replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0],var_name).unsqueeze(0) for x in self.device_ids],getattr(module_pai_modules[module_id].dendrite_module.dendrite_values[0],var_name).device).mean(0)
        setattr(module_pai_modules[module_id].dendrite_module.dendrite_values[0],var_name,ave)

    def gather_average_over_time(self, var_name, replica_pai_modules, module_pai_modules, module_id):
        ave = self.gather([getattr(replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0],var_name).unsqueeze(0) for x in self.device_ids],getattr(module_pai_modules[module_id].dendrite_module.dendrite_values[0],var_name).device).mean(0)
        setattr(module_pai_modules[module_id].dendrite_module.dendrite_values[0],var_name,getattr(module_pai_modules[module_id].dendrite_module.dendrite_values[0],var_name)*0.99)
        setattr(module_pai_modules[module_id].dendrite_module.dendrite_values[0],var_name,getattr(module_pai_modules[module_id].dendrite_module.dendrite_values[0],var_name)+ 0.01*ave)
    
    def initialize_arrays(self):
        if(self.initialized == 0):
            for device_id in self.device_ids:
                get_pai_models_and_setup_arrays(self.replicas[device_id],None, 0)
            module_pai_modules = get_pai_models_and_setup_arrays(self.module,self.replicas[0], 0) 
            self.initialized = 1  
            
    # is the only reason for this being complicated because module dont know the neuron dimensions?
    # I could test that by calling set dimensions manually for both layers and seeing if it works.
    # if that does work then maybe get rid of this and just use regular data parallel
    #but make it so that a dry run is required without dataparallel that saves the settings and then the only thing PAIDataParallel does is load from those settings and initialize all the models during the init function.
    # of there is not a PAI dat parallel at all and you just have to call init Data parallel function from TPA that loads the file instead.
    
    def gather_data(self):
        self.gathered += 1
        if len(self.device_ids) == 1:
            return
        replica_pai_modules = []
        for device_id in self.device_ids:
            replica_pai_modules.append(get_pai_modules(self.replicas[device_id],None, 0))
        module_pai_modules = get_pai_modules(self.module,self.replicas[0], 0) 
        #print('also think i need to change all of these sums to mean now that its doing arbitrary input sizes')  not sure if this will work when things are of multiple sizes
        if(len(module_pai_modules) == 0):
            print('didn\'t see any pb modules this means something is named wrong')
            pdb.set_trace()
        for module_id in range(len(module_pai_modules)):
            newD1 = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].current_d_sum.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_average_d.device).mean(0)
            module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_average_d *= 0.99
            module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_average_d += newD1 * 0.01

            #putting 4 in the middle of these because this needs to be looked at if adding a enw one whether it needs to be of this form or the form of the other 3 with a different sum/average/tracking method
            if(GPA.doing_thing):
                newD4 = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].normal_pass_max_mean_act.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_max_mean_act.device).max()
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_max_mean_act *= 0.99
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_max_mean_act += newD4 * 0.01
                
            if(GPA.pai_tracker.member_vars['mode'] == 'p'):
                #when getting here go through every value from the 'p' section and make sure it makes sense.  the other section passes unit testing, this one wont
                #values that are summed, or booleans that only one needs to be true
                #WHEN ADDING A NEW THING HERE BE SURE TO CHECK IF IT IS BY BATCH IN WHICH CASE CAN SET TO EQUAL OR BY EPOCH IN WHICH CASE MUST BE TORCH.GE
    
                for var_name in self.average_list_p:
                    self.gather_average(var_name, replica_pai_modules, module_pai_modules, module_id)
                
                prevAve = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average.device).mean(0)
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average = prevAve
                current_correlations = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].current_correlations_for_parallel.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].current_correlations_for_parallel.device).sum(0)
                cor = current_correlations - (prevAve * module_pai_modules[module_id].dendrite_module.dendrite_values[0].parents_average_d_vector)

                module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation *= 0.99
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation += cor * 0.01
                #print('next prev')
                #print(module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation)

                temp_abs = module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation.detach().abs()
                
                #best score is the max score of the previous best score and the current recently averaged correlation
                
                [module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score, temp_best_indices] =  torch.max(torch.cat((module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score.unsqueeze(0),temp_abs.unsqueeze(0)), 0),0)
                                
                
                #if that best score has improved enough or this is the very first iteration
                if((
                    (
                    (module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score*(1.0-GPA.pai_improvement_threshold))-module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score).max()>0.00000001 and (module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score - module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score).max() > GPA.improvement_threshold_raw)  or module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item() == 0):

                    # say that best score did improve this epoch and time step
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score_improved_this_epoch[0] = 1
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score_improved_this_time_step[0] = 1
                    #set the indexes of the best candidate
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].indexes_of_best = temp_best_indices
                    
                    ##check where temp_abs = best score and save the weights for those candidates in forward for the layer next iteration
                        #this is where that saveBest function was maybe called?
                    [values,indexes] = torch.max(module_pai_modules[module_id].dendrite_module.dendrite_values[0].indexes_of_best,0)
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].nodes_best_improved_this_epoch = (module_pai_modules[module_id].dendrite_module.dendrite_values[0].nodes_best_improved_this_epoch + module_pai_modules[module_id].dendrite_module.dendrite_values[0].indexes_of_best)
                    #only replace the ones that are bigger                            
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score = torch.max(module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score, module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score).detach()
                    
                else:
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score_improved_this_time_step[0] = 0
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].indexes_of_best *= 0
                
                #current correlations is the sum of what was found on both
                               
                # if its in the initialization phase
                if(module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item() < GPA.initial_correlation_batches):
                    #calculate cor2 based on the new prev_dendrite_candidate_average

                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average *= module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item()                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average += module_pai_modules[module_id].dendrite_module.dendrite_values[0].top_dendrite_candidate_averages
                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average /= module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item() + 1.0

                    cor2 = current_correlations - (module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average * module_pai_modules[module_id].dendrite_module.dendrite_values[0].parents_average_d_vector)
                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation *= module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item()                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation += cor2
                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation /= module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item() + 1.0
                    
                    #print('init update prev')
                    #print(module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation)
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score = module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score.detach() * 0
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score = module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score.detach() * 0                
               
                for var_name in self.average_list_p2:
                    self.gather_average(var_name, replica_pai_modules, module_pai_modules, module_id)
    ' ''
                
class PAIDistributedDataParallel(nn.parallel.DistributedDataParallel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gathered = 1
        GPA.using_pia_data_parallel = True
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.module, name)
    def forward(self, *inputs, **kwargs):
        if(self.gathered == 0 and self.training == True):
            print('PAIDistributedDataParallel did not call gather and training is true.')
            import pdb; pdb.set_trace()
        self.gathered = 0
        if not self.device_ids:
            return self.module(*inputs, **kwargs)

        for t in chain(self.module.parameters(), self.module.buffers()):
            if t.device != self.src_device_obj:
                raise RuntimeError("module must have its parameters and buffers "
                                   "on device {} (device_ids[0]) but found one of "
                                   "them on device: {}".format(self.src_device_obj, t.device))

        inputs, kwargs = self.scatter(inputs, kwargs, self.device_ids)
        if len(self.device_ids) == 1:
            return self.module(*inputs[0], **kwargs[0])
        self.replicas = self.replicate(self.module, self.device_ids[:len(inputs)])        
        for device_id in self.device_ids:           
            setup_all_value_tracker_arrays(self.replicas[device_id])
        outputs = self.parallel_apply(self.replicas, inputs, kwargs)
        return self.gather(outputs, self.output_device)
    
    #if this starts to work end goal is to have it not called by net() but called by GF.pai_tracker
        #also need to update the readme with whatever ends up happening
    def gather_data(self):
        self.gathered += 1
        if len(self.device_ids) == 1:
            return
        replica_pai_modules = []
        for device_id in self.device_ids:
            replica_pai_modules.append(get_pai_models_and_setup_arrays(self.replicas[device_id],None, 0))
        module_pai_modules = get_pai_models_and_setup_arrays(self.module,self.replicas[0], 0) 
        #print('also think i need to change all of these sums to mean now that its doing arbitrary input sizes')  not sure if this will work when things are of multiple sizes
        if(len(module_pai_modules) == 0):
            print('didn\'t see any pb modules this means something is named wrong')
            pdb.set_trace()
        for module_id in range(len(module_pai_modules)):
            newD1 = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].current_d_sum.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_average_d.device).mean(0)
            module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_average_d *= 0.99
            module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_average_d += newD1 * 0.01

            if(GPA.doing_thing):
                newD4 = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].normal_pass_max_mean_act.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_max_mean_act.device).max()
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_max_mean_act *= 0.99
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].normal_pass_max_mean_act += newD4 * 0.01

            if(GPA.pai_tracker.member_vars['mode'] == 'p'):
                topAve = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].top_dendrite_candidate_averages.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].top_dendrite_candidate_averages.device).mean(0)
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].top_dendrite_candidate_averages = topAve
                
                prevAve = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average.device).mean(0)
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average = prevAve

                current_correlations = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].current_correlations_for_parallel.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].current_correlations_for_parallel.device).sum(0)

                cor = current_correlations - (prevAve * module_pai_modules[module_id].dendrite_module.dendrite_values[0].parents_average_d_vector)
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation *= 0.99
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation += cor * 0.01
                temp_abs = module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation.detach().abs()
                [module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score, temp_best_indices] =  torch.max(torch.cat((module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score.unsqueeze(0),temp_abs.unsqueeze(0)), 0),0)
                if((
                    (
                    (module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score*(1.0-GPA.pai_improvement_threshold))-module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score).max()>0.00000001 and (module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score - module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score).max() > GPA.improvement_threshold_raw)  or module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item() == 0):
                    # say that best score did improve this epoch and time step
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score_improved_this_epoch[0] = 1
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score_improved_this_time_step[0] = 1
                    #set the indexes of the best candidate
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].indexes_of_best = temp_best_indices
                    
                    ##check where temp_abs = best score and save the weights for those candidates in forward for the layer next iteration
                        #this is where that saveBest function was maybe called?
                    [values,indexes] = torch.max(module_pai_modules[module_id].dendrite_module.dendrite_values[0].indexes_of_best,0)
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].nodes_best_improved_this_epoch = (module_pai_modules[module_id].dendrite_module.dendrite_values[0].nodes_best_improved_this_epoch + module_pai_modules[module_id].dendrite_module.dendrite_values[0].indexes_of_best)
                    #only replace the ones that are bigger                            
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score = torch.max(module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score, module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score).detach()

                else:
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score_improved_this_time_step[0] = 0
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].indexes_of_best *= 0

                #current correlations is the sum of what was found on both
                # if its in the initialization phase
                if(module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item() < GPA.initial_correlation_batches):
                    #calculate cor2 based on the new prev_dendrite_candidate_average

                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average *= module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item()                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average += module_pai_modules[module_id].dendrite_module.dendrite_values[0].top_dendrite_candidate_averages
                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average /= module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item() + 1.0

                    cor2 = current_correlations - (module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_average * module_pai_modules[module_id].dendrite_module.dendrite_values[0].parents_average_d_vector)
                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation *= module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item()                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation += cor2
                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation /= module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.item() + 1.0
                    
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score = module_pai_modules[module_id].dendrite_module.dendrite_values[0].best_score.detach() * 0
                    module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score = module_pai_modules[module_id].dendrite_module.dendrite_values[0].previous_best_score.detach() * 0

                ave3 = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].candidate_grad_average_for_scaling.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].candidate_grad_average_for_scaling.device).mean(0)
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].candidate_grad_average_for_scaling = ave3
                ave3 = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].main_grad_average_for_scaling.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].main_grad_average_for_scaling.device).mean(0)
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].main_grad_average_for_scaling = ave3
                
                #initialzied actually does matter for scoring.  should make sure that this next 
                initialized = self.gather([replica_pai_modules[x][module_id].dendrite_module.dendrite_values[0].initialized.unsqueeze(0) for x in self.device_ids],module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized.device).mean(0)
                module_pai_modules[module_id].dendrite_module.dendrite_values[0].initialized[0] = initialized
'''



