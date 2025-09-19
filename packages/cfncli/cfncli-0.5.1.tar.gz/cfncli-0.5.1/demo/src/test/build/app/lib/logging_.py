from datetime import datetime
import json
import logging
from logging import Formatter
import traceback
import sys

AUDIT_LEVELV_NUM = 50

class JsonEncoderStrFallback(json.JSONEncoder):
  def default(self, obj):
    try:
      return super().default(obj)
    except TypeError as exc:
      if 'not JSON serializable' in str(exc):
        return str(obj)
      raise

class JsonEncoderDatetime(JsonEncoderStrFallback):
  def default(self, obj):
    if isinstance(obj, datetime):
      return obj.strftime('%Y-%m-%dT%H:%M:%S%z')
    else:
      return super().default(obj)

class CustomFormatter(Formatter):

    def __init__(self, request_id, audit_params):
        super(CustomFormatter, self).__init__()
        self.audit_params = audit_params
        self.request_id = request_id

    def format(self, record):
      log = {
        'level': record.levelname,
        'unixtime': record.created,
        'thread': record.thread,
        'location': '{}:{}:{}'.format(
          record.pathname or record.filename,
          record.funcName,
          record.lineno,
        ),
        'requestid': self.request_id,
        'exception': record.exc_info if record.exc_info else None,
        'traceback': traceback.format_exception(*record.exc_info) if record.exc_info else None,
        'message': record.getMessage()
      }
      if record.levelname == 'AUDIT':
        audit = self.audit_params
        audit.update({
          'AuditEventTimestamp': int(datetime.now().timestamp()),
          'UserIdentifier': record.__dict__.get('audit', {}).get('user', 'unknown'),
          'AuditEventType': record.__dict__.get('audit', {}).get('type', 'unknown'),
          'BusinessProcessIdentifier': record.__dict__.get('audit', {}).get('type', 'unknown'),
          'AuditEventSuccess': 'Y' if record.__dict__.get('audit', {}).get('code', 401) == 200 else 'N',
          'AuditEventResultCode': record.__dict__.get('audit', {}).get('code', 401),
          'UserAuditDetails':  record.__dict__.get('audit', {}).get('details', {})
        })
        log['audit'] = self.audit_params
      return json.dumps(log, cls=JsonEncoderDatetime)

def audit(self, message,  *args, **kws):
  self._log(AUDIT_LEVELV_NUM, message, args, **kws)

def setup(request_id, level=logging.INFO, audit_params={}):
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = CustomFormatter(request_id, audit_params)
    handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(level)
    logging.addLevelName(AUDIT_LEVELV_NUM, "AUDIT")
    logging.Logger.audit = audit
    return logger

