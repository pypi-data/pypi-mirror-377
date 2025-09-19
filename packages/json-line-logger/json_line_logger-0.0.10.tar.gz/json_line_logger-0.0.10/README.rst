################
Json Line Logger
################
|TestStatus| |PyPiStatus| |BlackStyle| |BlackPackStyle| |MITLicenseBadge|


Uses python's awesome logging-library and configures it to write JSON-lines.
In JSON-lines, each line in the log is a valid json-object.
This makes the log easy to read with a machine.


*******
install
*******

.. code-block::

    pip install json-line-logger


*****
usage
*****

There are three handy constructors for loggers: ``LoggerFile``,
``LoggerStream``, and ``LoggerStdout``.

.. code-block:: python

    import json_line_logger

    logger = json_line_logger.LoggerFile(path="test.log.jsonl")

    logger.debug("This is a log message")

    with json_line_logger.TimeDelta(logger=logger, name="some costly task"):
        result_of_a_costly_task = 1 + 1

    json_line_logger.shutdown(logger=logger)


Yields a logfile ``test.log.jsonl`` which contains:

.. code-block::

    {"t":"1886-03-27T11:01:01.341", "l":"DEBUG", "m":"This is a log message"}
    {"t":"1886-03-27T11:01:01.341", "l":"INFO", "m":"<TimeDelta name='some costly task' delta='2.1457672119140625e-06'/>"}


.. |TestStatus| image:: https://github.com/cherenkov-plenoscope/json_line_logger/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/cherenkov-plenoscope/json_line_logger/actions/workflows/test.yml

.. |PyPiStatus| image:: https://img.shields.io/pypi/v/json_line_logger
    :target: https://pypi.org/project/json_line_logger

.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |BlackPackStyle| image:: https://img.shields.io/badge/pack%20style-black-000000.svg
    :target: https://github.com/cherenkov-plenoscope/black_pack

.. |MITLicenseBadge| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
