import logging.config
import os

from core.config import settings
from core.session import async_session


# check if logging.conf is exist use logging.conf else use '../logging.conf'
if os.path.exists('logging.conf'):
    log_file_config = 'logging.conf'
    logging.config.fileConfig(log_file_config, disable_existing_loggers=False)
elif settings.ENV == 'TEST':
    pass
else:
    raise FileNotFoundError('No logging configuration found')

logger = logging.getLogger(__name__)


async def get_db():
    async with async_session() as session:
        yield session
