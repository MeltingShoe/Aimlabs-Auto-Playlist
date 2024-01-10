import logging
import inspect
import functools
from utils import openYAML
import os


class Logger:
    def __init__(self):
        config = openYAML('devConfig.yaml')
        self.prints = config['prints']
        self.printLevel = config['printLevel']
        self.logs = config['logs']
        self.logLevel = config['logLevel']
        self.blockTaskLaunch = config['blockTaskLaunch']
        self.confirmToRunBlockedFunctions = config['confirmToRunBlockedFunctions']
        # Define the log directory
        log_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # Set the log file path
        log_file_path = os.path.join(log_dir, 'logfile.txt')
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

    def printMsg(self, level, msg=None):
        if self.prints and level >= self.printLevel:

            log_msg = f"{self.level_name[str(level)]} - {self._get_caller_info()} - {msg}" if msg else f"{self._get_caller_info()}"
            print(log_msg)

    def logMsg(self, level, msg=None):
        if self.logs and level > self.logLevel:
            log_msg = f"{self.level_name[str(level)]} - {self._get_caller_info()} - {msg}" if msg else f"{self._get_caller_info()}"
            with open(self.log_file_path, 'a') as logfile:
                logfile.write(log_msg + '\n')


logger_instance = Logger()


def log(func=None, level=None):
    def decorator(inner_func):
        @functools.wraps(inner_func)
        def wrapper(*args, **kwargs):
            # Set the level for entry and exit messages
            entry_exit_level = level if level is not None else 2

            # Set the level for args, kwargs, and return value messages
            args_return_level = level if level is not None else 1

            # Log function entry (entry_exit_level)
            entry_msg_func = f"Entering {inner_func.__name__}"
            logger_instance.printMsg(entry_exit_level, entry_msg_func)
            logger_instance.logMsg(entry_exit_level, entry_msg_func)

            # Log function entry with arguments and keyword arguments (args_return_level)
            entry_msg_args = f"Args: {args}, kwargs: {kwargs}"
            logger_instance.printMsg(args_return_level, entry_msg_args)
            logger_instance.logMsg(args_return_level, entry_msg_args)

            # Call the wrapped function
            result = inner_func(*args, **kwargs)

            # Log and print return value (args_return_level)
            return_msg = f"Return value: {result}"
            logger_instance.printMsg(args_return_level, return_msg)
            logger_instance.logMsg(args_return_level, return_msg)

            # Log function exit (entry_exit_level)
            exit_msg = f"Exiting {inner_func.__name__}"
            logger_instance.printMsg(entry_exit_level, exit_msg)
            logger_instance.logMsg(entry_exit_level, exit_msg)

            return result

        return wrapper

    if func is not None:  # Handle case when decorator is used without arguments
        return decorator(func)
    return decorator


def logLevel(print_level=None, log_level=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Store current levels
            old_print_level = logger_instance.printLevel
            old_log_level = logger_instance.logLevel

            # Set new levels if provided
            if print_level is not None:
                logger_instance.printLevel = print_level
            if log_level is not None:
                logger_instance.logLevel = log_level

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
    # Send message to both printMsg and logMsg at level 1
    logger_instance.printMsg(1, msg)
    logger_instance.logMsg(1, msg)


def info(msg=None):
    # Send message to both printMsg and logMsg at level 2
    logger_instance.printMsg(2, msg)
    logger_instance.logMsg(2, msg)


def warning(msg=None):
    # Send message to both printMsg and logMsg at level 3
    logger_instance.printMsg(3, msg)
    logger_instance.logMsg(3, msg)


def error(msg=None):
    # Send message to both printMsg and logMsg at level 4
    logger_instance.printMsg(4, msg)
    logger_instance.logMsg(4, msg)


def critical(msg=None):
    # Send message to both printMsg and logMsg at level 5
    logger_instance.printMsg(5, msg)
    logger_instance.logMsg(5, msg)
