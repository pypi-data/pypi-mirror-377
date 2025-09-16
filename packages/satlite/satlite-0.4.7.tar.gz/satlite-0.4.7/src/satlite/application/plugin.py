from typing import Callable, Unpack

from litestar.config.app import AppConfig
from litestar.plugins import InitPluginProtocol

from .config.defaults import get_default_config
from .config.litestar import LitestarAppConfigDict
from .config.mime_types import set_mime_types
from .config.settings import Api as ApiSettings
from .config.settings import App as AppSettings
from .config.settings import Server as ServerSettings
from .config.settings import Vite as ViteSettings

# override mime types with correct ones
# (there's an issue in mimetypes python library, with some mime types in Windows)
set_mime_types()


def merge_configs(
    left: LitestarAppConfigDict, right: LitestarAppConfigDict
) -> LitestarAppConfigDict:
    """Merge two Litestar app config dictionaries."""
    merged = left.copy()
    for key, value in right.items():
        if key in merged and isinstance(merged[key], list) and isinstance(value, list):
            merged[key].extend(value)
        elif key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


class SatlitePlugin(InitPluginProtocol):
    litestar_config: LitestarAppConfigDict
    app_settings: AppSettings
    api_settings: ApiSettings
    server_settings: ServerSettings
    on_app_init_handlers: list[Callable[[AppConfig], AppConfig]]

    def __init__(
        self,
        *,
        app_settings: AppSettings = AppSettings(),
        api_settings: ApiSettings = ApiSettings(),
        server_settings: ServerSettings = ServerSettings(),
        vite_settings: ViteSettings | None = None,
        enable_csrf: bool = False,
        on_app_init: list[Callable[[AppConfig], AppConfig]] = [],
        **litestar_config: Unpack[LitestarAppConfigDict],
    ) -> None:
        self.app_settings = app_settings
        self.api_settings = api_settings
        self.server_settings = server_settings
        self.on_app_init_handlers = on_app_init

        default_cfg = get_default_config(
            app_settings, api_settings, server_settings, vite_settings, enable_csrf
        )
        self.litestar_config = merge_configs(default_cfg, litestar_config)

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        for key, value in self.litestar_config.items():
            if value is not None:
                current_value = getattr(app_config, key, None)
                if isinstance(current_value, list) and isinstance(value, list):
                    current_value.extend(value)
                elif isinstance(current_value, dict) and isinstance(value, dict):
                    current_value.update(value)
                else:
                    setattr(app_config, key, value)

        for func in self.on_app_init_handlers:
            app_config = func(app_config)
        return app_config
