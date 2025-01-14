import numpy as np
import os
import torch

# model_as_text = torch.cuda.device_count()
# print(model_as_text)
#
# b = torch.cuda.get_device_name(0)
# print(b)
#
# c = torch.cuda.get_device_name(1)
# print(c)
#
# d = torch.cuda.get_device_name(2)
# print(d)


import torch
import torch.nn as nn
from utils import count_params, import_class
import argparse
import shutil
import yaml


def get_parser():
    # parameter priority: command line > config > default
    parser = argparse.ArgumentParser(
        description='Sematic ShiftGraph Convolution Network')
    parser.add_argument(
        '--work-dir',
        default='./work_dir/temp',
        help='the work folder for storing results')

    parser.add_argument('-model_saved_name', default='')
    parser.add_argument(
        '--config',
        default='./config/calo/test_lower_middle.yaml',
        help='path to the configuration file')

    # processor
    parser.add_argument(
        '--phase', default='train', help='must be train or test')


    # visulize and debug
    parser.add_argument(
        '--seed', type=int, default=1, help='random seed for pytorch')
    parser.add_argument(
        '--log-interval',
        type=int,
        default=100,
        help='the interval for printing messages (#iteration)')
    parser.add_argument(
        '--save-interval',
        type=int,
        default=2,
        help='the interval for storing models (#iteration)')
    parser.add_argument(
        '--eval-interval',
        type=int,
        default=5,
        help='the interval for evaluating models (#iteration)')

    parser.add_argument(
        '--show-topk',
        type=int,
        default=[1, 5],
        nargs='+',
        help='which Top K accuracy will be shown')

    # feeder
    parser.add_argument(
        '--feeder', default='feeder.feeder', help='data loader will be used')
    parser.add_argument(
        '--num-worker',
        type=int,
        default=8,
        help='the number of worker for data loader')
    parser.add_argument(
        '--train-feeder-args',
        default=dict(),
        help='the arguments of data loader for training')
    parser.add_argument(
        '--test-feeder-args',
        default=dict(),
        help='the arguments of data loader for test')

    # model
    parser.add_argument('--model', default=None, help='the model will be used')
    parser.add_argument(
        '--model-args',
        type=dict,
        default=dict(),
        help='the arguments of model')
    parser.add_argument(
        '--weights',
        default=None,
        help='the weights for network initialization')
    parser.add_argument(
        '--ignore-weights',
        type=str,
        default=[],
        nargs='+',
        help='the name of weights which will be ignored in the initialization')

    # optim
    parser.add_argument(
        '--base-lr', type=float, default=0.01, help='initial learning rate')
    parser.add_argument(
        '--step',
        type=int,
        default=[20, 40, 60],
        nargs='+',
        help='the epoch where optimizer reduce the learning rate')
    parser.add_argument(
        '--device',
        type=int,
        default=0,
        nargs='+',
        help='the indexes of GPUs for training or testing')
    parser.add_argument('--optimizer', default='SGD', help='type of optimizer')
    parser.add_argument(
        '--nesterov', default=False, help='use nesterov or not')
    parser.add_argument(
        '--batch-size', type=int, default=256, help='training batch size')
    parser.add_argument(
        '--test-batch-size', type=int, default=256, help='test batch size')
    parser.add_argument(
        '--start-epoch',
        type=int,
        default=0,
        help='start training from which epoch')
    parser.add_argument(
        '--num-epoch',
        type=int,
        default=80,
        help='stop training in which epoch')
    parser.add_argument(
        '--weight-decay',
        type=float,
        default=0.0005,
        help='weight decay for optimizer')
    parser.add_argument(
        '--seg',
        type=int,
        default=1,
        help='segment')
    parser.add_argument(
        '--metric',
        type=str,
        default='upper',
        help='upper or lower semantic space')
    parser.add_argument(
        '--graph',
        type=str,
        default='calo',
        help='adjacency matrix graph for specific dataset'
    )
    parser.add_argument(
        '--monitor',
        type=str,
        default='acc_val',
        help='monitor validation accuracy'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        default='ntu',
        help='selection dataset'
    )
    parser.add_argument(
        '--case',
        type=int,
        default=0,
        help='cross subject / cross view'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=0,
        help='workers number for dataloader'
    )
    parser.add_argument(
        '--train',
        type=int,
        default=1,
        help='train or test phase'
    )
    parser.add_argument(
        '--save_score',
        type=bool,
        default=True,
        help='save test score'
    )
    parser.add_argument(
        '--save_model',
        type=bool,
        default=True,
        help='save model'
    )

    parser.add_argument(
        '--assume-yes',
        action='store_true',
        help='Say yes to every prompt')
    parser.add_argument(
        '--forward-batch-size',
        type=int,
        default=1,
        help='Batch size during forward pass, must be factor of --batch-size')
    parser.add_argument(
        '--checkpoint',
        type=str,
        help='path of previously saved training checkpoint')

    parser.add_argument('--only_train_part', default=False)
    parser.add_argument('--only_train_epoch', default=0)
    parser.add_argument('--warm_up_epoch', default=0)
    return parser

def load_model(arg):
    output_device = arg.device[0] if type(arg.device) is list else arg.device
    #output_device = 0
    Model = import_class(arg.model)
    model = Model(**arg.model_args).cuda(output_device)
    loss = nn.CrossEntropyLoss().cuda(output_device)

    #device_ids = [0, 1]

    if type(arg.device) is list:
        if len(arg.device) > 1:
            model = nn.DataParallel(model, device_ids=arg.device, output_device=output_device)
            print("here")


if __name__ == '__main__':
    parser = get_parser()
    p = parser.parse_args()
    if p.config is not None:
        with open(p.config, 'r') as f:
            default_arg = yaml.safe_load(f)
        key = vars(p).keys()
        for k in default_arg.keys():
            if k not in key:
                print('WRONG ARG: {}'.format(k))
                assert (k in key)
        parser.set_defaults(**default_arg)

    args = parser.parse_args()
    load_model(args)


print("s")