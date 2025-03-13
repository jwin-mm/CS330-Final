#!/usr/bin/env python

"""
audsley.py - suite for scheduling/feasibility functions according to Audsley's
original paper.
"""

import math
from taskset import *

def audsleyFeasibility(taskSet):
    """
    Returns True if the given taskSet is schedulable under Audsley's optimal
    fixed-priority assignment, else False.
    """

    remainingTasks = taskSet.copy() # So we can safely remove tasks

    assignedTasks = []

    for j in range(len(taskSet), 0, -1): # priority level j
        unassigned = True # The current priority level begins unassigned
        for candidate in remainingTasks:
            interferingTasks = [t for t in remainingTasks if t is not candidate]
            # We need to assume all other remaining tasks have higher priority
            if isFeasible(candidate, interferingTasks):
                assignedTasks.append(candidate)
                remainingTasks.remove(candidate)
                unassigned = False 
        if (unassigned):
            return False
    
    return True

def isFeasible(task, interferingTasks):
    """
    Checks the feasibility of task, assuming that each task in interferingTasks
    has a higher priority than it. We use the iterative fixed-point RTA algorithm
    we learned in class to determine feasibility.
    """

    R_prev = task.wcet  # Start with the execution time of the candidate
    while True:
        interference = sum(math.ceil(R_prev / t.period) * t.wcet for t in interferingTasks)
        R_next = task.wcet + interference
        
        if R_next == R_prev:
            break  # Fixed point reached
        if R_next > task.relativeDeadline:
            return False  # Task fails to meet its deadline
        R_prev = R_next
    
    return R_next <= task.relativeDeadline

def isFeasible(task, interferingTasks):
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