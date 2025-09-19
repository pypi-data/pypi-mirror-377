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
from perforatedai import modules_perforatedai as MPA
from perforatedbp import check_license
import copy
import random


def update_dendrite_tensor_values(DENDRITE_TENSOR_VALUES):
    return DENDRITE_TENSOR_VALUES + [
        "top_dendrite_candidate_averages",
        "prev_dendrite_candidate_correlation",
        "current_correlations_for_parallel",
        "best_score",
        "previous_best_score",
        "prev_dendrite_candidate_average",
        "main_grad_average_for_scaling",
        "candidate_grad_average_for_scaling",
        "indexes_of_best",
        "nodes_best_improved_this_epoch",
        "parents_average_d_vector",
        #'parents_average_d_mags',
        "normal_pass_average_d",
        #'normal_pass_average_d_mags',
        #'normal_pass_average_d_sq'
    ]


def update_dendrite_single_values(DENDRITE_SINGLE_VALUES):
    return DENDRITE_SINGLE_VALUES + [
        "breaking",
        "locked",
        "best_score_improved_this_time_step",
        "best_score_improved_this_epoch",
        #'parents_average_d_sq'
    ]


# These are included above, they just get skipped for reinit if not live
non_live_skip_values = [
    "normal_pass_average_d",
    #'normal_pass_average_d_mags',
    #'normal_pass_average_d_sq'
]


if GPA.doing_thing:
    dendrite_single_values = dendrite_single_values + [
        "normal_pass_max_mean_act",
        "parent_max_mean_act",
    ]
    non_live_skip_values = non_live_skip_values + ["normal_pass_max_mean_act"]


def update_value_tracker_arrays(VALUE_TRACKER_ARRAYS):
    return VALUE_TRACKER_ARRAYS + ["current_parent_d"]


def filter_backward_pb(val, values, candidate_nonlinear_outs):
    with torch.no_grad():
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
        if GPA.pai_tracker.member_vars["mode"] == "p":
            for i in range(0, GPA.global_candidates):
                # this is where the grad_in is actually set for the tagger
                average_d_matrix = values[i].parents_average_d_vector.view(view_tuple)
                if val.device.type == "cpu":
                    device_index = 0
                else:
                    device_index = val.device.index
                if (
                    GPA.debugging_memory_leak
                    and len(values[i].current_parent_d[device_index]) != 0
                ):
                    print(
                        "%s called backward but then didn't get PAIified.  This can cause a memory leak. Check processors."
                        % values[i].layer_name
                    )
                if len(candidate_nonlinear_outs) == 0:
                    print(
                        "Trying to call backwards but module %s wasn't PAIified"
                        % values[i].layer_name
                    )
                    sys.exit(0)
                if GPA.dendrite_learn_mode:
                    values[i].current_parent_d[device_index].append(
                        (val - (average_d_matrix)).detach()
                    )
                    candidate_nonlinear_outs[i].register_hook(
                        lambda grad: values[i]
                        .current_parent_d[device_index][-1]
                        .to(val.device)
                    )
                # pretty sure this next line is the right way to do this, not above.  doesn't seem to really have any significant impact though.  should run normal unit tests and xor_main with it to be sure.
                # Values[i].current_parent_d = (val).detach()
                # candidate_nonlinear_outs[i].register_hook(lambda grad: (Values[i].current_parent_d  - (Values[i].parents_average_d_matrix)))
        if True:
            values[0].normal_pass_average_d *= 0.99
            """
            print('val and tuple')
            print(val.shape)
            print(math_tuple)
            print(values[0].layer_name)
            """
            try:
                values[0].normal_pass_average_d += (
                    val.sum(math_tuple) * 0.01
                ) / full_mult
                if GPA.dpp_verbose:
                    print("no error with")
                    print(val.shape)
                    print(values[0].this_node_index)
                    print(math_tuple)
                    print(full_mult)
            except Exception as e:
                print(e)
                print("Error with type shape in %s" % values[0].layer_name)
                print(val.shape)
                print(values[0].this_node_index)
                print(math_tuple)
                print(full_mult)
                import pdb

                pdb.set_trace()
                exit(0)
            # values[0].normal_pass_average_d_mags *= 0.99
            # values[0].normal_pass_average_d_mags += (val.abs().sum(math_tuple) * 0.01) / full_mult
            # values[0].normal_pass_average_d_std = values[0].normal_pass_average_d_std * 0.99 + val.std((math_tuple))*0.01

            # this is **2 after everything because it is a scalar to scale the final grad_in.  The final gradient that actually gets applied is gradient.sum(math_tuple)
            # final weight adjustment/actual grad value is net.module.main_module[0].PAINeuronModule.current_d.sum(math_tuple)
            # You can tell this by looking at the bias values in grad.  It will be similar for the convolution kernel weight values in grad
            """
            values[0].normal_pass_average_d_sq *= 0.99
            if(GPA.grad_sum_first):
                values[0].normal_pass_average_d_sq += ((val)**2).sum(math_tuple) * 0.01# / full_mult #if changing here change previous in data parallel
            else:
                values[0].normal_pass_average_d_sq += ((val)).sum(math_tuple)**2 * 0.01# / full_mult
            """

            # values[0].current_d_out = grad_output
            if GPA.learn_dendrites_live:
                full_mult = 1
                view_tuple = []
                for dim in range(len(val.shape)):
                    if dim == values[0].this_node_index:
                        view_tuple.append(-1)
                        continue
                    full_mult *= val.shape[dim]
                    view_tuple.append(1)

                # Keep these values updated on the fly  if this works, might only need to do mean, above and will stay the same and be faster.
                # values[0].parents_average_d_mags.copy_(values[0].normal_pass_average_d_mags.double().detach().clone()/(full_mult))
                values[0].parents_average_d_vector.copy_(
                    values[0].normal_pass_average_d.detach().clone() / (full_mult)
                )
                # values[0].parents_average_d_sq.copy_(values[0].normal_pass_average_d_sq.double().mean().detach().clone())#/full_mult)

                values[0].parents_average_d_vector.requires_grad = False
                # Values[0].parents_average_d_sq.requires_grad = False
                # Values[0].parents_average_d_mags.requires_grad = False
    if GPA.extra_verbose:
        print("%s completing backward" % values[0].layer_name)


def set_grad_params(model, to_set):
    for p in model.parameters():
        p.requires_grad = to_set


def set_module_n_pb(neuron_module):
    set_grad_params(neuron_module.main_module, True)
    # pb to top [x] is a nodes_x_dendrite_module array, old one of one smaller is deleted and never used again
    if neuron_module.dendrite_modules_added > 0:
        neuron_module.dendrites_to_top[
            neuron_module.dendrite_modules_added - 1
        ].requires_grad = True
    for param in neuron_module.dendrite_module.dendrites_to_dendrites:
        param.requires_grad = False


def set_module_p_pb(neuron_module, mode):
    if GPA.learn_dendrites_live:
        neuron_module.candidate_to_top = nn.Parameter(
            torch.zeros(
                (1, neuron_module.out_channels), device=GPA.device, dtype=GPA.d_type
            )
            .detach()
            .clone(),
            requires_grad=True,
        )
        neuron_module.register_parameter(
            "current_candidate_to_top", neuron_module.candidate_to_top
        )

        # THIS SHOULDN'T BE NEEDED BUT MESSED IT UP IN THIS RUN
        set_grad_params(neuron_module.main_module, True)
        # pb to top [x] is a nodes_x_dendrite_module array, old one of one smaller is deleted and never used again
        if neuron_module.dendrite_modules_added > 0:
            neuron_module.dendrites_to_top[
                neuron_module.dendrite_modules_added - 1
            ].requires_grad = True
            for param in neuron_module.dendrite_module.dendrites_to_dendrites:
                param.requires_grad = True

    # set normal layers to no longer learn
    else:
        set_grad_params(neuron_module.main_module, False)
        if neuron_module.dendrite_modules_added > 0:
            neuron_module.dendrites_to_top[
                neuron_module.dendrite_modules_added - 1
            ].requires_grad = False
            for param in neuron_module.dendrite_module.dendrites_to_dendrites:
                param.requires_grad = False


def load_tagger_values(neuron_module):
    neuron_module.dendrite_module.load_tagger_values()


def apply_pb(
    neuron_module,
    out,
    candidate_outs,
    candidate_nonlinear_outs,
    candidate_outs_non_zeroed,
):
    # if pb is not in p mode it means this one isnt doing a grad
    if (
        GPA.pai_tracker.member_vars["mode"] == "p"
        and neuron_module.dendrite_module.mode == "p"
    ):
        ## NEED LOOP HERE
        for i in range(0, GPA.global_candidates):
            if GPA.learn_dendrites_live:
                to_top = neuron_module.candidate_to_top[i, :]
                for dim in range(len(candidate_outs_non_zeroed[i].shape)):
                    if dim == neuron_module.this_node_index:
                        continue
                    to_top = to_top.unsqueeze(dim)
                if GPA.confirm_correct_sizes:
                    to_top = to_top.expand(
                        list(candidate_outs_non_zeroed[i].size())[
                            0 : neuron_module.this_node_index
                        ]
                        + [neuron_module.out_channels]
                        + list(candidate_outs_non_zeroed[i].size())[
                            neuron_module.this_node_index :
                        ]
                    )
                out = out + (
                    candidate_outs_non_zeroed[i].to(out.device) * to_top.to(out.device)
                )

            # also try this before the next out thing
            out = out + candidate_outs[i].to(out.device)

    # POINT1
    if GPA.pai_tracker.member_vars["mode"] == "n" and GPA.doing_thing:
        if (
            out.abs().max()
            > neuron_module.dendrite_module.dendrite_values[0].normal_pass_max_mean_act
        ):
            neuron_module.dendrite_module.dendrite_values[0].normal_pass_max_mean_act[
                0
            ] = (out.abs().max().item())
            if GPA.learn_dendrites_live:
                neuron_module.dendrite_module.dendrite_values[
                    0
                ].parent_max_mean_act.copy_(
                    neuron_module.dendrite_module.dendrite_values[0]
                    .normal_pass_max_mean_act[0]
                    .detach()
                    .clone()
                )
                neuron_module.dendrite_module.dendrite_values[
                    0
                ].parent_max_mean_act.requires_grad = False
        if (
            neuron_module.dendrite_module.dendrite_values[0].normal_pass_max_mean_act[0]
            == 0
        ):
            print("An entire layer got exactly 0 Correlation")
    return out


def setup_hooks(neuron_module, out, candidate_nonlinear_outs):
    if candidate_nonlinear_outs == {}:
        out.register_hook(
            lambda grad: MPA.filter_backward(
                grad, neuron_module.dendrite_module.dendrite_values, {}
            )
        )
    else:
        candidate_nonlinear_outs[0] = candidate_nonlinear_outs[0].to(out.device)
        out.register_hook(
            lambda grad: MPA.filter_backward(
                grad,
                neuron_module.dendrite_module.dendrite_values,
                candidate_nonlinear_outs,
            )
        )


def create_extra_tensors(dendrite_module):
    # base layer options
    dendrite_module.current_recurrent_pass_tensors = []
    dendrite_module.current_recurrent_pass_candidate_tensors = []
    # PAI VALUES
    dendrite_module.normal_learning_taggers = {}
    dendrite_module.internal_recurrent = False

    dendrite_module.best_weights = {}
    dendrite_module.best_biases = {}
    dendrite_module.best_bn_weights = {}
    dendrite_module.best_bn_biases = {}
    dendrite_module.random_pai_to_candidates = GPA.default_random_pai_to_candidates


def init_candidates(dendrite_module, j):
    dendrite_module.dendrites_to_candidates[j].data.pai_wrapped = True
    if dendrite_module.random_pai_to_candidates:
        with torch.no_grad():
            dendrite_module.dendrites_to_candidates[j].normal_(
                0, math.sqrt(2.0 / dendrite_module.out_channels)
            )
    # dendrite_module.register_parameter(('dendrites_to_candidates'+str(j)), dendrite_module.dendrites_to_candidates[j])


def set_pb_mode(dendrite_module, mode):
    if mode == "n":
        if GPA.verbose:
            print("so calling all the things to add to layers")
        for i in range(0, GPA.global_candidates):
            dendrite_module.dendrite_values[i].locked[0] = 1

        # set PAI nodes to no longer learn

        set_grad_params(
            dendrite_module.layers[dendrite_module.num_dendrites],
            GPA.dendrite_update_mode,
        )
        for param in dendrite_module.dendrites_to_dendrites:
            param.requires_grad = GPA.dendrite_update_mode
        if dendrite_module.num_dendrites > 0:
            for j in range(0, GPA.global_candidates):  # Loopy Loops
                dendrite_module.dendrites_to_candidates[j].requires_grad = False


### CLOSED ONLY
def killer_recursive(in_vals, killing):
    # Check license every 0.000001% of the time, this should also have been checked in convert network
    if random.random() < 0.000001:
        license_file = "./license.yaml"
        status = check_license.valid_license(license_file)
        if not status:
            print("License Invalid. Quiting...")
            sys.exit(1)
    device = None
    if type(in_vals) is list:
        if len(in_vals) == 0:
            return in_vals, None
        for index in range(len(in_vals)):
            in_vals[index], device2 = killer_recursive(in_vals[index], killing)
            if not device2 is None:
                device = device2
    elif type(in_vals) is tuple:
        if len(in_vals) == 0:
            return in_vals, None
        for index in range(len(in_vals)):
            in_vals = list(in_vals)
            in_vals[index], device2 = killer_recursive(in_vals[index], killing)
            if not device2 is None:
                device = device2
            in_vals = tuple(in_vals)
    elif type(in_vals) is dict:
        if len(in_vals.keys()) == 0:
            return in_vals, None
        for index in in_vals.keys():
            in_vals[index], device2 = killer_recursive(in_vals[index], killing)
            if not device2 is None:
                device = device2
    elif issubclass(torch.Tensor, type(in_vals)):
        with torch.cuda.device_of(in_vals):
            if killing:
                to_return = grad_killer(in_vals).detach().clone()
            else:
                to_return = in_vals
            return to_return, in_vals.device
    else:
        return in_vals, None
    return in_vals, device

    ### END CLOSED ONLY


def preprocess_pb(*args, **kwargs):
    args2, device = killer_recursive(args, GPA.dendrite_graph_mode)
    kwargs2, device2 = killer_recursive(kwargs, GPA.dendrite_graph_mode)
    return args2, kwargs2


def forward_candidates(dendrite_module, view_tuple, outs, *args, **kwargs):
    candidate_outs = {}
    candidate_nonlinear_outs = {}
    candidate_non_zeroed = {}
    for i in range(0, GPA.global_candidates):
        # dendrite_module.mode will only not also be p if this is not learning
        if GPA.pai_tracker.member_vars["mode"] == "p" and dendrite_module.mode == "p":
            args2, device = killer_recursive(args, GPA.candidate_graph_mode)
            kwargs2, device2 = killer_recursive(kwargs, GPA.candidate_graph_mode)
            if device is None:
                device = device2

            """
            DEBUG: if you\'re here this layer should have PAI nodes which means
            candidate processors should have been initialized.  If its not you are likely
            still pointing to the old model that doesn\'t have PAI nodes added.  make sure
            when you call add validation score you are properly setting the model
            """
            if dendrite_module.candidate_processors != []:
                args2, kwargs2 = dendrite_module.candidate_processors[i].pre_d(
                    *args2, **kwargs2
                )

            """
            DEBUG:
            If you are getting a cpu vs gpu issue on this line its because the model is receiving args that are on the wrong thing, but within the forward function it gets passed to the correct spot.  don't ever call to() in the forward function, call it before it gets passed in
            """
            candidate_out_values = dendrite_module.candidate_module[i].to(device)(
                *args2, **kwargs2
            )
            if dendrite_module.candidate_processors != []:
                candidate_outs[i] = dendrite_module.candidate_processors[i].post_d(
                    candidate_out_values
                )
            else:
                candidate_outs[i] = candidate_out_values

            for in_index in range(dendrite_module.num_dendrites):
                # PARALLEL HACK
                if view_tuple == [
                    1
                ]:  # This is only the case when passing a single datapoint rather than a batch
                    candidate_outs[i] = (
                        candidate_outs[i].to(device)
                        + dendrite_module.dendrites_to_candidates[i][in_index, :].to(
                            device
                        )
                        * outs[in_index]
                    )
                else:
                    candidate_outs[i] = (
                        candidate_outs[i].to(device)
                        + dendrite_module.dendrites_to_candidates[i][in_index, :]
                        .view(view_tuple)
                        .to(device)
                        * outs[in_index]
                    )

            if GPA.dendrite_learn_mode:
                candidate_outs[i] = pai_tagger(
                    candidate_outs[i], dendrite_module.dendrite_values[i].to(device)
                )
            # import pdb; pdb.set_trace()
            candidate_nonlinear_outs[i] = GPA.pb_forward_function(candidate_outs[i]).to(
                device
            )

            # candidate_nonlinear_outs chosen randomly, just generally saying dont do this during inference, only training.
            if dendrite_module.training:
                # no it seems like this should be cleared on the main module so when its replicated it should work properly.
                if device.type == "cpu":
                    device_index = 0
                else:
                    device_index = device.index
                if (
                    GPA.debugging_memory_leak
                    and len(
                        dendrite_module.dendrite_values[i].dendrite_outs[device_index]
                    )
                    != 0
                ):
                    if GPA.no_backward_workaround:
                        del dendrite_module.dendrite_values[i].dendrite_outs[
                            device_index
                        ][-1]
                        # This may also be required for no_backward_workaround.  Found it earlier, but didn't have a noBackwards problem to debug with
                        # del dendrite_module.dendrite_values[i].current_parent_d[device_index][-1]
                    else:
                        print(
                            "%s is in backwards graph multiple times.  This will cause a memory leak unless it is a recurrent layer.  Currently stacked (%d/%d) times"
                            % (
                                dendrite_module.name,
                                len(
                                    dendrite_module.dendrite_values[0].dendrite_outs[0]
                                ),
                                len(
                                    dendrite_module.dendrite_values[0].current_parent_d[
                                        0
                                    ]
                                ),
                            )
                        )
                        print(
                            "If this is coming up before a memory leak that happens anywhere other than the first batch of an epoch you NEED to debug this."
                        )
                        print("Check the Memory Leak section of the debugging MD file.")
                        print(
                            "If this is just being printed but there is not a memory leak you can set GPA.debugging_memory_leak = False"
                        )
                        print(
                            "If you don't have any recurrent layers you can also clear this by in a more memory efficient way by setting GPA.no_backward_workaround = True"
                        )
                        print(
                            "If you set GPA.no_backward_workaround = True and it causes a IndexError: list index out of range error, that means you do have a recurrent layer"
                        )
                        # import pdb; pdb.set_trace()
                if GPA.dendrite_learn_mode:
                    dendrite_module.dendrite_values[i].dendrite_outs[
                        device_index
                    ].append(candidate_nonlinear_outs[i].detach().clone().to(device))
                    if GPA.extra_verbose and candidate_nonlinear_outs[i].isnan().any():
                        print("got candidate out nan")
                        import pdb

                        pdb.set_trace()
            candidate_non_zeroed[i] = (
                candidate_nonlinear_outs[i].detach().clone().to(device)
            )
            candidate_outs[i] = no_forward(candidate_nonlinear_outs[i])

    return candidate_outs, candidate_nonlinear_outs, candidate_non_zeroed


from packaging import version

if version.parse(torch.__version__) >= version.parse("2.4.0"):
    from torch.amp import custom_fwd, custom_bwd
else:
    from torch.cuda.amp import custom_fwd, custom_bwd


def pai_tagger(inp, Values):
    class Tagger(torch.autograd.Function):
        @staticmethod
        @custom_fwd(device_type="cuda", cast_inputs=torch.float32)
        def forward(ctx, inp):
            return inp

        @staticmethod
        @custom_bwd(device_type="cuda")
        def backward(ctx, grad_out):
            yolo_testing = False
            # Check license every 0.000001% of the time, this should also have been checked in convert network
            if random.random() < 0.000001:
                license_file = "./license.yaml"
                status = check_license.valid_license(license_file)
                if not status:
                    print("License Invalid. Quiting...")
                    sys.exit(1)

            with torch.no_grad():
                saved_values = Values
                if GPA.extra_verbose:
                    print("%s calling Dendrite backward" % saved_values.layer_name)

                if saved_values.layer_name == ".layers.29" and yolo_testing:
                    GPA.extra_verbose = True

                if saved_values.locked:
                    return grad_out * 0, None

                math_tuple = []
                view_tuple = []
                for i in range(len(grad_out.size())):
                    if i == Values.this_node_index:
                        view_tuple.append(-1)
                        continue
                    math_tuple.append(i)
                    view_tuple.append(1)

                eps = 0.00000001
                if grad_out.device.type == "cpu":
                    device_index = 0
                else:
                    device_index = grad_out.device.index
                if len(saved_values.dendrite_outs[device_index]) == 0:
                    print(
                        "Dendrite does not have output Value for layer %s"
                        % saved_values.layer_name
                    )
                    print(
                        "This is caused by your model being in eval mode when you call loss.backwards()"
                    )
                    import pdb

                    pdb.set_trace()
                last_dendrite_outs = (
                    saved_values.dendrite_outs[device_index][-1]
                    .detach()
                    .clone()
                    .to(grad_out.device)
                )
                last_parent_d = (
                    saved_values.current_parent_d[device_index][-1]
                    .detach()
                    .clone()
                    .to(grad_out.device)
                )
                direction = saved_values.prev_dendrite_candidate_correlation.sign()
                temp_reshape_direction = direction.view(view_tuple)
                current_correlations = last_dendrite_outs * (last_parent_d)

                # shouldn't this be the average?  its * all of the current outputs and parent errors. why would it sum them before subtracting them from the average output * the average errors.
                # retain all PAI is currently broken. doesn't seem to actually work and also messages up saving     graphs.

                # looks lke this is worse, but not sure why.  Switch back to the original and move on.
                # if every coming back to this remember to chance cor calculation to just be this later
                # current_correlations = (last_dendrite_outs.to(last_parent_d.device)-aveOut) * (last_parent_d)
                # current_correlations = current_correlations.mean(math_tuple)

                # can also try one where it switches to mean if the sum is > 1. or allow it to be set by layer manually
                if GPA.correlations_by_mean:
                    current_correlations = current_correlations.mean((math_tuple))
                else:
                    current_correlations = current_correlations.sum((math_tuple))

                # got rid of averagedsq because doing a proportional scaling later so this scaling doesnt matter.
                if GPA.formula_type == 0:
                    grad_in = -(
                        grad_out.detach() * (temp_reshape_direction)
                    )  # / ((saved_values.parents_average_d_sq + eps))
                elif GPA.formula_type == 1:
                    grad_in = -(
                        grad_out.detach()
                        * current_correlations.view(view_tuple)
                        * (temp_reshape_direction)
                    )  # / ((saved_values.parents_average_d_sq + eps))
                # this doesnt work, the second gradin is just the same since its average and not actual sum
                elif GPA.formula_type == 2:
                    grad_in = -(
                        grad_out.detach()
                        * current_correlations.view(view_tuple)
                        * (temp_reshape_direction)
                    )  # / ((saved_values.parents_average_d_sq + eps))
                    grad_in /= (
                        grad_out.pow(2) * current_correlations.view(view_tuple).pow(2)
                    ).sqrt()
                elif GPA.formula_type == 3:
                    grad_in = -(
                        grad_out.detach()
                        * (
                            last_dendrite_outs
                            - saved_values.prev_dendrite_candidate_average.view(
                                view_tuple
                            )
                        )
                        * (temp_reshape_direction)
                    )
                # same as 2
                elif GPA.formula_type == 4:
                    grad_in = -(
                        grad_out.detach()
                        * (
                            last_dendrite_outs
                            - saved_values.prev_dendrite_candidate_average.view(
                                view_tuple
                            )
                        )
                        * (temp_reshape_direction)
                    )
                    grad_in /= (
                        grad_out.pow(2)
                        * (
                            last_dendrite_outs
                            - saved_values.prev_dendrite_candidate_average.view(
                                view_tuple
                            )
                        ).pow(2)
                    ).sqrt()

                # print('top')
                # print(saved_values.top_dendrite_candidate_averages)
                # print('ave')
                # print(saved_values.prev_dendrite_candidate_average)

                # adjust correlations

                saved_values.top_dendrite_candidate_averages.copy_(
                    last_dendrite_outs.mean((math_tuple))
                )

                saved_values.prev_dendrite_candidate_average *= 0.99
                saved_values.prev_dendrite_candidate_average += (
                    saved_values.top_dendrite_candidate_averages * 0.01
                )

                if GPA.extra_verbose:
                    print("new top")
                    print(saved_values.top_dendrite_candidate_averages)
                    print("new ave")
                    print(saved_values.prev_dendrite_candidate_average)
                    print("parentsAverageD")
                    print(saved_values.parents_average_d_vector)
                    print("last_dendrite_outs")
                    print(last_dendrite_outs)
                    print("last_parent_d")
                    print(last_parent_d)
                    print("current_correlations")
                    print(current_correlations)
                # if(not GPA.using_pia_data_parallel):
                if True:
                    # TODO: Should this use top_dendrite_candidate_averages until initialized has completed?
                    cor = current_correlations - (
                        saved_values.prev_dendrite_candidate_average
                        * saved_values.parents_average_d_vector
                    )  # / net['layers'][l]['sumSqError'][j]
                    if GPA.extra_verbose:
                        print("prev")
                        print(saved_values.prev_dendrite_candidate_correlation)
                        print("cor")
                        print(cor)
                        print("current_correlations")
                        print(current_correlations)
                    saved_values.prev_dendrite_candidate_correlation *= 0.99
                    saved_values.prev_dendrite_candidate_correlation += cor * 0.01
                    if GPA.extra_verbose:
                        print("next prev")
                        print(saved_values.prev_dendrite_candidate_correlation)
                        if (
                            (saved_values.parents_average_d_vector).isnan().any()
                            or (saved_values.prev_dendrite_candidate_average)
                            .isnan()
                            .any()
                            or (saved_values.top_dendrite_candidate_averages)
                            .isnan()
                            .any()
                            or (current_correlations).isnan().any()
                        ):
                            print("got a nan in correlation score")
                            import pdb

                            pdb.set_trace()

                    temp_abs = (
                        saved_values.prev_dendrite_candidate_correlation.detach().abs()
                    )

                    # best score is the max score of the previous best score and the current recently averaged correlation

                    [best_score, temp_best_indices] = torch.max(
                        torch.cat(
                            (
                                saved_values.best_score.unsqueeze(0),
                                temp_abs.unsqueeze(0),
                            ),
                            0,
                        ),
                        0,
                    )
                    saved_values.best_score.copy_(best_score)

                    # print(saved_values.best_score)
                    # if that best score has improved enough or this is the very first iteration
                    if (
                        (
                            (
                                saved_values.best_score
                                * (1.0 - GPA.pai_improvement_threshold)
                            )
                            - saved_values.previous_best_score
                        ).max()
                        > 0.00000001
                        and (
                            saved_values.best_score - saved_values.previous_best_score
                        ).max()
                        > GPA.pai_improvement_threshold_raw
                    ) or saved_values.initialized.item() == 0:

                        if (
                            saved_values.best_score_improved_this_epoch[0] == 0
                            and GPA.verbose
                        ):
                            print(
                                "Score from %.16f to %.16f for %s with initialized %d"
                                % (
                                    saved_values.previous_best_score.mean(),
                                    saved_values.best_score.mean(),
                                    saved_values.layer_name,
                                    saved_values.initialized.item(),
                                )
                            )
                        # say that best score did improve this epoch and time step
                        saved_values.best_score_improved_this_epoch[0].copy_(
                            torch.tensor(1)
                        )
                        # print('setting best score improved this timestep with')
                        # print(saved_values.best_score)
                        # print(saved_values.previous_best_score)
                        # print(saved_values.initialized.item())
                        saved_values.best_score_improved_this_time_step[0].copy_(
                            torch.tensor(1)
                        )
                        # set the indexes of the best candidate
                        saved_values.indexes_of_best.copy_(temp_best_indices)

                        ##check where temp_abs = best_score and save the weights for those candidates in forward for the layer next iteration
                        # this is where that saveBest function was maybe called?
                        [values, indexes] = torch.max(saved_values.indexes_of_best, 0)
                        saved_values.nodes_best_improved_this_epoch += (
                            saved_values.indexes_of_best
                        )
                        # only replace the ones that are bigger
                        saved_values.previous_best_score.copy_(
                            torch.max(
                                saved_values.best_score,
                                saved_values.previous_best_score,
                            ).detach()
                        )
                    else:
                        # print('setting best score improved this timestep with')
                        # print(saved_values.best_score)
                        # print(saved_values.previous_best_score)
                        # print(saved_values.initialized.item())
                        saved_values.best_score_improved_this_time_step[0].copy_(
                            torch.tensor(0)
                        )
                        saved_values.indexes_of_best *= 0
                    if saved_values.breaking.item():
                        pdb.set_trace()
                # else: # if not new data parallel all of this is being done in gather
                # saved_values.current_correlations_for_parallel = current_correlations

                if (
                    saved_values.initialized.item() < GPA.initial_correlation_batches
                ):  # *2?
                    # for the first 10 iterations average out the initial conditions a little bit
                    # at the beginning have it equal the actual average, not the abs average
                    # this is because the best is the abs of running best, but running best is average of a bunch of positives and negatives, so to just initialize as a single value it it a high positive or negative

                    saved_values.candidate_grad_average_for_scaling *= (
                        saved_values.initialized
                    )
                    saved_values.candidate_grad_average_for_scaling += (
                        grad_in.abs().mean(math_tuple)
                    )
                    saved_values.candidate_grad_average_for_scaling /= (
                        saved_values.initialized + 1.0
                    )
                    saved_values.main_grad_average_for_scaling *= (
                        saved_values.initialized
                    )
                    saved_values.main_grad_average_for_scaling += (
                        last_parent_d.abs().mean(math_tuple)
                    )
                    saved_values.main_grad_average_for_scaling /= (
                        saved_values.initialized + 1.0
                    )

                    # if(not GPA.using_pia_data_parallel):
                    if True:
                        saved_values.prev_dendrite_candidate_average *= (
                            saved_values.initialized
                        )
                        saved_values.prev_dendrite_candidate_average += (
                            saved_values.top_dendrite_candidate_averages
                        )
                        saved_values.prev_dendrite_candidate_average /= (
                            saved_values.initialized + 1.0
                        )
                        # print('init update prev_dendrite_candidate_average')
                        # print(saved_values.prev_dendrite_candidate_average)

                        cor = current_correlations - (
                            saved_values.prev_dendrite_candidate_average
                            * saved_values.parents_average_d_vector
                        )  # / net['layers'][l]['sumSqError'][j]
                        # print('init update cor')
                        # print(cor)

                        saved_values.prev_dendrite_candidate_correlation *= (
                            saved_values.initialized
                        )
                        saved_values.prev_dendrite_candidate_correlation += cor
                        saved_values.prev_dendrite_candidate_correlation /= (
                            saved_values.initialized + 1.0
                        )
                        # print('init update prev')
                        # print(saved_values.prev_dendrite_candidate_correlation)
                    # else:
                    # saved_values.current_correlations_for_parallel.copy_(current_correlations)
                    # and other values should be zeroed so they dont effect things during this initialization step
                    saved_values.best_score.copy_(saved_values.best_score.detach() * 0)
                    saved_values.previous_best_score.copy_(
                        saved_values.previous_best_score.detach() * 0
                    )
                    saved_values.initialized += 1.0
                    # print('initialized')
                    # print(saved_values.initialized.item())
                    scalar = 0.0000000
                else:
                    """
                    if this candidate is getting errors so low that the average at this point is 0 it is likely because vanishing gradient has died so theres not much to do here anyway
                    just set scalar to 0 and move on.  TODO: see if there is a better way to to this?  When it was caught with with autograd.detect_anomaly(): around forward->backward .normal_pass_average_d was actually
                    just a super small number but not exactly 0.  this means there is some amount of error it just is getting deleted after averaging because of float resolution.
                    """
                    if (
                        saved_values.candidate_grad_average_for_scaling.mean().item()
                        == 0
                    ):
                        # pdb.set_trace()
                        scalar = 0.0
                    else:
                        # saved_values.candidate_grad_average_for_scaling = grad_in.abs().mean(math_tuple) * 0.001 + saved_values.candidate_grad_average_for_scaling * 0.999
                        # grad_in = (grad_in * (saved_values.parents_average_d_vector.abs().mean()/saved_values.candidate_grad_average_for_scaling.abs().mean())) / saved_values.current_parent_d.abs().std()#.view(1,-1,1,1))
                        # scalar = saved_values.parents_average_d_vector.abs().mean()/saved_values.candidate_grad_average_for_scaling.abs().mean()
                        scalar = (
                            saved_values.main_grad_average_for_scaling.mean()
                            / saved_values.candidate_grad_average_for_scaling.mean()
                        )
                        # print('\n\n%s scaler ended up as ' % saved_values.layer_name)
                        # print(scalar)
                        # print('with')
                        # print(saved_values.parents_average_d_mags.mean())
                        # print('from')
                        # print(saved_values.main_grad_average_for_scaling.mean())
                        # print('and')
                        # print(saved_values.candidate_grad_average_for_scaling.mean())

                        # scalar = (1/saved_values.parents_average_d_sq)
                        # scalar = 1 seems to not make things die.  gotta figure out a way to do this scalar reasonably.  Why would this not work if its scaling it to the same magnitude as the main gradient is learning?
                        # scalar = 1
                if GPA.doing_thing:
                    scalar /= saved_values.parent_max_mean_act.item()

                if saved_values.layer_name == ".layers.29" and yolo_testing:
                    GPA.extra_verbose = False

                grad_in = grad_in * scalar  # .view(1,-1,1,1))
                del saved_values.current_parent_d[device_index][-1]
                del saved_values.dendrite_outs[device_index][-1]
                if GPA.extra_verbose:
                    print("%s completing Dendrite backward" % saved_values.layer_name)

                return grad_in, None

    return Tagger.apply(inp)


def grad_killer(inp):
    class Killer(torch.autograd.Function):
        @staticmethod
        def forward(ctx, inp):
            # print('forward called')
            return inp

        @staticmethod
        def backward(ctx, grad_out):
            # print('backward called')
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


def reinitialize_for_pb(dendrite_module):

    for val_name in MPA.DENDRITE_REINIT_VALUES:
        if (not val_name in non_live_skip_values) or GPA.learn_dendrites_live:
            setattr(dendrite_module, val_name, getattr(dendrite_module, val_name) * 0)

    if GPA.doing_thing:
        dendrite_module.parent_max_mean_act.copy_(
            dendrite_module.normal_pass_max_mean_act.detach().clone()
        )
        dendrite_module.parent_max_mean_act.requires_grad = False
    # dendrite_module.parents_average_d_mags.copy_(dendrite_module.normal_pass_average_d_mags.double().detach().clone())
    dendrite_module.parents_average_d_vector.copy_(
        dendrite_module.normal_pass_average_d.detach().clone()
    )
    # dendrite_module.parents_average_d_sq.copy_(dendrite_module.normal_pass_average_d_sq.double().mean().detach().clone())
    dendrite_module.parents_average_d_vector.requires_grad = False
    # dendrite_module.parents_average_d_sq.requires_grad = False
    # dendrite_module.parents_average_d_mags.requires_grad = False
