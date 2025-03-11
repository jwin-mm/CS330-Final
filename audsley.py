#!/usr/bin/env python

"""
audsley.py - suite for scheduling/feasibility functions according to Audsley's
original paper.
"""

import json
import sys

from taskset import *

def audsleyFeasibility(taskSet):
    """
    Returns True if the given taskSet is schedulable under Audsley's optimal
    fixed-priority assignment, else False.
    """
    result = []
    for j in range(len(taskSet), 0, -1): # priority level j
        unassigned = True
        for task in taskSet:
            if isFeasible(task, j):
                result.append(task)
                taskSet.remove(task)
                unassigned = False 
        if (unassigned):
            return False
    
    return True


def isFeasible(task, priority):
    """
    Returns True if a given task can feasibly be scheduled at the given priority,
    else false.
    """
    # CA + I A <= DA
    if (task.wcet + calInterference(task) <= task.relativeDeadline):
        return True
    return False


def calInterference(task):
    """
    Calculates the total interference, which is the sum of "remaining"
    interference and "created" interference, as defind in the original paper.
    """
    return calRemainingInterference() + calCreatedInterference()


def calRemainingInterference(task, timeInstant):
    """
    The remaining interference on a release of t_i at time t, due to higher priority tasks
    that have not completed their execution at t.
    """
    tupleSet = [()] #TODO
    time = timeInstant - task.period + task.relativeDeadline
    totalRInterference = 0
    for (tupleWCET, tupleTime) in tupleSet:
        if (tupleTime > time + totalRInterference):
            totalRInterference = 0
        time = tupleTime
        totalRInterference += tupleWCET
    totalRInterference = totalRInterference - (timeInstant - tupleTime)
    if (totalRInterference < 0):
        totalRInterference = 0
    return totalRInterference


def calCreatedInterference(task):
    """
    The created interference on a release of t_i at time t, due to higher priority tasks
    released in the interval [t, t + D_i),
    """