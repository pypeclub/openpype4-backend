from openpype.addons import BaseServerAddonVersion

from .settings import FtrackSettings


class AddOn(BaseServerAddonVersion):
    version = "1.0.0"
    settings = FtrackSettings