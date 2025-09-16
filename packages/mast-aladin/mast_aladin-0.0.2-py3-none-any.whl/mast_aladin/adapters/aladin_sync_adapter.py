from IPython.display import display
from mast_aladin.app import gca

from .viewer_sync_adapter import ViewerSyncAdapter


class AladinSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        self.viewer = viewer if viewer else gca()
        self.aid = self.viewer.aid

    def sync_to(self, sync_viewer):
        self.aid.set_viewport(
            **sync_viewer.aid.get_viewport(sky_or_pixel="sky")
        )

    def add_callback(self, func):
        self.viewer.observe(func, names=["_fov", "_target", "_rotation"])

    def remove_callback(self, func):
        self.viewer.unobserve(func, names=["_fov", "_target", "_rotation"])

    def show(self):
        display(self.viewer)
