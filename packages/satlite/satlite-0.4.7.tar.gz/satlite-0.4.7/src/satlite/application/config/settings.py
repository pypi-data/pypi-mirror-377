import binascii
import os
from dataclasses import field
from pathlib import Path
from typing import Final

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class ModuleMeta:
    """Metadata for a module."""

    name: str
    version: str
    summary: str
    base_dir: Path


def get_module_meta(module_name: str) -> ModuleMeta:
    """Get the metadata of a module."""
    from importlib.metadata import metadata

    from litestar.utils.module_loader import module_to_os_path

    BASE_DIR: Final[Path] = module_to_os_path(module_name)
    meta = metadata(module_name)

    return ModuleMeta(
        name=meta.get('name', module_name),
        version=meta.get('version', '0.0.0'),
        summary=meta.get('summary', ''),
        base_dir=BASE_DIR,
    )


@dataclass
class Csrf:
    """Configuration for **CSRF** (**C**ross **S**ite **R**equest **F**orgery) protection."""

    secret: str = field(default=binascii.hexlify(os.urandom(32)).decode(encoding='utf-8'))
    '''A string that is used to create an HMAC to sign the CSRF token.'''

    cookie_name: str = field(default='csrftoken')
    '''The CSRF cookie name.'''

    cookie_path: str = field(default='/')
    '''The CSRF cookie path.'''

    header_name: str = field(default='x-csrftoken')
    '''The header that will be expected in each request.'''

    cookie_secure: bool = field(default=False)
    '''A boolean value indicating whether to set the Secure attribute on the cookie.'''

    cookie_httponly: bool = field(default=False)
    '''A boolean value indicating whether to set the `HttpOnly` attribute on the cookie.'''

    cookie_domain: str | None = field(default=None)
    '''The value to set in the `SameSite` attribute of the cookie.'''

    exclude: str | list[str] | None = field(default=None)
    '''Specifies which hosts can receive the cookie.'''

    exclude_from_csrf_key: str = field(default='exclude_from_csrf')
    '''A set of “safe methods” that can set the cookie.'''

    cookie_samesite: str = field(default='lax')  # "lax", "strict", "none"
    '''A pattern or list of patterns to skip in the CSRF middleware.'''

    safe_methods: set[str] = field(default_factory=lambda: {'GET', 'HEAD', 'OPTIONS'})
    '''An identifier to use on routes to disable CSRF for a particular route.'''


@dataclass
class Cors:
    """Configuration for **CORS** (**C**ross-**O**rigin **R**esource **S**haring)."""

    allowed_origins: list[str] = field(default_factory=lambda: ['*'])
    '''
    List of origins that are allowed. Can use `*` in any component of the path, e.g. `domain.*`.
    Sets the `Access-Control-Allow-Origin` header.
    '''

    allow_methods: list[str] = field(default_factory=lambda: ['*'])
    '''List of allowed HTTP methods. Sets the `Access-Control-Allow-Methods` header.'''

    allow_headers: list[str] = field(default_factory=lambda: ['*'])
    '''List of allowed headers. Sets the `Access-Control-Allow-Headers` header.'''

    allow_credentials: bool = field(default=False)
    '''Boolean dictating whether or not to set the `Access-Control-Allow-Credentials` header.'''

    allow_origin_regex: str | None = field(default=None)
    '''Regex to match origins against.'''

    expose_headers: list[str] = field(default_factory=list)
    '''List of headers that are exposed via the `Access-Control-Expose-Headers` header.'''

    max_age: int = field(default=600)
    '''Response caching TTL in secs, defaults: 600. Sets the `Access-Control-Max-Age` header.'''


@dataclass
class Api:
    cache_expiration: int = field(default=60)
    '''Default cache expiration in secs, when a route handler is configured with `cache=True`.'''

    csrf: Csrf = field(default_factory=Csrf)
    '''Configuration for **CSRF** (**C**ross **S**ite **R**equest **F**orgery) protection.'''

    cors: Cors = field(default_factory=Cors)
    '''Configuration for **CORS** (**C**ross-**O**rigin **R**esource **S**haring).'''


@dataclass
class Server:
    name: str = field(default='satlite')
    '''The name of the HTTP server.'''

    host: str = field(default='127.0.0.1')
    '''The host to bind the Granian server to.'''

    port: int = Field(default=8080, gt=0, le=65535)
    '''The port to bind the Granian server to.'''


@dataclass
class App:
    name: str = field(default='satlite')
    '''The name of the application.'''

    slug: str = field(default='satlite')
    '''A slug for the application (a short, URL-friendly version of the name).'''

    version: str = field(default='0.0.1')
    '''The version of the application.'''

    debug: bool = field(default=False)
    '''A boolean indicating whether to run the application in debug mode.'''

    enable_structlog: bool = field(default=False)
    '''A boolean indicating whether to enable structlog logging.'''


@dataclass
class Vite:
    """Configuration for ViteJS support."""

    asset_url: str = field(default='/static/')
    '''Base URL to generate for static asset references.
    This URL will be prepended to anything generated from Vite.
    '''

    build_command: list[str] = field(default_factory=lambda: ['bun', 'run', 'build'])
    '''Default command to use for building with Vite.'''

    build_watch_command: list[str] = field(default_factory=lambda: ['bun', 'run', 'watch'])
    '''Default command to use for dev building with Vite.'''

    bundle_dir: Path = field(default=Path('web/public'))
    '''Location of the compiled assets from  Vite. The manifest file will also be found here.'''

    detect_nodeenv: bool = field(default=True)
    '''When True, The initializer will install and configure nodeenv if present'''

    dev_mode: bool = field(default=False)
    '''When True, Vite will run with HMR or watch build'''

    host: str = field(default='localhost')
    '''Default host to use for Vite server.'''

    hot_file: str = 'hot'
    '''Name of the hot file.
    This file contains a single line containing the host, protocol, and port the Vite server is
    running.
    '''

    hot_reload: bool = field(default=True)
    '''Enable HMR for Vite development server.'''

    install_command: list[str] = field(default_factory=lambda: ['bun', 'install'])
    '''Default command to use for installing dependencies.'''

    is_react: bool = field(default=True)
    '''Enable React components.'''

    manifest_name: str = field(default='manifest.json')
    '''Name of the manifest file.'''

    port: int = field(default=5173)
    '''Name of the hot file.
    This file contains a single line containing the host, protocol, and port the Vite server is
    running.
    '''

    protocol: str = field(default='http')
    '''Protocol to use for communication'''

    public_dir: Path = field(default=Path('public'))
    '''The optional public directory Vite serves assets from.
    In a standalone Vue or React application, this would be equivalent to the `./public` directory.
    '''

    resource_dir: Path = field(default=Path('resources'))
    '''The directory where all typescript/javascript source are written.
    In a standalone Vue or React application, this would be equivalent to the `./src` directory.
    '''

    root_dir: Path | None = field(default=None)
    '''The base path to your application.
    In a standalone Vue or React application, this would be equivalent to the top-level project
    folder containing the `./src` directory.
    '''

    run_command: list[str] = field(default_factory=lambda: ['bun', 'run', 'dev'])
    '''Default command to use for running Vite.'''

    set_environment: bool = field(default=True)
    '''When True, configuration in this class will be set into environment variables.

    This can be useful to ensure Vite always uses the configuration supplied to the plugin
    '''

    set_static_folders: bool = field(default=True)
    '''When True, Litestar will automatically serve assets at the `ASSET_URL` path.'''

    ssr_enabled: bool = field(default=False)
    '''Enable SSR.'''

    ssr_output_dir: Path | None = field(default=None)
    '''SSR Output path'''

    template_dir: Path = field(default=Path('web/templates'))
    '''The directory jinja templates are stored in.'''

    use_server_lifespan: bool = field(default=True)
    '''Utilize the server lifespan hook to run Vite.'''
