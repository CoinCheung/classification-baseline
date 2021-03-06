# Copyright (c) 2019, Adobe Inc. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike
# 4.0 International Public License. To view a copy of this license, visit
# https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.

import numpy as np
import torch
import torch.nn.parallel
import torch.nn as nn
import torch.nn.functional as F


class BlurPool(nn.Module):

    def __init__(self, channels, pad_type='reflect', filt_size=4, stride=2, pad_off=0):
        super(BlurPool, self).__init__()
        self.filt_size = filt_size
        self.pad_off = pad_off
        self.pad_sizes = [int(1.*(filt_size-1)/2), int(np.ceil(1.*(filt_size-1)/2)), int(1.*(filt_size-1)/2), int(np.ceil(1.*(filt_size-1)/2))]
        self.pad_sizes = [pad_size+pad_off for pad_size in self.pad_sizes]
        self.stride = stride
        self.off = int((self.stride-1)/2.)
        self.channels = channels

        if(self.filt_size==1):
            filt = torch.tensor([1.,])
        elif(self.filt_size==2):
            filt = torch.tensor([1., 1.])
        elif(self.filt_size==3):
            filt = torch.tensor([1., 2., 1.])
        elif(self.filt_size==4):
            filt = torch.tensor([1., 3., 3., 1.])
        elif(self.filt_size==5):
            filt = torch.tensor([1., 4., 6., 4., 1.])
        elif(self.filt_size==6):
            filt = torch.tensor([1., 5., 10., 10., 5., 1.])
        elif(self.filt_size==7):
            filt = torch.tensor([1., 6., 15., 20., 15., 6., 1.])

        # fix padding to 5
        #  self.padding = 2
        #  filt = torch.tensor([1., 4., 6., 4., 1.])
        # fix padding to 3
        self.padding = 1
        filt = torch.tensor([1., 2., 1.])

        filt = torch.einsum('ik,kj->ij', filt[:,None], filt[None,:])
        filt = filt / torch.sum(filt)
        filt = filt[None,None,:,:].repeat((self.channels,1,1,1)).detach()
        filt.requires_grad_(False)

        self.register_buffer('filt', filt)


    def forward(self, inp):
        if(self.filt_size==1):
            if(self.pad_off==0):
                return inp[:,:,::self.stride,::self.stride]
            else:
                return self.pad(inp)[:,:,::self.stride,::self.stride]
        else:
            return F.conv2d(inp, self.filt, stride=self.stride, groups=self.channels, padding=self.padding)


#  class BlurPool(nn.Module):
#
#      def __init__(self, channels, pad_type='reflect', filt_size=4, stride=2, pad_off=0):
#          super(BlurPool, self).__init__()
#          self.filt_size = filt_size
#          self.pad_off = pad_off
#          self.pad_sizes = [int(1.*(filt_size-1)/2), int(np.ceil(1.*(filt_size-1)/2)), int(1.*(filt_size-1)/2), int(np.ceil(1.*(filt_size-1)/2))]
#          self.pad_sizes = [pad_size+pad_off for pad_size in self.pad_sizes]
#          self.stride = stride
#          self.off = int((self.stride-1)/2.)
#          self.channels = channels
#
#          if(self.filt_size==1):
#              filt = torch.tensor([1.,])
#          elif(self.filt_size==2):
#              filt = torch.tensor([1., 1.])
#          elif(self.filt_size==3):
#              filt = torch.tensor([1., 2., 1.])
#          elif(self.filt_size==4):
#              filt = torch.tensor([1., 3., 3., 1.])
#          elif(self.filt_size==5):
#              filt = torch.tensor([1., 4., 6., 4., 1.])
#          elif(self.filt_size==6):
#              filt = torch.tensor([1., 5., 10., 10., 5., 1.])
#          elif(self.filt_size==7):
#              filt = torch.tensor([1., 6., 15., 20., 15., 6., 1.])
#
#          filt = torch.einsum('ik,kj->ij', filt[:,None], filt[None,:])
#          filt = filt / torch.sum(filt)
#          filt = filt[None,None,:,:].repeat((self.channels,1,1,1)).detach()
#          filt.requires_grad_(False)
#
#          self.register_buffer('filt', filt)
#
#          self.pad = get_pad_layer(pad_type)(self.pad_sizes)
#
#      def forward(self, inp):
#          if(self.filt_size==1):
#              if(self.pad_off==0):
#                  return inp[:,:,::self.stride,::self.stride]
#              else:
#                  return self.pad(inp)[:,:,::self.stride,::self.stride]
#          else:
#              return F.conv2d(self.pad(inp), self.filt, stride=self.stride, groups=inp.shape[1])

def get_pad_layer(pad_type):
    if(pad_type in ['refl','reflect']):
        PadLayer = nn.ReflectionPad2d
    elif(pad_type in ['repl','replicate']):
        PadLayer = nn.ReplicationPad2d
    elif(pad_type=='zero'):
        PadLayer = nn.ZeroPad2d
    else:
        print('Pad type [%s] not recognized'%pad_type)
    return PadLayer

class BlurPool1D(nn.Module):
    def __init__(self, channels, pad_type='reflect', filt_size=3, stride=2, pad_off=0):
        super(BlurPool1D, self).__init__()
        self.filt_size = filt_size
        self.pad_off = pad_off
        self.pad_sizes = [int(1. * (filt_size - 1) / 2), int(np.ceil(1. * (filt_size - 1) / 2))]
        self.pad_sizes = [pad_size + pad_off for pad_size in self.pad_sizes]
        self.stride = stride
        self.off = int((self.stride - 1) / 2.)
        self.channels = channels

        # print('Filter size [%i]' % filt_size)
        if(self.filt_size == 1):
            filt = torch.tensor([1., ])
        elif(self.filt_size == 2):
            filt = torch.tensor([1., 1.])
        elif(self.filt_size == 3):
            filt = torch.tensor([1., 2., 1.])
        elif(self.filt_size == 4):
            filt = torch.tensor([1., 3., 3., 1.])
        elif(self.filt_size == 5):
            filt = torch.tensor([1., 4., 6., 4., 1.])
        elif(self.filt_size == 6):
            filt = torch.tensor([1., 5., 10., 10., 5., 1.])
        elif(self.filt_size == 7):
            filt = torch.tensor([1., 6., 15., 20., 15., 6., 1.])

        filt = filt / torch.sum(filt)
        self.register_buffer('filt', filt[None, None, :].repeat((self.channels, 1, 1)))

        self.pad = get_pad_layer_1d(pad_type)(self.pad_sizes)

    def forward(self, inp):
        if(self.filt_size == 1):
            if(self.pad_off == 0):
                return inp[:, :, ::self.stride]
            else:
                return self.pad(inp)[:, :, ::self.stride]
        else:
            return F.conv1d(self.pad(inp), self.filt, stride=self.stride, groups=inp.shape[1])

def get_pad_layer_1d(pad_type):
    if(pad_type in ['refl', 'reflect']):
        PadLayer = nn.ReflectionPad1d
    elif(pad_type in ['repl', 'replicate']):
        PadLayer = nn.ReplicationPad1d
    elif(pad_type == 'zero'):
        PadLayer = nn.ZeroPad1d
    else:
        print('Pad type [%s] not recognized' % pad_type)
    return PadLayer
