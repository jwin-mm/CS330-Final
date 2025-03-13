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

    This function assigns the lowest priority first and progressively assigns tasks
    to higher priorities while checking feasibility.

    Args:
        taskSet: A list of tasks, each containing attributes:
                 - wcet (C_i)
                 - relativeDeadline (D_i)
                 - period (T_i)
                 - offset (O_i)  # (if relevant)
    
    Returns:
        True if the taskSet is schedulable, False otherwise.
    """

    remainingTasks = taskSet.copy()  # Create a mutable copy
    assignedTasks = []  # Ordered list of assigned tasks

    # Assign priorities from lowest to highest
    for j in range(len(taskSet), 0, -1):  
        unassigned = True  # The current priority level starts unassigned

        for candidate in remainingTasks:
            interferingTasks = [t for t in remainingTasks if t is not candidate]

            # Check feasibility over the entire feasibility interval
            feasible = True
            releaseTime = 0
            while (releaseTime < candidate.period):
            # for releaseTime in range(0, candidate.period, candidate.period):
                if not isFeasible(candidate, interferingTasks, releaseTime):
                    feasible = False
                    break
                releaseTime += candidate.period

            if feasible:  
                assignedTasks.append(candidate)
                remainingTasks.remove(candidate)
                unassigned = False  
                break  # Move to the next priority level

        if unassigned:
            return False  # If no task is feasible at this priority, the set is not schedulable

    return True  # All tasks were assigned feasible priorities


def isFeasibleRTA(task, interferingTasks):
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

def isFeasible(task, interferingTasks, timeInstant):
    """
    Determines whether a given task can feasibly be scheduled at a given priority.
    
    A task is feasible if:
        C_A + I_A ≤ D_A
    
    where:
        - C_A: Execution time of the task.
        - I_A: Total interference from higher-priority tasks.
        - D_A: Relative deadline of the task.

    Args:
        task: The task for which feasibility is being checked.
        interferingTasks: A list of higher-priority tasks that may interfere.
        timeInstant: The time instant at which feasibility is being assessed.

    Returns:
        True if the task is feasible, False otherwise.
    """
    totalInterference = calcInterference(task, timeInstant, interferingTasks)
    
    return task.wcet + totalInterference <= task.relativeDeadline



def calcInterference(task, timeInstant, higherPriorityTasks):
    """
    Calculates the total interference, which is the sum of "remaining"
    interference and "created" interference, as defined in the original paper.
    
    Args:
        task: The task for which interference is being calculated.
        timeInstant: The specific time instant at which interference is being assessed.
        higherPriorityTasks: A list of higher-priority tasks that may contribute to interference.

    Returns:
        Total interference value at the given time instant.
    """
    return calcRemainingInterference(task, timeInstant, higherPriorityTasks) + \
           calcCreatedInterference(task, timeInstant, higherPriorityTasks)


def calcRemainingInterference(task, timeInstant, higherPriorityTasks):
    """
    Computes the remaining interference at a given time instant.
    
    Args:
        task: The task for which interference is being calculated.
        timeInstant: The specific time instant at which remaining interference is being assessed.
        higherPriorityTasks: A list of higher-priority tasks.

    Returns:
        Remaining interference at the given time instant.
    """
    tupleSet = []  # This will hold (execution_time, release_time) tuples for uncompleted tasks

    # Define the initial time range
    time = timeInstant - task.period + task.relativeDeadline
    totalRInterference = 0

    # Populate tupleSet with execution demands of higher priority tasks that haven't completed
    for hpTask in higherPriorityTasks:
        releaseTime = 0
        while (releaseTime < timeInstant):
        # for releaseTime in range(0, timeInstant, hpTask.period):
            if releaseTime + hpTask.wcet > timeInstant:
                tupleSet.append((hpTask.wcet, releaseTime))
            releaseTime += hpTask.period

    # Sort tuple set based on release times
    tupleSet.sort(key=lambda x: x[1])

    if tupleSet:  # Only subtract if tupleSet is non-empty
         # Compute remaining interference
        for (tupleWCET, tupleTime) in tupleSet:
            if tupleTime > time + totalRInterference:
                totalRInterference = 0  # Reset if there's an idle period
            time = tupleTime
            totalRInterference += tupleWCET
        totalRInterference -= (timeInstant - tupleTime)
    else:
        totalRInterference = 0  # If no interference, ensure it remains 0


   

    return max(totalRInterference, 0)  # Ensure non-negative interference


def calcCreatedInterference(task, timeInstant, higherPriorityTasks):
    """
    Computes the created interference at a given time instant.

    Args:
        task: The task for which interference is being calculated.
        timeInstant: The specific time instant at which created interference is being assessed.
        higherPriorityTasks: A list of higher-priority tasks.

    Returns:
        Created interference at the given time instant.
    """
    tupleSet = []  # This will hold (execution_time, release_time) tuples for new task releases

    # Calculate interference caused by higher priority tasks released in [t, t + D_i)
    for hpTask in higherPriorityTasks:
        releaseTime = 0
        while (releaseTime < timeInstant + task.relativeDeadline):
        # for releaseTime in range(timeInstant, timeInstant + task.relativeDeadline, hpTask.period):
            tupleSet.append((hpTask.wcet, releaseTime))
            releaseTime += hpTask.period

    # Sort tuple set based on release times
    tupleSet.sort(key=lambda x: x[1])

    # Compute created interference
    totalCreatedInterference = 0
    nextFreeTime = timeInstant
    for (execTime, releaseTime) in tupleSet:
        if nextFreeTime < releaseTime:
            nextFreeTime = releaseTime  # Adjust free time to the new task's release
        totalCreatedInterference += min(timeInstant + task.relativeDeadline - nextFreeTime, execTime)
        nextFreeTime += execTime

    return totalCreatedInterference
