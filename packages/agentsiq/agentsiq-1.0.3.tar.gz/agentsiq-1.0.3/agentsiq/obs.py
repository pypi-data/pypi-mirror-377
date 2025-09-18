
import os, logging
from dotenv import load_dotenv
load_dotenv()
class SafeConsoleFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            enc = getattr(getattr(logging, 'stream', None), 'encoding', None) or os.environ.get('PYTHONIOENCODING') or 'cp1252'
            record.msg = str(record.getMessage()).encode(enc, errors='replace').decode(enc, errors='replace')
        except Exception:
            record.msg = str(record.msg).encode('ascii', errors='replace').decode('ascii', errors='replace')
        return True
def init_agentops():
    api_key = os.getenv("AGENTOPS_API_KEY")
    if not api_key: return False
    try:
        import agentops
        agentops.init(api_key)
        logger = logging.getLogger("agentops")
        logger.addFilter(SafeConsoleFilter())
        logging.getLogger().addFilter(SafeConsoleFilter())
        return True
    except Exception:
        return False
