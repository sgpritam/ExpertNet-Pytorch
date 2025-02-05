#!/usr/bin/env python
# coding: utf-8

import torch
torch.backends.cudnn.benchmark=True

import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import torch.nn.functional as F

import torchvision.datasets as datasets
import torchvision.models as models
import torchvision.transforms as transforms

import argparse 
import numpy as np
from random import shuffle

import copy
from autoencoder import *

import sys
sys.path.append(os.path.join(os.getcwd(), 'utils'))

from encoder_train import *
from encoder_utils import *

from model_train import *
from model_utils import *

parser = argparse.ArgumentParser(description='Test file')
parser.add_argument('--task_number', default=1, type=int, help='Select the task you want to test out the architecture; choose from 1-4')
parser.add_argument('--use_gpu', default=False, type=bool, help = 'Set the flag if you wish to use the GPU')

args = parser.parse_args()
task_number = args.task_number
use_gpu = args.use_gpu


if (task_number < 1 or task_number > 4):
	print ("Come on man, 1-4 only")
	sys.exit()


data_transforms = {
		'train': transforms.Compose([
			transforms.Resize(256),
			transforms.CenterCrop(224),
			transforms.ToTensor(),
			transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
		]),
		'test': transforms.Compose([
			transforms.Resize(256),
			transforms.CenterCrop(224),
			transforms.ToTensor(),
			transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
		])
	}


data_path = os.path.join(os.getcwd(), "Data")

encoder_path = os.path.join(os.getcwd(), "models", "autoencoders")

model_path = os.path.join(os.getcwd(), "models", "trained_models")

path_task = os.path.join(data_path, "Task_" + str(task_number))

image_folder = datasets.ImageFolder(os.path.join(path_task, 'test'), transform = data_transforms['test'])

dset_size = len(image_folder)

device = torch.device("cuda:0" if use_gpu else "cpu")

dset_loaders = torch.utils.data.DataLoader(image_folder, batch_size = batch_size,
												shuffle=True, num_workers=4)

device = torch.device("cuda:0" if use_gpu else "cpu")

best_loss = 99999999999
model_number = 0

#Load autoencoder models
for ae_number in range(1, 5):
	ae_path = os.path.join(encoder_path, "autoencoder_" + str(ae_number))
	
	#Load a trained autoencoder model
	model = Autoencoder()
	model.load_state_dict(torch.load(os.path.join(ae_path, 'best_performing_model.pth')))

	running_loss = 0

	#Test out the different auto encoder models and check their reconstruction error
	for data in dset_loaders:
		input_data, labels = data
		del labels
		del data

		if (use_gpu):
			input_data = input_data.to(device)
			 
		else:
			input_data  = Variable(input_data)

		model.to(device)

		preds = model(input_data)
		loss = encoder_criterion(preds, input_data)
		
		del preds
		del input_data
		
		running_loss = running_loss + loss.item()

	model_loss = running_loss/dset_size

	if(model_loss < best_loss):
		best_loss = model_loss
		model_number = ae_number
	
	del model

trained_model_path = os.path.join(model_path, "model_" + model_number)

file_name = os.path.join(trained_model_path, "classes.txt") 
file_object = open(file_name, 'r')

num_of_classes = file_object.read()
file_object.close()

num_of_classes = int(num_of_classes_old)

model = GeneralModelClass(num_of_classes)
model.load_state_dict(torch.load(os.path.join(trained_model_path, 'best_performing_model.pth')))

running_loss = 0

for data in dset_loaders:
	input_data, labels = data
	del data

	if (use_gpu):
		input_data = Variable(input_data.to(device))
		labels = Variable(labels.to(device)) 
	
	else:
		input_data  = Variable(input_data)
		labels = Variable(labels)
	
	model.to(device)

	preds = model(input_data)
	loss = model_criterion(preds, labels, 'CE')
	running_loss = running_loss + loss.item()

	del preds
	del input_data
	del labels

model_loss = running_loss/dset_size

if(model_number == task_number):
	print ("Auto Encoder correctly routed the task")

else:
	print ("Incorrect routing")

print ("The model selected reports a loss of {}".format(model_loss))











