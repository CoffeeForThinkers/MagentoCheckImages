import logging
import datetime

__version__ = '0.1.4'

_LOGGER = logging.getLogger(__name__)


class Progress(object):
    """Produce the calculated/estimated progress output based on averages."""

    def __init__(self, total_count, min_display_interval_s, 
                 context='<flat>', history_size=10):
        now = datetime.datetime.now()

        self.__history_size = history_size
        self.__total_count = total_count
        self.__last_progress = 0.0
        self.__last_timestamp = now
        self.__progress_interval_s = min_display_interval_s
        self.__started_at_timestamp = now
        self.__time_deltas = []
        self.__progress_deltas = []
        self.__i = 0
        self.__context = context

    def tick(self):
        now = datetime.datetime.now()
        time_since_last_s = (now - self.__last_timestamp).total_seconds() 
        if time_since_last_s < self.__progress_interval_s:
            self.__i += 1
            return

        # Calculate the amount of progress that we'll expect to make before the 
        # next time.

        current_progress = float(self.__i + 1) / float(self.__total_count) * 100.0
        progress_delta = current_progress - self.__last_progress

        self.__progress_deltas.append(progress_delta)
        len_ = len(self.__progress_deltas)
        if len_ > self.__history_size:
            del self.__progress_deltas[0]
            len_ -= 1

        average_progress_delta = \
            float(sum(self.__progress_deltas)) / float(len_)

        # Calculate the amount of time that we'll expect to have to wait until 
        # the next tick.

        self.__time_deltas.append(float(time_since_last_s))
        len_ = len(self.__time_deltas)
        if len_ > self.__history_size:
            del self.__time_deltas[0]
            len_ -= 1

        average_time_delta = \
            float(sum(self.__time_deltas)) / float(len_)

        # How many percentage until done =>
        #   How many times does the percentage-points-change-
        #   since-last divide into it.
        #       Multiplied by time for that particular interval
        time_until_done_s = \
            (100.0 - current_progress) / \
                average_progress_delta * \
                    average_time_delta

        r = self.__split_seconds(time_until_done_s)
        (self.__hours, self.__minutes, self.__seconds) = r

        self.__last_progress = current_progress
        self.__last_timestamp = now

        self.print_progress()

        self.__i += 1

    def __split_seconds(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds - hours * 3600) // 60
        seconds = total_seconds - hours * 3600 - minutes * 60

        return (hours, minutes, seconds)

    def __str__(self):
        if self.__i == 0:
            return "[%s] Progress: (none)" % (self.__context)
        else:
            time_since_started_s = \
                (datetime.datetime.now() - self.__started_at_timestamp).total_seconds()

            r = self.__split_seconds(time_since_started_s)
            (running_hours, running_minutes, running_seconds) = r

            return "[%s] Progress: %.1f%% (DONE IN [%02d:%02d:%02d] RUNNING "\
                   "FOR [%02d:%02d:%02d])" % (
                    self.__context, self.__last_progress, self.__hours, 
                    self.__minutes, self.__seconds, running_hours, 
                    running_minutes, running_seconds)

    def print_progress(self):
        print(self)
