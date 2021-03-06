from pydantic import Field

from openpype.settings import BaseSettingsModel


class ListPerPlatform(BaseSettingsModel):
    windows: list[str] = Field(default_factory=list)
    linux: list[str] = Field(default_factory=list)
    darwin: list[str] = Field(default_factory=list)


class AppVariant(BaseSettingsModel):
    name: str
    label: str | None = None
    executables: ListPerPlatform = Field(
        default_factory=ListPerPlatform, title="Executables"
    )
    arguments: ListPerPlatform = Field(
        default_factory=ListPerPlatform, title="Arguments"
    )
    environment: str = Field("{}", title="Environment", widget="textarea")


class AppVariantWithPython(AppVariant):
    usePython2: bool = Field(False, title="Use Python 2")


class AppGroup(BaseSettingsModel):
    enabled: bool = Field(default=True)
    hostName: str | None
    icon: str | None
    environment: str = Field("{}", title="Environment", widget="textarea")

    variants: list[AppVariant] = Field(
        default_factory=list,
        title="Variants",
        description="Different variants of the applications",
        section="Variants",
    )


class AppGroupWithPython(AppGroup):
    variants: list[AppVariantWithPython] = Field(
        default_factory=list,
        title="Variants",
        description="Different variants of the applications",
        section="Variants",
    )


class ApplicationSettings(BaseSettingsModel):
    """Applications settings"""

    maya: AppGroupWithPython = Field(..., title="Autodesk Maya")
    flame: AppGroupWithPython = Field(..., title="Autodesk Flame")
    nuke: AppGroupWithPython = Field(..., title="Nuke")
    aftereffects: AppGroup = Field(..., title="Adobe After Effects")
    photoshop: AppGroup = Field(..., title="Adobe Photoshop")
    tvpaint: AppGroup = Field(..., title="TV Paint")
    harmony: AppGroup = Field(..., title="Harmony")
    additional_apps: AppGroup = Field(..., title="Additional Applications")
