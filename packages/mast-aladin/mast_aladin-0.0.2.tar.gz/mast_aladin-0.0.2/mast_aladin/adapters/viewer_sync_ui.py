import ipywidgets as widgets
from IPython.display import display

from mast_aladin.adapters import ImvizSyncAdapter, AladinSyncAdapter, SyncManager


class ViewerSyncUI():
    def __init__(self):

        self.mast_aladin = AladinSyncAdapter()
        self.imviz = ImvizSyncAdapter()
        self.sync_manager = SyncManager()

        self.buttons = widgets.ToggleButtons(
            options=['None', 'Imviz', 'Mast Aladin'],
            disabled=False,
            button_style='',
            tooltips=['No Syncing', 'Sync to Imviz', 'Sync to Mast Aladin'],
            style=widgets.ToggleButtonsStyle(button_width="33.1%")
        )

        self.buttons.observe(self._handle_sync, names="value")

    def _handle_sync(self, change):
        match change["new"]:
            case "None":
                self.sync_manager.stop_real_time_sync()
            case "Imviz":
                self.sync_manager.start_real_time_sync(
                    source=self.imviz,
                    destination=self.mast_aladin
                )
            case "Mast Aladin":
                self.sync_manager.start_real_time_sync(
                    source=self.mast_aladin,
                    destination=self.imviz
                )

    def display(self):
        self.imviz.show()
        display(self.buttons)
        self.mast_aladin.show()
