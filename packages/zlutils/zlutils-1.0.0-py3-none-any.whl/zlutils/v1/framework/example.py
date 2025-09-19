# example
from zlutils.framework.ep.app import App


class MainApp(App):

    def on_running(self):
        self.plugin_manager.publishEvent('pmprint')


if __name__ == "__main__":

    plugin_dir = 'Plugins'  # default
    config_path = 'config.ini'
    mainapp = MainApp(plugin_dir=plugin_dir, config_path=config_path)
    print('lifecycle_states',mainapp.lifecycle_states)
    mainapp.run()
