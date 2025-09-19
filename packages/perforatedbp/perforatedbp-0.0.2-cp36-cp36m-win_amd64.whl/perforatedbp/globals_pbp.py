# Copyright (c) 2025 Perforated AI
import math
import torch
import torch.nn as nn
import torchvision.models.resnet as resnet
import sys

### This file only contains globals which are not included in original

### Global Constants


# Debug settings
debugging_memory_leak = True

# Confirmation flags for non-recommended options
count_training_params = False

no_backward_workaround = False


dpp_verbose = False
verbose_scores = False

# Prevent flow of error back to network after candidates and dendrites
doing_perferated_candidates = True
doing_perferated_dendrites = True
# Do Correlation learning
doing_cc = True
# Allow dendrite weights to continue to learn
update_dendrite_weights = False

internal_batch_norm = False
variable_p = 142

# Typically the best way to do correlation scoring is to do a sum over each index, but sometimes for large convolutional layers this
# can cause exploding gradients.  To correct this, the mean can be used instead.
correlations_by_mean = False

grad_sum_first = True

# this is for whether or not to batch norm the PAI outputs
default_pai_batch = False
default_random_pai_to_candidates = False
default_pai_dropout = 0.0

# Improvement thresholds
# this is if even a single node has gone up by at least 10% over the total number of epochs to switch.
pai_improvement_threshold = (
    0.1  # improvement increase needed to call a new best PAIScore
)
pai_improvement_threshold_raw = (
    1e-5  # raw increase needed, if its lower than this its not really learning
)

doing_mean_best = 0
formula_type = 0

# SWITCH MODE SETTINGS

p_epochs_to_switch = 10
cap_at_n = False  # Makes sure PAI rounds last max as long as first N round


doing_thing = 0

# if one is true both should be true.
# seems to be better for conv but may or may not be better for linear
learn_dendrites_live = False
no_extra_n_modes = False

# Dendrite retention settings
save_all_epochs = False

switch_on_lr_change = False

# this number is to check how many batches to average out the initial correlation score over
# this should be at least 100 and up to 10% of a whole epoch
initial_correlation_batches = 100

doing_dropout_for_small = True
doing_dropout_for_small_input = False

relu_mode = "relu"
sigmoid_mode = "sigmoid"
tan_h_mode = "tanH"
leaky_relu_mode = "leakyRelu"
no_nonlinarity_mode = "noNonliniarity"
softmax_top_layer_mode = "softmaxTopLayer"


pb_forward_function = torch.sigmoid
# Prevent flow of error back to network after candidates and dendrites (Doing Perforation)
candidate_graph_mode = True  # default True
dendrite_graph_mode = True  # default True
# Do Correlation learning (Doing CC)
dendrite_learn_mode = True  # default True
# Allow dendrite weights to continue to learn (unfreeze Dendrite weights)
dendrite_update_mode = False  # default False
