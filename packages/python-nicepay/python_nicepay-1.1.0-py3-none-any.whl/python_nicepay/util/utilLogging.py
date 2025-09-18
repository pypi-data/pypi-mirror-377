import logging


class Log:
    logging.basicConfig(format='%(asctime)s [PY-NICEPAY] - %(message)s',
                        filemode='w')
    LOGGER = logging.getLogger()
    MAGENTA = "\u001B[35m"
    BLUE = "\u001B[34m"
    YELLOW = "\u001B[33m"
    GREEN = "\u001B[32m"
    RED = "\u001B[31m"
    RESET = "\u001B[0m"
    LOGGER.setLevel(logging.DEBUG)

    def headers(self, logging):
        self.LOGGER.info(f"{self.YELLOW}{logging}{self.RESET}")

    def body(self, logging):
        self.LOGGER.info(f"{self.BLUE}{logging}{self.RESET}")

    def response(self, logging):
        self.LOGGER.info(f"{self.MAGENTA}{logging}{self.RESET}")

    def info(self, logging):
        self.LOGGER.info(f"{self.GREEN}{logging}{self.RESET}")

    def error(self, logging):
        self.LOGGER.error(f"{self.RED}{logging}{self.RESET}")

# log = LoggerPrint()
# log.logInfo("HANTU KESOREAN")
