"""
A simple json-line-logger
"""

from .version import __version__
import time
import logging
import sys
import io


DATEFMT_ISO8601 = "%Y-%m-%dT%H:%M:%S"
FMT = "{"
FMT += '"t":"%(asctime)s.%(msecs)03d"'
FMT += ", "
FMT += '"l":"%(levelname)s"'
FMT += ", "
FMT += '"m":"%(message)s"'
FMT += ", "
FMT += '"c":"%(pathname)s:%(funcName)s:%(lineno)s"'
FMT += "}"


def LoggerStdout(name="stdout"):
    return LoggerStream(stream=sys.stdout, name=name)


def LoggerStdout_if_logger_is_None(logger):
    if logger is None:
        return LoggerStdout()
    else:
        return logger


def LoggerStream(stream=sys.stdout, name="stream"):
    lggr = logging.Logger(name=name)
    fmtr = logging.Formatter(fmt=FMT, datefmt=DATEFMT_ISO8601)
    stha = logging.StreamHandler(stream)
    stha.setFormatter(fmtr)
    lggr.addHandler(stha)
    lggr.setLevel(logging.DEBUG)
    return lggr


def LoggerFile(path, name="file"):
    lggr = logging.Logger(name=name)
    file_handler = logging.FileHandler(filename=path, mode="w")
    fmtr = logging.Formatter(fmt=FMT, datefmt=DATEFMT_ISO8601)
    file_handler.setFormatter(fmtr)
    lggr.addHandler(file_handler)
    lggr.setLevel(logging.DEBUG)
    return lggr


def shutdown(logger):
    for fh in logger.handlers:
        fh.flush()
        fh.close()
        logger.removeHandler(fh)


class TimeDelta:
    def __init__(self, logger, name, level=logging.INFO):
        self.logger = logger
        self.name = name
        self.level = level

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop = time.time()
        self.logger.log(
            level=self.level,
            msg=xml(tagname="TimeDelta", name=self.name, delta=self.delta()),
        )

    def delta(self):
        return self.stop - self.start


def xml(tagname, **kwargs):
    buff = io.StringIO()
    buff.write("<{:s}".format(tagname))
    for key, value in kwargs.items():
        svalue = str(value)
        svalue = svalue.replace('"', ";")
        svalue = svalue.replace("'", ":")
        buff.write(" ")
        buff.write("{:s}='{:s}'".format(key, svalue))
    buff.write("/>")
    buff.seek(0)
    return buff.read()
