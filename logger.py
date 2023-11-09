from loguru import logger as logging


logging.add("logs/logs.log",
            rotation="500 MB",
            backtrace=True,
            diagnose=True,
            format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | <level>{function}</level> : <level>{message}</level>",
            colorize=False  # Включаем цветовую разметку
            )
logging.opt(colors=True)
