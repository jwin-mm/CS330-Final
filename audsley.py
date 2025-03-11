#!/usr/bin/env python

"""
fifo.py - First-In First-Out scheduler

FifoScheduler: scheduling algorithm that executes FIFO (non-preemptive)
FifoPriorityQueue: priority queue that prioritizes by release time
"""

import json
import sys

from taskset import *
from scheduleralgorithm import *
from schedule import ScheduleInterval, Schedule
from display import SchedulingDisplay

#############################################################
# FifoScheduler class                                       #
#############################################################

class FifoScheduler(SchedulerAlgorithm):
    def __init__(self, taskSet):
        SchedulerAlgorithm.__init__(self, taskSet)

    def buildSchedule(self, startTime, endTime):
        self._buildPriorityQueue(FifoPriorityQueue)

        time = startTime
        self.schedule.startTime = time

        previousJob = None
        didPreemptPrevious = False # should stay false due to FIFO

        # Loop until the priority queue is empty, executing jobs non-preemptively in FIFO order
        while not self.priorityQueue.isEmpty():
            # Make a scheduling decision resulting in an interval
            interval, newJob = self._makeSchedulingDecision(time, previousJob)

            nextTime = interval.startTime
            didPreemptPrevious = interval.didPreemptPrevious # should be False for FIFO

            if didPreemptPrevious:
                print("ERROR!  FIFO is meant to be non-preemptive!")
                return None

            # If the previous interval wasn't idle, execute the previous job to completion
            # until the start of the new interval
            if previousJob is not None:
                previousJob.executeToCompletion()

            # Add the interval to the schedule
            self.schedule.addInterval(interval)

            # Update the time and job
            time = nextTime
            previousJob = newJob

        # If there is still a previous job, complete it and update the time
        if previousJob is not None:
            time += previousJob.remainingTime
            previousJob.executeToCompletion()

        # Add the final idle interval
        finalInterval = ScheduleInterval()
        finalInterval.initialize(time, None, False)
        self.schedule.addInterval(finalInterval)

        # Post-process the intervals to set the end time and whether the job completed
        latestDeadline = max([job.deadline for job in self.taskSet.jobs])
        endTime = max(time + 1.0, latestDeadline, float(endTime))
        self.schedule.postProcessIntervals(endTime)

        return self.schedule

    def _makeSchedulingDecision(self, t, previousJob):
        """
        Makes a scheduling decision after time t.  Assumes there is at least one job
        left in the priority queue.

        t: the beginning of the previous time interval, if one exists (or 0 otherwise)
        previousJob: the job that was previously executing, and will either complete or be preempted

        returns: (ScheduleInterval instance, Job instance of next job to execute)
        """

        # Make a scheduling decision at the next scheduling time point after time t.
        # Let's call this new time nextTime.

        # If there was no previous job executing, the next job will come from the priority
        # queue at or after time t.
        if (previousJob == None): 
            nextJob = self.priorityQueue.popNextJob(t)
            nextTime = nextJob.releaseTime

        # If there was a previous job executing, choose the highest-priority job from the
        # priority queue at nextTime.
        # Note that if there was a previous job but when it finishes, no more jobs are ready
        # (released prior to that time), then there should be no job associated with the new
        # interval.  The ScheduleInterval.initialize method will handle this, you just have
        # to provide it with None rather than a job.
        if (previousJob):
            nextTime = t + previousJob.remainingTime
            nextJob = self.priorityQueue.popFirst(nextTime)

        # Once you have the next job to execute (if any), build the interval (which starts at
        # nextTime) and return it and the next job.
        interval = ScheduleInterval()
        interval.initialize(nextTime, nextJob, False)
        
        return interval, nextJob 

#############################################################
# FifoPriorityQueue class                                   #
#############################################################
    
class FifoPriorityQueue(PriorityQueue):
    def __init__(self, jobReleaseDict):
        """
        Creates a priority queue of jobs ordered by release time.
        """
        PriorityQueue.__init__(self, jobReleaseDict)

    def _sortQueue(self):
        # FIFO orders by release time
        self.jobs.sort(key = lambda x: (x.releaseTime, x.task.id))

    def _findFirst(self, t):
        """
        Returns the index of the highest-priority job released at or before t,
        or -1 if the queue is empty or if all remaining jobs are released after t.
        """
        if self.isEmpty():
            return -1

        if self.jobs[0].releaseTime > t:
            return -1

        return 0

    def popNextJob(self, t):
        """
        Removes and returns the highest-priority job of those released at or after t,
        or None if no jobs are released at or after t.
        """
        if not self.isEmpty() and self.jobs[0].releaseTime >= t:
            return self.jobs.pop(0)
        else:
            return None

    def popPreemptingJob(self, t, job):
        """
        Removes and returns the job that will preempt job 'job' after time 't', or None
        if no such preemption will occur (i.e., if no higher-priority jobs
        are released before job 'job' will finish executing).

        t: the time after which a preemption may occur
        job: the job that is executing at time 't', and which may be preempted
        """
        return None

#############################################################
# When this file is run, try it out with a given file       #
# (or with the default of p1_test1.json)                    #
#############################################################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "tasksets/p1_test1.json"

    with open(file_path) as json_data:
        data = json.load(json_data)

    taskSet = TaskSet(data)

    taskSet.printTasks()
    taskSet.printJobs()

    scheduleStartTime = float(data[TaskSetJsonKeys.KEY_SCHEDULE_START])
    scheduleEndTime = float(data[TaskSetJsonKeys.KEY_SCHEDULE_END])

    fifo = FifoScheduler(taskSet)
    schedule = fifo.buildSchedule(scheduleStartTime, scheduleEndTime)

    schedule.printIntervals(displayIdle=True)

    print("\n// Validating the schedule:")
    schedule.checkWcets()
    schedule.checkFeasibility()

    display = SchedulingDisplay(width=800, height=480, fps=33, scheduleData=schedule)
    display.run()