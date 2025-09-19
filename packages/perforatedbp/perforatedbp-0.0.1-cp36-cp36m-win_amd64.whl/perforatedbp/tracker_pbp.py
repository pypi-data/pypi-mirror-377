import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F
import math
import sys
import numpy as np
import pdb
import io
import shutil

import time
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.use("Agg")
import pandas as pd
import copy
import os
from pydoc import locate

from perforatedai import globals_perforatedai as GPA


def check_cap_switch(tracker, this_count):
    if (
        tracker.member_vars["switch_mode"] == GPA.DOING_HISTORY
        and tracker.member_vars["mode"] == "p"
        and GPA.cap_at_n
    ):
        # if(len(tracker.member_vars['switch_epochs']) == 1):
        # trying method with always capping at the first N
        prev_count = tracker.member_vars["switch_epochs"][0]
        # else:
        # prevCount = tracker.member_vars['switch_epochs'][-1] - tracker.member_vars['switch_epochs'][-2]
        # print('Checking cap_at_n switch with this count  %d, prev %d' % (thisCount, prevCount))
        if this_count >= prev_count:
            cap_switch = True
            if not GPA.silent:
                print("cap_at_n is True")


def history_switch(tracker):
    (
        (tracker.member_vars["mode"] == "p")
        and (
            tracker.member_vars["num_epochs_run"]
            - tracker.member_vars["epoch_last_improved"]
            >= GPA.p_epochs_to_switch
        )
    )


### CLOSED ONLY
# this is for if the pb score improved
def best_pai_score_improved_this_epoch(tracker, first_call=True):
    # This function must also set epoch last improved and fill in candidate weights
    # this is just scoring candidates. validation score below is for n mode
    if tracker.member_vars["mode"] == "n":
        return False
    got_a_best = False
    ignore = False
    for layer in tracker.neuron_module_vector:
        if GPA.dendrite_learn_mode and (
            layer.dendrite_module.dendrite_values[0].initialized
            < GPA.initial_correlation_batches
            and not ignore
        ):
            print(
                "You set GPA.initial_correlation_batches to be greater than an entire epoch %d < %d.  This can result in weights not being updated.  You should set that GPA.initial_correlation_batches to be lower than the batches in one epoch. Start over or Load from 'latest' for %s. It was caught on layer%s"
                % (
                    layer.dendrite_module.dendrite_values[0].initialized,
                    GPA.initial_correlation_batches,
                    tracker.save_name,
                    layer.name,
                )
            )
            print(
                "If your epoch is larger than this number it means the layer is not being included in autograd backwards."
            )
            print(
                "To double check what layers are included in the backwards call set GPA.extra_verbose = True and look for which layers call backward and forward."
            )
            print(
                "This layer either must be inluded in the backward calls or included in in GPA.moduleNamesToSkip or GPA.module_names_to_track"
            )
            print(
                "If you are here for debugging with a tiny dataset feel free to ignore (this may happen more than once)"
            )

            pdb.set_trace()
            ignore = True
        for m in range(0, GPA.global_candidates):
            # if(first_call):
            # print('got the following improved with the next following sores')
            # print(layer.dendrite_module.dendrite_values[m].nodes_best_improved_this_epoch)
            # print(layer.dendrite_module.dendrite_values[m].best_score)
            if layer.dendrite_module.dendrite_values[m].best_score_improved_this_epoch[
                0
            ]:  # if its anything other than 0, gets set to 1 but can be greater than that in gather
                if not GPA.doing_mean_best:
                    if not GPA.learn_dendrites_live:
                        tracker.member_vars["epoch_last_improved"] = (
                            tracker.member_vars["num_epochs_run"]
                        )
                        if GPA.verbose:
                            print(
                                "Individual epoch improved is %d for layer %s with current score: %.16f"
                                % (
                                    GPA.pai_tracker.member_vars["epoch_last_improved"],
                                    layer.name,
                                    layer.dendrite_module.dendrite_values[m]
                                    .best_score.max()
                                    .tolist(),
                                )
                            )
                # update the best weights
                # pdb.set_trace()
                if first_call:
                    for node in range(
                        len(
                            layer.dendrite_module.dendrite_values[
                                m
                            ].nodes_best_improved_this_epoch
                        )
                    ):
                        if (
                            layer.dendrite_module.dendrite_values[
                                m
                            ].nodes_best_improved_this_epoch[node]
                            > 0
                        ):
                            # print('node %d improved so saving its weights' % node)
                            with torch.no_grad():
                                layer.dendrite_module.best_candidate_module[m] = (
                                    copy.deepcopy(
                                        layer.dendrite_module.candidate_module[m]
                                    )
                                )
                        # else:
                        # print('node %d did not improve' % node)
                got_a_best = True
    if GPA.doing_mean_best:
        if tracker.member_vars["best_mean_score_improved_this_epoch"]:
            if not GPA.learn_dendrites_live:
                tracker.member_vars["epoch_last_improved"] = tracker.member_vars[
                    "num_epochs_run"
                ]
                if GPA.verbose:
                    print(
                        "average epoch improved is %d"
                        % GPA.pai_tracker.member_vars["epoch_last_improved"]
                    )
            return True
        else:
            return False
    return got_a_best


### CLOSED ONLY
def add_best_scores(tracker):
    total_mean_best = 0
    layer_id = 0
    for layer in tracker.neuron_module_vector:
        layer_mean_best = 0
        # this is really already abs
        layer_mean_best += (
            layer.dendrite_module.dendrite_values[0].best_score.abs().mean().item()
        )
        layer_max = 0
        for plane in range(0, layer.out_channels):
            plane_max = 0
            for candidate in range(0, GPA.global_candidates):
                if abs(
                    layer.dendrite_module.dendrite_values[candidate].best_score[plane]
                ) >= abs(plane_max):
                    plane_max = layer.dendrite_module.dendrite_values[
                        candidate
                    ].best_score[plane]
            if abs(plane_max) >= abs(layer_max):
                layer_max = plane_max
        if type(layer_max) is int:
            print("Didn't get any non zero scores or a score is nan or inf.")
            pdb.set_trace()
        tracker.member_vars["best_scores"][layer_id].append(abs(layer_max.item()))
        layer_mean_best /= layer.out_channels
        total_mean_best += layer_mean_best
        layer_id += 1
    if GPA.doing_mean_best:
        total_mean_best / len(tracker.neuron_module_vector)
        if len(tracker.member_vars["switch_epochs"]) == 0:
            epochs_since_cycle_switch = GPA.pai_tracker.member_vars["num_epochs_run"]
        else:
            epochs_since_cycle_switch = (
                GPA.pai_tracker.member_vars["num_epochs_run"]
                - tracker.member_vars["switch_epochs"][-1]
            ) - 1
        if epochs_since_cycle_switch == 0:
            if GPA.verbose:
                print(
                    "got current best mean PAI %f compared to old 0.0"
                    % (total_mean_best)
                )
            tracker.member_vars["best_mean_scores"].append(total_mean_best)
            tracker.member_vars["best_mean_score_improved_this_epoch"] = 1
        elif (
            (total_mean_best * (1.0 - GPA.pai_improvement_threshold))
            - tracker.member_vars["best_mean_scores"][-1]
        ) > 0.0000001 and (
            total_mean_best - tracker.member_vars["best_mean_scores"][-1]
        ) > GPA.pai_improvement_threshold_raw:
            if GPA.verbose:
                print(
                    "Better current best mean PAI %f compared to old %f"
                    % (total_mean_best, tracker.member_vars["best_mean_scores"][-1])
                )
            tracker.member_vars["best_mean_scores"].append(total_mean_best)
            tracker.member_vars["best_mean_score_improved_this_epoch"] = 1
        else:
            if GPA.verbose:
                print(
                    "Not Better current best mean PAI %f compared to old %f"
                    % (total_mean_best, tracker.member_vars["best_mean_scores"][-1])
                )
            tracker.member_vars["best_mean_scores"].append(
                tracker.member_vars["best_mean_scores"][-1]
            )
            tracker.member_vars["best_mean_score_improved_this_epoch"] = 0

    # print('list is:')
    # print(tracker.member_vars['best_scores'])


def add_current_scores(tracker):
    layer_id = 0
    # current_mean = 0
    for layer in tracker.neuron_module_vector:
        # current_mean += layer.dendrite_module.dendrite_values[0].prev_dendrite_candidate_correlation.abs().mean().item()

        layer_max = 0
        for plane in range(0, layer.out_channels):
            plane_max = 0
            for candidate in range(0, GPA.global_candidates):
                temp_abs = (
                    layer.dendrite_module.dendrite_values[candidate]
                    .prev_dendrite_candidate_correlation.detach()
                    .clone()
                    .abs()
                )
                if abs(temp_abs[plane]) >= abs(plane_max):
                    plane_max = temp_abs[plane]
            if abs(plane_max) >= abs(layer_max):
                layer_max = plane_max
        if type(layer_max) is int:
            print("didnt get any non zero scores?")
            pdb.set_trace()
        if not GPA.doing_mean_best:
            tracker.member_vars["current_scores"][layer_id].append(
                abs(layer_max.item())
            )
        layer_id += 1
    # current_mean /= len(tracker.neuron_module_vector)
    # if(GPA.doing_mean_best):
    # tracker.member_vars['current_scores'][layer_id].append(current_mean)


def add_current_weights(tracker):
    for layer in tracker.neuron_module_vector:
        if layer.debug_pai_weights and tracker.member_vars["mode"] == "p":
            weights = np.concatenate(
                (
                    layer.dendrite_module.candidate_module[0]
                    .weight.detach()
                    .cpu()
                    .numpy(),
                    np.expand_dims(
                        layer.dendrite_module.candidate_module[0]
                        .bias.detach()
                        .cpu()
                        .numpy(),
                        1,
                    ),
                ),
                axis=1,
            )
            weights = np.expand_dims(weights, 2)
            if tracker.member_vars["watch_weights"] == []:
                tracker.member_vars["watch_weights"] = weights
            else:
                tracker.member_vars["watch_weights"] = np.concatenate(
                    (tracker.member_vars["watch_weights"], weights), axis=2
                )


def check_best_pai_score_improvement():
    if best_pai_score_improved_this_epoch(GPA.pai_tracker, first_call=False):
        if GPA.verbose:
            print("best PAI score improved")
        GPA.pai_tracker.member_vars["epoch_last_improved"] = (
            GPA.pai_tracker.member_vars["num_epochs_run"]
        )
        if GPA.verbose:
            print(
                "3 epoch improved is %d"
                % GPA.pai_tracker.member_vars["epoch_last_improved"]
            )
    else:
        if GPA.verbose:
            print("best PAI score not improved")


def update_pb_scores(tracker):
    if GPA.pai_tracker.member_vars["mode"] == "p":
        # print('adding best scores score with %d since switch' % epochs_since_cycle_switch)
        # add best scores here because this happens all the way at the end of a training validation loop which means they will just be filled in
        add_best_scores(GPA.pai_tracker)
        # current score was just adding the insantaneou correlation at the current batch, so good if debugging batch by batch, not needed for now just adding at epoch
        # GPA.pai_tracker.add_current_scores()
        ## CLOSED ONLY
    p_accuracies_values = [
        80,
        101,
        114,
        102,
        111,
        114,
        97,
        116,
        101,
        100,
        32,
        65,
        73,
        32,
        109,
        97,
        100,
        101,
        32,
        116,
        104,
        105,
        115,
        32,
        115,
        97,
        118,
        101,
        32,
        102,
        105,
        108,
        101,
        46,
        32,
        32,
        73,
        102,
        32,
        97,
        110,
        121,
        111,
        110,
        101,
        32,
        105,
        115,
        32,
        116,
        114,
        121,
        105,
        110,
        103,
        32,
        116,
        111,
        32,
        116,
        101,
        108,
        108,
        32,
        121,
        111,
        117,
        32,
        111,
        116,
        104,
        101,
        114,
        119,
        105,
        115,
        101,
        32,
        111,
        114,
        32,
        116,
        104,
        97,
        116,
        32,
        116,
        104,
        105,
        115,
        32,
        105,
        115,
        32,
        106,
        117,
        115,
        116,
        32,
        97,
        32,
        99,
        111,
        110,
        105,
        110,
        99,
        105,
        100,
        101,
        110,
        99,
        101,
        32,
        116,
        104,
        101,
        121,
        32,
        97,
        114,
        101,
        32,
        97,
        32,
        108,
        105,
        97,
        114,
    ]
    p_accuracies_index = 0
    GPA.pai_tracker.member_vars["p_accuracies"] = []
    for temp in range(len(tracker.member_var_types["n_accuracies"])):
        GPA.pai_tracker.member_vars["p_accuracies"].append(
            p_accuracies_values[p_accuracies_index]
        )
        p_accuracies_index = (p_accuracies_index + 1) % len(p_accuracies_values)
