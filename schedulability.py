#!/usr/bin/env python

"""
schedulability.py - suite of schedulability tests
"""

from taskset import TaskSetJsonKeys, Task
from audsley import *

import matplotlib.pyplot as plt
import random

#############################################################
# Functions to choose utilization and periods               #
#############################################################

def getUniformValue(a, b):
    """
    Returns a value uniformly selected from the range [a,b].
    """
    return random.uniform(a,b)

# Per-task utilization functions
lightUtilFunc = lambda : getUniformValue(0.001, 0.01)
mediumLightUtilFunc = lambda : getUniformValue(0.01, 0.1)
mediumUtilFunc = lambda : getUniformValue(0.1, 0.4)

# periods are in milliseconds
shortPeriodFunc = lambda : getUniformValue(3, 33)
longPeriodFunc = lambda : getUniformValue(50, 250)
choicePeriodFunc = lambda : random.choice([250, 500, 750, 1000, 1500, 2000, 6000])

offsetFunc = lambda : getUniformValue(0, 10)

#############################################################
# Task set generation                                       #
#############################################################

def generateRandomTaskSet(targetUtil, utilFunc, periodFunc):
    """
    Generates a random task set with total utilization targetUtil.

    targetUtil: the utilization sum to have for the generated task set (a float)
    utilFunc: a function that takes no parameters, and returns a utilization (a float)
    periodFunc: a function that takes no parameters, and returns a period (a float)

    Returns: the generated task set as a list of Task objects (not the TaskSet type)
    """
    utilSum = 0

    # Generate tasks until the utilization target is met
    taskSet = []
    i = 0
    while utilSum < targetUtil:
        taskId = i+1

        util = utilFunc()
        if (util + utilSum > targetUtil):
            util = targetUtil - utilSum

        offset = offsetFunc()
        period = periodFunc()
        wcet = util * period
        relativeDeadline = getUniformValue(wcet, period)

        # Build a dictionary for the task parameters
        taskDict = {}
        taskDict[TaskSetJsonKeys.KEY_TASK_ID] = taskId
        taskDict[TaskSetJsonKeys.KEY_TASK_PERIOD] = period
        taskDict[TaskSetJsonKeys.KEY_TASK_WCET] = wcet
        taskDict[TaskSetJsonKeys.KEY_TASK_DEADLINE] = relativeDeadline
        taskDict[TaskSetJsonKeys.KEY_TASK_OFFSET] = offset

        task = Task(taskDict)
        taskSet.append(task)

        i += 1
        utilSum += util

    return taskSet

#############################################################
# Checking schedulability                                   #
#############################################################


def rmSchedulabilityTest(taskSet):
    """
    Performs an RTA schedulability test for RM, using the fixed-point
    iterative algorithm we learned in class.
    """

    for task in taskSet:
        interferingTasks = [] # Will hold tasks whose RM priority is higher than Task

        for t in taskSet:
            if t is not task and t.period<task.period:
                interferingTasks.append(t)
        
        R_prev = task.wcet
        while True:
            interference = sum(math.ceil(R_prev / t.period) * t.wcet for t in interferingTasks)
            R_next = task.wcet + interference
            
            if R_next == R_prev:
                break  # Fixed point reached
            if R_next > task.relativeDeadline:
                return False  # Task fails to meet its deadline
            R_prev = R_next
        
        if R_next > task.relativeDeadline:
            return False
    
    return True



def dmSchedulabilityTest(taskSet):
    """
    Performs an RTA schedulability test for DM, using the fixed-point
    iterative algorithm we learned in class.
    """

    for task in taskSet:
        interferingTasks = [] # Will hold tasks whose DM priority is higher than Task

        for t in taskSet:
            if t is not task and t.relativeDeadline<task.relativeDeadline:
                interferingTasks.append(t)
        
        R_prev = task.wcet
        while True:
            interference = sum(math.ceil(R_prev / t.period) * t.wcet for t in interferingTasks)
            R_next = task.wcet + interference
            
            if R_next == R_prev:
                break  # Fixed point reached
            if R_next > task.relativeDeadline:
                return False  # Task fails to meet its deadline
            R_prev = R_next
        
        if R_next > task.relativeDeadline:
            return False
    
    return True


def checkSchedulability(numTaskSets, targetUtilization, utilFunc, periodFunc, testFunc):
    """
    Generates numTaskSets task sets using a given utilization-generation function
    and a given period-generation function, such that the task sets have a given
    target system utilization.  Uses the given schedulability test to determine
    what fraction of the task sets are schedulable.

    Returns: the fraction of task sets that pass the schedulability test.
    """
    count = 0
    for i in range(numTaskSets):
        taskSet = generateRandomTaskSet(targetUtilization, utilFunc, periodFunc)

        if testFunc(taskSet):
            count += 1

    return count / numTaskSets



#############################################################
# Schedulability study                                      #
#############################################################

def performTests(numTests):
    utilizationVals = []
    for i in range(90):
        val = 0.01 + i * 0.01
        utilizationVals.append(val)

    results = {}
    results["rm"] = []
    results["dm"] = []
    results["audsley"] = []

    for util in utilizationVals:
        rmResult = checkSchedulability(numTests, util, mediumLightUtilFunc, shortPeriodFunc, rmSchedulabilityTest)
        dmResult = checkSchedulability(numTests, util, mediumLightUtilFunc, shortPeriodFunc, dmSchedulabilityTest)
        audsleyResult = checkSchedulability(numTests, util, mediumUtilFunc, shortPeriodFunc, audsleyFeasibility)

        results["rm"].append(rmResult)
        results["dm"].append(dmResult)
        results["audsley"].append(audsleyResult)

    return utilizationVals, results

#############################################################
# Generate a schedulability graph                           #
#############################################################

def plotResults(utilVals, results):
    plt.figure()

    LINE_STYLE = ['b:+', 'g-^', 'r-s']

    for (styleId, label) in enumerate(results):
        yvals = results[label]
        plt.plot(utilVals, yvals, LINE_STYLE[styleId], label=label, markersize=1)

        # print("Results for {0}: {1}".format(label, yvals))

    plt.legend(loc="best")

    plt.xlabel("System Utilization")
    plt.ylabel("RM Schedulability")
    plt.title("RM Schedulability for Different Utilization Distributions")

    plt.show()

#############################################################
# Main: run experiments and plot the results                #
#############################################################

def generateTasks():
    # First try with util = 0.5, medium-light-util tasks
    taskSet = generateRandomTaskSet(0.5, mediumLightUtilFunc, shortPeriodFunc)

    print("Task set with goal utilization of 0.5:")
    for task in taskSet:
        print(task)

    print(f"(total util: {sum([task.getUtilization() for task in taskSet])})")

    # Now, try with util = 1.4, medium-util tasks
    taskSet = generateRandomTaskSet(1.4, mediumUtilFunc, longPeriodFunc)

    print("\nTask set with goal utilization of 1.4:")
    for task in taskSet:
        print(task)
        
    print(f"(total util: {sum([task.getUtilization() for task in taskSet])})")

def testSchedulability():
    random.seed(None) # seed the random library

    # Perform the schedulability tests
    utilVals, results = performTests(1000) 

    # Plot the results
    plotResults(utilVals, results)

if __name__ == "__main__":
    # Test Part 1
    generateTasks()

    # Test Parts 2 and 3
    testSchedulability()
