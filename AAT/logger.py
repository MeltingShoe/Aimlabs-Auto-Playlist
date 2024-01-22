import logging
import inspect
import functools
import os
import datetime
import yaml
import time
import ast


class timeAccumulator:
    def __init__(self):
        self.accTime = 0
        self.startTime = None

    def start(self):
        self.time = time.perf_counter()

    def stop(self):
        elapsed = time.perf_counter()-self.time
        self.accTime += elapsed

    def readTime(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.start()
            result = func(*args, **kwargs)
            self.stop()
            return result

        return wrapper


def format_list_as_table(row):
    formatted_string = "| " + " | ".join(map(str, row)) + " |\n"
    return formatted_string


def padNum(num):
    if not isinstance(num, (float, int)):
        raise ValueError("Input must be a float or an int")

    formatted_num = "{:07.4f}".format(float(num))
    return formatted_num


def format_nested_list(nested_list):
    formatted_list = []

    for sublist in nested_list:
        formatted_sublist = []

        for element in sublist:
            formatted_sublist.append(padNum(element))

        formatted_list.append(formatted_sublist)

    return formatted_list


def isMatrix(input_list):
    if not isinstance(input_list, list):
        return False

    if not all(isinstance(sublist, list) for sublist in input_list):
        return False

    if not input_list:
        # Empty list is considered valid
        return True

    length_of_first_sublist = len(input_list[0])

    return all(len(sublist) == length_of_first_sublist for sublist in input_list[1:])


def processMatrix(input_matrix):
    if not isMatrix(input_matrix):
        raise ValueError("Input is not a valid matrix")

    formatted_nested_list = format_nested_list(input_matrix)

    # Applying format_list_as_table to every sublist and concatenating the results
    formatted_table = ''.join(format_list_as_table(sublist)
                              for sublist in formatted_nested_list)

    return formatted_table


class Logger:
    def __init__(self):
        self.acc = timeAccumulator()

        config = self.loadConfig()
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
        self.level_name = {'1': 'DEBUG',
                           '2': 'INFO',
                           '3': 'WARNING',
                           '4': 'ERROR',
                           '5': 'CRITICAL'
                           }

    def outputAcc(self):
        self.logMsg(5, msg=self.acc.accTime)

    def loadConfig(self):
        path = os.path.abspath(os.path.join(
            os.getcwd(), os.pardir, 'config', 'devConfig.yaml'))
        with open(path, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def _get_caller_info(self):
        # Get information about the caller (file, line, function)
        # Adjusted to consider the frame outside the wrapper
        self.acc.start()
        frame = inspect.currentframe()
        frame = frame.f_back
        frame = frame.f_back
        frame = frame.f_back
        line_number = frame.f_lineno
        function_name = frame.f_code.co_name
        file_name = os.path.basename(frame.f_globals['__file__'])
        self.acc.stop()

        return f"{file_name}:{line_number} - {function_name}"

    def logMsg(self, level, msg=None):
        if (self.prints == False) and (self.logs == False):
            return False
        callerInfo = self._get_caller_info()
        if isMatrix(msg):
            processed_msg = processMatrix(msg)

            logMsg = f"{self.level_name[str(level)]} - {callerInfo} - {processed_msg}"
        else:
            logMsg = f"{self.level_name[str(level)]} - {callerInfo} - {msg}" if msg else f"{callerInfo}"

        if self.prints and level >= self.printLevel:
            print(logMsg)

        if self.logs and level >= self.logLevel:
            with open(self.log_file_path, 'a') as logfile:
                logfile.write(logMsg + '\n')

        return True


logger_instance = Logger()
path = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, 'config//modelConfig', 'config.yaml'))
with open(path, "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


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

            start = time.perf_counter()
            # Call the wrapped function
            result = inner_func(*args, **kwargs)
            end = time.perf_counter()
            elapsed = end - start
            entry_exit_level = 4 if elapsed > config[
                'errorTime'] else 3 if elapsed > config['warningTime'] else entry_exit_level
            # Before
            # Log and print return value (args_return_level)
            return_msg = f"Return value: {result}"
            logger_instance.logMsg(args_return_level, return_msg)

            # Log function exit (entry_exit_level)
            exit_msg = f"Exiting {inner_func.__name__}.  Execution took {elapsed: 0.2f} seconds"
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
