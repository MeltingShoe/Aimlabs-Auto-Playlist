import logging
import inspect
import functools
from utils import openYAML, isMatrix, processMatrix
import os
import datetime


class Logger:
    def __init__(self):
        config = openYAML('devConfig.yaml')
        self.prints = config['prints']
        self.printLevel = config['printLevel']
        self.logs = config['logs']
        self.logLevel = config['logLevel']
        # Get the current time to include in the log file name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define the log directory
        log_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '..', 'logs')

        # Create the log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Set the log file path with the timestamp
        log_file_name = f"logfile_{timestamp}.txt"
        log_file_path = os.path.join(log_dir, log_file_name)
        self.log_file_path = log_file_path
        self.level_name = {
            '1': 'DEBUG',
            '2': 'INFO',
            '3': 'WARNING',
            '4': 'ERROR',
            '5': 'CRITICAL'
        }

    def _get_caller_info(self):
        # Get information about the caller (file, line, function)
        # Adjusted to consider the frame outside the wrapper
        frame_info = inspect.stack()[3]
        caller_frame = frame_info[0]
        file_name = os.path.basename(
            caller_frame.f_globals['__file__'])  # Changed this line
        line_number = frame_info[2]
        function_name = caller_frame.f_code.co_name

        return f"{file_name}:{line_number} - {function_name}"

    def logMsg(self, level, msg=None):
        if (self.prints == False) and (self.logs == False):
            return False

        if isMatrix(msg):
            processed_msg = processMatrix(msg)
            logMsg = f"{self.level_name[str(level)]} - {self._get_caller_info()} - {processed_msg}"
        else:
            logMsg = f"{self.level_name[str(level)]} - {self._get_caller_info()} - {msg}" if msg else f"{self._get_caller_info()}"

        if self.prints and level >= self.printLevel:
            print(logMsg)

        if self.logs and level >= self.logLevel:
            with open(self.log_file_path, 'a') as logfile:
                logfile.write(logMsg + '\n')

        return True


logger_instance = Logger()


def log(level_or_func=None):
    if callable(level_or_func):  # No level provided, only the function
        level = None
        func = level_or_func
    else:
        level = level_or_func
        func = None

    def decorator(inner_func):
        @functools.wraps(inner_func)
        def wrapper(*args, **kwargs):
            # Set the level for entry and exit messages
            entry_exit_level = level if level is not None else 2

            # Set the level for args, kwargs, and return value messages
            args_return_level = level if level is not None else 1

            # Log function entry (entry_exit_level)
            entry_msg_func = f"Entering {inner_func.__name__}"
            logger_instance.logMsg(entry_exit_level, entry_msg_func)

            # Log function entry with arguments and keyword arguments (args_return_level)
            entry_msg_args = f"Args: {args}, kwargs: {kwargs}"
            logger_instance.logMsg(args_return_level, entry_msg_args)

            # Call the wrapped function
            result = inner_func(*args, **kwargs)

            # Log and print return value (args_return_level)
            return_msg = f"Return value: {result}"
            logger_instance.logMsg(args_return_level, return_msg)

            # Log function exit (entry_exit_level)
            exit_msg = f"Exiting {inner_func.__name__}"
            logger_instance.logMsg(entry_exit_level, exit_msg)

            return result

        return wrapper

    # Handle the case when decorator is used without providing a level
    if func is not None:
        return decorator(func)
    return decorator


def logLevel(level):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Store current levels
            old_print_level = logger_instance.printLevel
            old_log_level = logger_instance.logLevel

            # Set new levels

            logger_instance.printLevel = level
            logger_instance.logLevel = level

            try:
                # Call the wrapped function
                result = func(*args, **kwargs)
                return result
            finally:
                # Restore original levels
                logger_instance.printLevel = old_print_level
                logger_instance.logLevel = old_log_level

        return wrapper

    return decorator


def debug(msg=None):
    # Send message to logMsg at level 1
    logger_instance.logMsg(1, msg)


def info(msg=None):
    # Send message to logMsg at level 2
    logger_instance.logMsg(2, msg)


def warning(msg=None):
    # Send message to logMsg at level 3
    logger_instance.logMsg(3, msg)


def error(msg=None):
    # Send message to logMsg at level 4
    logger_instance.logMsg(4, msg)


def critical(msg=None):
    # Send message to logMsg at level 5
    logger_instance.logMsg(5, msg)
