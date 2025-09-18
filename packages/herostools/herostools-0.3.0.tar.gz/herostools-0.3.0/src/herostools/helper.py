import logging


##############################################################
# extend logging mechanism
SPAM = 5
setattr(logging, "SPAM", 5)
logging.addLevelName(levelName="SPAM", level=5)


class Logger(logging.Logger):
    def setLevel(self, level, globally=False):
        if isinstance(level, str):
            level = level.upper()
        try:
            level = int(level)
        except ValueError:
            pass
        logging.Logger.setLevel(self, level)
        if globally:
            for name, logger in logging.root.manager.loggerDict.items():
                if not hasattr(logger, "setLevel"):
                    continue
                logger.setLevel(level)

    def spam(self, msg, *args, **kwargs):
        self.log(SPAM, msg, *args, **kwargs)


logging.setLoggerClass(Logger)
format = "%(asctime)-15s %(name)s: %(message)s"
logging.basicConfig(format=format)

log = logging.getLogger("herostools")
