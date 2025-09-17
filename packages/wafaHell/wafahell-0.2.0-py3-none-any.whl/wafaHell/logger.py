import logging

class Logger:
    def __init__(self, name="WAF", log_file="waf.log", level=logging.INFO):
        # Cria logger com nome
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Evita handlers duplicados ao reinicializar
        if not self.logger.handlers:
            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # Handler para arquivo
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)

            # Formato
            formatter = logging.Formatter(
                "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S - %d/%m/%Y"
            )

            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            # Adiciona handlers
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def debug(self, msg):
        self.logger.debug(msg)
