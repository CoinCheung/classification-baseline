
n_gpus = 8
batchsize = 128
n_epoches = 350
n_eval_epoch = 1
lr = 1.6e-2 * (batchsize / 256) * n_gpus
weight_decay = 1e-5
opt_wd = 1e-5
momentum = 0.9
warmup = 'linear'
warmup_ratio = 0
datapth = './imagenet/'
model_type = 'b1'
n_classes = 1000
cropsize = 240
num_workers = 4
ema_alpha = 0.9999
fp16_level = 'O1'
use_sync_bn = False
nesterov = True