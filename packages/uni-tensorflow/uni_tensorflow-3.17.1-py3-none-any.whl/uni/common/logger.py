# -------------------------------------------------------------------------------
# (c) Copyright 2022 Sony Semiconductor Israel, Ltd. All rights reserved.
#
#      This software, in source or object form (the "Software"), is the
#      property of Sony Semiconductor Israel Ltd. (the "Company") and/or its
#      licensors, which have all right, title and interest therein, You
#      may use the Software only in  accordance with the terms of written
#      license agreement between you and the Company (the "License").
#      Except as expressly stated in the License, the Company grants no
#      licenses by implication, estoppel, or otherwise. If you are not
#      aware of or do not agree to the License terms, you may not use,
#      copy or modify the Software. You may use the source code of the
#      Software only for your internal purposes and may not distribute the
#      source code of the Software, any part thereof, or any derivative work
#      thereof, to any third party, except pursuant to the Company's prior
#      written consent.
#      The Software is the confidential information of the Company.
# -------------------------------------------------------------------------------
"""
Created on 6/30/22

@author: irenab
"""
import logging
import os
import sys
import json
from enum import Enum
from typing import Optional, NamedTuple
import time
"""
1. Output json/text -> JsonFormatter/TextFormatter
2. Inject static context info -> ContextFilter
3. Add message_code: mandatory for WARNING/ERROR, optional for lower severity -> CustomLoggerAdapter.
   Refer to CustomLoggerAdapter for exact log method signatures

   Filter and Formatter are applied to the root logger, so any logging will conform (that's why Filter is used even
   though a context can be easily handled directly by LoggerAdapter).

   Using LoggerAdapter inside our project enables us to modify log methods signatures, without worrying about
   handling logging from dependency code.
   LoggerAdapter is a wrapper around Logger and it does not affect the default Logger hierarchy and management
   in any way, unlike custom Loggers, so its usage is much more convenient.

   Usage:
   in each module requiring logging

   from uni.commion.logger import get_logger, MessageCodes
   logger = get_logger(__name__)

   log.error(msg, message_code=MessageCodes.X)  # ok
   log.debug(msg)  # ok
   log.error(msg)  # error
"""


def get_logger(name) -> 'CustomLoggerAdapter':
    logger = logging.getLogger(name)
    return CustomLoggerAdapter(logger, {})


def setup_uni_logging(logger_name: str,
                      logger_level: 'SDSPLoggerLevel',
                      logger_format: 'LoggerFormat',
                      context: str,
                      component: str,
                      component_suffix: Optional[str] = None):
    level = _sdsp_level_to_python_logging[logger_level]
    if level is not None:
        component_name = f'{component}-{component_suffix}' if component_suffix else component
        ctx = ContextInfo(logger=logger_name, context=context, component_type=component, component_name=component_name)
        _set_logging(level, ctx, logger_format)


class MessageCodes(Enum):
    UNSUPPORTED_OPS = 'USOP'
    INVALID_OPS = 'INVOP'
    EXECUTION = 'EXEC'
    QUANTIZATION = 'QUANT'
    INVALID_MODEL = 'INVMOD'


class LoggerFormat(str, Enum):
    JSON = 'json'
    TEXT = 'text'

    @classmethod
    def values(cls):
        return [v.value for v in cls]


class ContextInfo(NamedTuple):
    logger: str
    context: str
    component_type: str
    component_name: str


class SDSPLoggerLevel(str, Enum):
    # values are level strings defined for all conv tools
    TRACE = 'trace'
    DEBUG = 'debug'
    INFO = 'info'
    WARN = 'warn'
    ERROR = 'error'
    OFF = 'off'

    @classmethod
    def values(cls):
        return [v.value for v in cls]


# keys are the sdsp logger level options
_sdsp_level_to_python_logging = {
    SDSPLoggerLevel.TRACE: logging.DEBUG,
    SDSPLoggerLevel.DEBUG: logging.DEBUG,
    SDSPLoggerLevel.INFO: logging.INFO,
    SDSPLoggerLevel.WARN: logging.WARNING,
    SDSPLoggerLevel.ERROR: logging.ERROR,
    SDSPLoggerLevel.OFF: None,
}

# sdsp level strings to appear in json
_logging_level_to_sdsp_str = {
    logging.DEBUG: 'DEBUG',
    logging.INFO: 'INFO',
    logging.WARNING: 'WARN',
    logging.ERROR: 'ERROR',
    logging.CRITICAL: 'ERROR',
}


def _set_logging(level, context: ContextInfo, output_format: LoggerFormat):
    handler = _set_handler(level, output_format, context)
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)


def _set_handler(level, output_format: LoggerFormat, context: ContextInfo):
    """ Creates stdout Stream handler with context filter and appropriate formatter """
    formatters = {
        LoggerFormat.JSON: JsonFormatter,
        LoggerFormat.TEXT: TextFormatter,
    }
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = formatters[output_format]()
    handler.setFormatter(formatter)
    handler.addFilter(ContextFilter(context))
    return handler


class ContextFilter(logging.Filter):
    """ Filter that injects contextual information into log record """

    def __init__(self, context: ContextInfo):
        super().__init__()
        self.context = context

    def filter(self, record: logging.LogRecord):
        record.context = self.context
        return True


class CustomLoggerAdapter(logging.LoggerAdapter):
    """ CustomLogger is used to properly define new custom params.
        Otherwise, it should be passed as 'extra' dict in each log method call.
        In order to enforce mandatory custom params, it should not replace the default logger,
        since 3rd party libraries might use the application log config.

        uni-converter modules should use get_logger method defined here instead of logging.getLogger
    """

    def debug(self, *args, message_code: Optional[MessageCodes] = None, **kwargs):    # type: ignore
        super().debug(*args, **self._update_kwargs(kwargs, message_code))

    def info(self, *args, message_code: Optional[MessageCodes] = None, **kwargs):    # type: ignore
        super().info(*args, **self._update_kwargs(kwargs, message_code))

    def warning(self, *args, message_code: MessageCodes, **kwargs):    # type: ignore
        super().warning(*args, **self._update_kwargs(kwargs, message_code))

    def error(self, *args, message_code: MessageCodes, **kwargs):    # type: ignore
        super().error(*args, **self._update_kwargs(kwargs, message_code))

    def critical(self, *args, message_code: MessageCodes, **kwargs):    # type: ignore
        super().critical(*args, **self._update_kwargs(kwargs, message_code))

    def exception(self, *args, message_code: MessageCodes, **kwargs):    # type: ignore
        super().exception(*args, **self._update_kwargs(kwargs, message_code))

    def process(self, msg, kwargs):
        # update instead of overriding as in default implementation
        kwargs["extra"].update(self.extra)
        return msg, kwargs

    @staticmethod
    def _update_kwargs(kwargs, message_code):
        extra = kwargs.get('extra', {})
        if isinstance(message_code, MessageCodes):
            message_code = message_code.value
        extra.update({'message_code': message_code})
        kwargs['extra'] = extra
        return kwargs


class TextFormatter(logging.Formatter):
    TEXT_FORMAT = '%(asctime)s %(levelname)s : %(message)s [%(pathname)s:%(lineno)d]'

    def __init__(self):
        super().__init__(self.TEXT_FORMAT)

    def format(self, record: logging.LogRecord):
        try:
            msg_code = record.message_code    # type: ignore
        except AttributeError:    # pragma: no cover
            msg_code = None

        if msg_code:
            record.msg = f'CODE: [{record.message_code}] {record.msg}'    # type: ignore
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """ Generate json entry in ECS format (https://www.elastic.co/guide/en/ecs/current/ecs-reference.html)
        per https://app.clickup.com/t/860puwj34 """

    ECS_VERSION = '1.2.0'
    LINE_FEED = '<br>'    # replaces \n

    converter = time.gmtime
    DATEFMT = '%Y-%m-%d %H:%M:%S UTC'

    def __init__(self):
        super().__init__(datefmt=self.DATEFMT)

    def format(self, record: logging.LogRecord):
        try:
            msg_code = record.message_code    # type: ignore
        except AttributeError:    # pragma: no cover
            msg_code = None

        record.message = record.getMessage().replace('\n', self.LINE_FEED)
        record.asctime = self.formatTime(record, self.datefmt)
        record_json = {
            '@timestamp': record.asctime,
            'ecs.version': self.ECS_VERSION,
            'process.thread.name': record.threadName,
            'log.level': _logging_level_to_sdsp_str[record.levelno],
            'message': record.message,
            'log.logger': record.context.logger,    # type: ignore
            'component.name': record.context.component_name,    # type: ignore
            'component.type': record.context.component_type,    # type: ignore
            'context': record.context.context,    # type: ignore
            'message.code': msg_code,
        }
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)    # pragma: no cover

            record_json['error.type'] = record.exc_info[0].__name__ if record.exc_info[0] else 'unknown'
            record_json['error.message'] = record.exc_info[1].args[0] if record.exc_info[1] else 'unknown'
            if record.exc_text:
                record_json['error.stack_trace'] = record.exc_text.replace('\n', self.LINE_FEED)

        return json.dumps(record_json)


def trace_method(func):
    """ Debug decorator for tracing arguments passed at each invocation of the decorated function
        Activated by 'TRACE' env variable """
    from functools import wraps

    @wraps(func)
    def f(*args, **kwargs):
        if os.getenv('TRACE'):    # pragma: no cover
            passed_args = map(str, args[1:] + tuple([f'{k}={v}' for k, v in kwargs.items()]))
            logging.getLogger('tracer').debug(
                f'{args[0].__class__.__name__}::{func.__name__}({", ".join(passed_args)})')
        return func(*args, **kwargs)

    return f
