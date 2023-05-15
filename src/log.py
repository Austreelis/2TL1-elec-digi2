from micropython import const

# Log levels
LOG_TRACE = const(0)
LOG_DEBUG = const(LOG_TRACE + 1)
LOG_INFO = const(LOG_DEBUG + 1)
LOG_WARN = const(LOG_INFO + 1)
LOG_ERROR = const(LOG_WARN + 1)
LOG_SILENT = const(LOG_ERROR + 1)


def noop(*args, **kwargs):
    """
    A function that does nothing, used to ignore logs of level lower than
    current log level.
    """
    pass

# Declare log functions to be used as globals
trace = noop
debug = noop
info = noop
warn = noop
error = noop

if __debug__:
    def make_log_fn(prefix: str):
        """
        Generates a logging function, taking the message to log as its single
        string argument.

        # Arguments

        - `prefix`: `str`, A string to add in front of each message.
        """
        def log(msg: str):
            print(prefix + msg)
        return log


    log_fn_trace = make_log_fn("[.] ")
    log_fn_debug = make_log_fn("[*] ")
    log_fn_info = make_log_fn("[=] ")
    log_fn_warn = make_log_fn("[!] ")
    log_fn_error = make_log_fn("[#] ")

    def set_log_level(level: int):
        """
        Set the current log level.

        Expects on of `LOG_DEBUG`, `LOG_INFO`, `LOG_WARN`, `LOG_ERROR`, or
        `LOG_SILENT`.
        """
        global LOG_TRACE
        global LOG_DEBUG
        global LOG_INFO
        global LOG_WARN
        global LOG_ERROR
        global LOG_SILENT
        global trace
        global debug
        global info
        global warn
        global error
        global log_fn_trace
        global log_fn_debug
        global log_fn_info
        global log_fn_warn
        global log_fn_error

        # Bound-check `level`
        if level < LOG_TRACE:
            log_fn_error(f"Invalid log level: {level} < LOG_TRACE = {LOG_TRACE}")
            machine.soft_reset()
        elif level > LOG_SILENT:
            log_fn_error(f"Invalid log level: {level} > LOG_SILENT = {LOG_SILENT}")
            machine.soft_reset()

        # Clear logging functions
        trace = noop
        debug = noop
        info = noop
        warn = noop
        error = noop

        # Set them back to the appropriate function
        # If level >= LOG_SILENT, none of these will branch in
        if level <= LOG_TRACE:
            trace = log_fn_trace
        if level <= LOG_DEBUG:
            debug = log_fn_debug
        if level <= LOG_INFO:
            info = log_fn_info
        if level <= LOG_WARN:
            warn = log_fn_warn
        if level <= LOG_ERROR:
            error = log_fn_error

        if level == LOG_TRACE:
            info("Log level set to: LOG_TRACE")
        elif level == LOG_DEBUG:
            info("Log level set to: LOG_DEBUG")
        elif level == LOG_INFO:
            info("Log level set to: LOG_INFO")

    # Set a default log level
    set_log_level(LOG_DEBUG)

