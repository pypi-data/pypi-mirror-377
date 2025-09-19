from gunicorn import glogging


class GunicornLogger(glogging.Logger):
    """Custom logger for Gunicorn log messages."""

    def setup(self, cfg):
        """Configure Gunicorn application logging configuration."""
        super().setup(cfg)
        # fix annoying gunicorn wanting to implement its own logging
        self.error_log.propagate = True
        self.access_log.propagate = True
        [self.error_log.removeHandler(handler) for handler in self.error_log.handlers]
        [self.error_log.removeHandler(handler) for handler in self.access_log.handlers]
