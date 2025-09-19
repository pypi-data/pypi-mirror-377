from .plugin import PluginManager
from .config import ConfigManager
# from .lifecycle import default_states


class App:

    def on_initialized(self):
        pass

    def on_configued(self):
        pass

    def on_started(self):
        pass

    def on_running(self):
        pass

    def on_stopping(self):
        pass

    def on_stopped(self):
        pass

    def __init__(
            self,
            plugin_dir='Plugins',
            config_path='config.ini',
            ):
        self.config_path = config_path
        self.plugin_dir = plugin_dir
        self.config = ConfigManager()
        self.config.loadINI(config_path)
        self.plugin_manager = PluginManager(plugin_dir, config=self.config)
        self.lifecycle_states = [
            'initialized', 'configued', 'started', 'running', 'stopping', 'stopped'
            ]
        pass

    @property
    def pm(self):  # 别名 plugin_manager
        return self.plugin_manager

    def run(self):
        for state in self.lifecycle_states:
            getattr(self, f'on_{state}')()
            self.plugin_manager.publishEvent(state)
