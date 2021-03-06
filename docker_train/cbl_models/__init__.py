
from copy import deepcopy
import math
import torch.nn as nn

from .efficientnet_refactor import EfficientNet
from .efficientnet_lite import EfficientNetLite
from .resnet_base import ResNet
#  from .resnet import (ResNet, SEResNet, ASKCResNet,
#          WAResNet, FReLUResNet, DYConvResNet, IBNResNetA, IBNResNetB,
#          IBNResNetDenseCLA, IBNResNetDenseCLB)
from .pa_resnet import PAResNet, SE_PAResNet
from .ushape_effnet import UShapeEffNetB0ClassificationWrapper
from .xception_v2 import Xception41, Xception65, Xception71
from .spinenet import SpineNetClassificationWrapper, SpineNet
from .bisenetv2 import BiSeNetV2TrainWrapper, BiSeNetV2TrainWrapperDenseCL
from .repvgg import RepVGG

# also import backbones
#  from .resnet import ResNetBackbone, IBNResNetBackboneA, IBNResNetBackboneB
from .resnet_base import ResNetBackbone
from .xception_v2 import XceptionBackbone
from .repvgg import RepVGGBackBone

from .timm_model import TIMM


def build_model(model_args):
    model_type = model_args['model_type']
    model_args_ = deepcopy(model_args)
    model_args_.pop('model_type')
    model = eval(model_type)(**model_args_)
    init_model_weights(model)
    return model


#  def build_model(model_type, n_classes):
#  def build_model(model_args):
#      model_type, n_classes = model_args['model_type'], model_args['n_classes']
#      if model_type.startswith('effcientnet'):
#          mtype = model_type.split('-')[1]
#          model = EfficientNet(mtype, n_classes)
#
#      elif model_type.startswith('lite-effcientnet'):
#          mtype = model_type.split('-')[-1]
#          model = EfficientNetLite(mtype, n_classes)
#
#      elif model_type.startswith('spinenet'):
#          mtype = model_type.split('-')[-1]
#          model = SpineNetClassificationWrapper(mtype, n_classes)
#
#      elif model_type == 'ushape-effnet-b0':
#          model = UShapeEffNetB0ClassificationWrapper(n_classes)
#
#      elif model_type.startswith('xception'):
#          mtype = model_type.split('-')[-1]
#          model = Xception(n_layers=mtype, n_classes=n_classes)
#
#      elif model_type == 'resnet-50':
#          model = ResNet(n_classes=n_classes)
#      elif model_type == 'resnet-101':
#          model = ResNet(n_layers=101, n_classes=n_classes)
#
#      elif model_type == 'pa_resnet-50':
#          model = PAResNet(n_classes=n_classes)
#      elif model_type == 'pa_resnet-101':
#          model = PAResNet(n_layers=101, n_classes=n_classes)
#
#      elif model_type.startswith('se_resnet'):
#          n_layers = int(model_type.split('-')[1])
#          model = SEResNet(n_layers=n_layers, n_classes=n_classes)
#
#      elif model_type == 'wa_resnet-50':
#          model = WAResNet(n_classes=n_classes)
#      elif model_type == 'wa_resnet-101':
#          model = WAResNet(n_layers=101, n_classes=n_classes)
#
#      elif model_type == 'ibn_a_resnet-50':
#          model = IBNResNetA(n_classes=n_classes)
#      elif model_type == 'ibn_a_resnet-101':
#          model = IBNResNetA(n_layers=101, n_classes=n_classes)
#      elif model_type == 'ibn_b_resnet-50':
#          model = IBNResNetB(n_classes=n_classes)
#      elif model_type == 'ibn_b_resnet-101':
#          model = IBNResNetB(n_layers=101, n_classes=n_classes)
#      elif model_type == 'ibn_a_resnet_densecl-101':
#          model = IBNResNetDenseCLA(n_layers=101, n_classes=n_classes)
#      elif model_type == 'ibn_b_resnet_densecl-101':
#          model = IBNResNetDenseCLB(n_layers=101, n_classes=n_classes)
#
#      elif model_type.startswith('frelu_resnet'):
#          n_layers = int(model_type.split('-')[1])
#          model = FReLUResNet(n_layers=n_layers, n_classes=n_classes)
#
#      elif model_type == 'se_pa_resnet-50':
#          model = SE_PAResNet(n_classes=n_classes)
#      elif model_type == 'se_pa_resnet-101':
#          model = SE_PAResNet(n_layers=101, n_classes=n_classes)
#
#      elif model_type == 'askc-resnet-50':
#          model = ASKCResNet(n_classes=n_classes)
#      elif model_type == 'askc-resnet-101':
#          model = ASKCResNet(n_layers=101, n_classes=n_classes)
#
#      elif model_type == 'dyconv_resnet-50':
#          model = DYConvResNet(n_classes=n_classes)
#
#      elif model_type == 'bisenetv2':
#          model = BiSeNetV2TrainWrapper(n_classes=n_classes)
#
#      init_model_weights(model)
#
#      return model


def init_model_weights(model):
    #  if isinstance(model, (WAResNet, )): return
    if hasattr(model, 'conv_type') and model.conv_type == 'wa': return
    for name, module in model.named_modules():
        if isinstance(module, nn.Conv2d):
            fan_out = module.kernel_size[0] * module.kernel_size[1] * module.out_channels
            module.weight.data.normal_(0, math.sqrt(2.0 / fan_out))
            #  nn.init.kaiming_normal_(module.weight, mode='fan_out')
            if not module.bias is None: nn.init.constant_(module.bias, 0)
        elif isinstance(module, nn.modules.batchnorm._BatchNorm):
            if hasattr(module, 'last_bn') and module.last_bn:
                nn.init.zeros_(module.weight)
            else:
                nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Linear):
            fan_out = module.weight.size(0)  # fan-out
            fan_in = 0
            init_range = 1.0 / math.sqrt(fan_in + fan_out)
            #  module.weight.data.uniform_(-init_range, init_range)
            module.weight.data.normal_(mean=0.0, std=0.01)
            #  nn.init.xavier_uniform_(module.weight)
            nn.init.constant_(module.bias, 0)
