from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from itertools import product
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Self, Sequence
from urllib.parse import urlsplit, urlunsplit

import favicon
import requests

logger = logging.getLogger(__name__)


def _just_netloc(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))


@dataclass
class BaseModel:
    @classmethod
    def model_validate_json(cls, v: str) -> Self:
        return cls.model_validate(json.loads(v))

    @classmethod
    def model_validate(cls, v: Any) -> Self:
        match v:
            case dict():
                return cls(**v)
            case object() if isinstance(v, cls):
                return cls(**v.__dict__)
            case _:
                raise ValueError(f"Invalid {cls.__name__}: {v}")

    def model_dump(self, exclude_none: bool = False) -> dict[str, Any]:
        data = {}
        for k, _v in self.__dataclass_fields__.items():
            match getattr(self, k):
                case BaseModel() as v:
                    data[k] = v.model_dump()
                case list() | tuple() as v:
                    data[k] = [_.model_dump() for _ in v]
                case dict() as v:
                    data[k] = v
                case None if exclude_none:
                    continue
                case v:
                    data[k] = v

        return data

    def model_dump_json(self, indent: int = 2, exclude_none: bool = False) -> str:
        return json.dumps(self.model_dump(exclude_none=exclude_none), indent=indent)


@dataclass
class AwsAccount(BaseModel):
    id: str
    name: str
    services: Sequence[str] = ()
    role_names: Sequence[str] = ("AdministratorAccess",)

    @classmethod
    def model_validate_list(cls, v: Any) -> list[Self]:
        match v:
            case "null" | None:
                return []
            case str() if v.startswith("{") and v.endswith("}"):
                return [cls.model_validate_json(v)]
            case str() if v.startswith("[") and v.endswith("]"):
                return [cls.model_validate(_) for _ in json.loads(v)]
            case list() | tuple():
                return [cls.model_validate(_) for _ in v]
            case _:
                raise ValueError(f"Invalid AWS accounts: {v}")


def _env[R](key: str, default: R, cast: Callable[[str | R], R]) -> Callable[[], R]:
    def _() -> R:
        return cast(os.environ.get(key, default))

    return _


@dataclass
class Config(BaseModel):
    user: str = field(
        default_factory=_env("USER", "", str),
    )
    home: Path = field(
        default_factory=_env("HOME", Path.home(), Path),
    )
    src_dir: Path = field(
        default_factory=_env("SRC_DIR", Path.home() / "src", Path),
    )
    maxcare_src_dir: Path = field(
        default_factory=_env(
            "MAXCAREAI_SRC_DIR", Path.home() / "src" / "maxcare-ai", Path
        ),
    )
    icon_cache: Path = field(
        default_factory=_env(
            "ICON_CACHE", Path.home() / ".cache" / "alfred-icons", Path
        ),
    )
    cache_ttl: int = field(
        default_factory=_env("CACHE_TTL", 3600, int),
    )
    aws_domain: str = field(
        default_factory=_env("AWS_DOMAIN", "d-9067da16a7.awsapps.com", str),
    )
    aws_region: str = field(
        default_factory=_env("AWS_REGION", "us-west-2", str),
    )
    aws_accounts: list[AwsAccount] = field(
        default_factory=_env("AWS_ACCOUNTS", [], AwsAccount.model_validate_list),
    )
    buildkite_username: str = field(
        default_factory=_env("BUILDKITE_USERNAME", os.environ["USER"], str),
    )

    def __post_init__(self):
        self.aws_accounts = AwsAccount.model_validate_list(self.aws_accounts)


@dataclass
class MenuItem(BaseModel):
    """Pydantic model for Alfred menu items."""

    title: str
    subtitle: str = ""
    alt: str | dict[str, str] | None = None
    cmd: str | dict[str, str] | None = None
    arg: str = ""
    uid: str = ""
    match: str = ""
    autocomplete: str = ""

    icon: dict[str, str] | None = None

    def __post_init__(self):
        if isinstance(self.alt, str):
            self.alt = {"subtitle": self.alt}
        if isinstance(self.cmd, str):
            self.cmd = {"subtitle": self.cmd}


@dataclass
class MenuCache(BaseModel):
    """Pydantic model for Alfred menu cache settings."""

    seconds: int
    loosereload: bool = True


@dataclass
class AlfredMenu(BaseModel):
    """Pydantic model for the complete Alfred menu structure."""

    cache: MenuCache
    items: list[MenuItem] = field(default_factory=list)


@dataclass
class AlfredMaxcareWorkflow(BaseModel):
    """Alfred workflow generator for MaxCare."""

    config: Config
    cache_ttl: int = field(default=3600)
    home: Path = field(default_factory=Path.home)
    xdg_cache_home: Path = field(default_factory=lambda: Path.home() / ".cache")
    icon_cache: Path = field(
        default_factory=lambda: Path.home() / ".cache" / "alfred-icons"
    )
    menu_items: list[MenuItem] = field(default_factory=list)

    # SF Symbols glyphs mapping
    glyphs: dict[str, str] = field(
        default_factory=lambda: {
            "terminal": "􀩼",
            "terminal-fill": "􀪏",
            "bookmark": "􀉞",
            "path": "􀈕",
            "file": "􀈷",
            "maxcare": "􀴿",
            "sparkles": "􀆿",
            "monitor-sparkles": "􁅋",
            "monitor-sparkles-fill": "􁅌",
            "bubbles-sparkles": "􁒉",
            "bubbles-sparkles-fill": "􁒊",
            "cloud": "􀇂",
        }
    )

    def sfsymbol(self, symbol: str) -> Optional[str]:
        """Generate SF Pro icon files for given symbol."""
        icon_stem = self.xdg_cache_home / f"font-icons/sf-pro-{symbol}"
        dark_path = icon_stem.with_suffix(".png").with_name(
            f"{icon_stem.stem}-dark.png"
        )
        light_path = icon_stem.with_suffix(".png").with_name(
            f"{icon_stem.stem}-light.png"
        )

        if not dark_path.exists():
            dark_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                # Create dark icon
                subprocess.run(
                    [
                        "convert",
                        "-background",
                        "none",
                        "-fill",
                        "white",
                        "-font",
                        str(self.home / "Library/Fonts/SF-Pro.ttf"),
                        "-pointsize",
                        "300",
                        f"label:{symbol}",
                        str(dark_path),
                    ],
                    check=True,
                )
                # Create light icon
                subprocess.run(
                    [
                        "convert",
                        "-background",
                        "none",
                        "-fill",
                        "black",
                        "-font",
                        str(self.home / "Library/Fonts/SF-Pro.ttf"),
                        "-pointsize",
                        "300",
                        f"label:{symbol}",
                        str(light_path),
                    ],
                    check=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                return None

        return str(dark_path) if dark_path.exists() else None

    def generate_uid(self, title: str, subtitle: str, arg: str) -> str:
        """Generate unique ID for menu item."""
        content = f"{title} {subtitle} {arg}"
        return hashlib.sha256(content.encode()).hexdigest()

    def process_icon(
        self, icon_type: str, value: str, existing_icon: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, str]]:
        """Process different icon types and return icon dict."""
        if existing_icon and icon_type in ["appicon", "urlicon", "clearbiticon"]:
            return existing_icon

        match icon_type:
            case "icon" if "*" in value:
                if icon_path := next(Path().glob(value, case_sensitive=False), None):
                    return {"path": str(icon_path.absolute())}
                return None

            case "icon":
                return {"path": value}

            case "glyph":
                if value in self.glyphs:
                    icon_path = self.sfsymbol(self.glyphs[value])
                    return {"path": icon_path} if icon_path else None
                elif Path(value).exists():
                    return {"path": value}
                else:
                    print(
                        f"glyph: '{value}' does not exist",
                        file=__import__("sys").stderr,
                    )
                    return None

            case "filetype":
                return {"type": "filetype", "path": value}

            case "fileicon" | "utiicon":
                return {"type": "fileicon", "path": value}

            case "workflowicon":
                return {"path": f"./icons/{value}.png"}

            case "appicon":
                app_path = Path(
                    f"/Applications/{value}.app/Contents/Resources/{value}.icns"
                )
                icon_path = self.icon_cache / f"{value}.png"
                if icon_path.exists():
                    return {"path": str(icon_path)}
                elif app_path.exists():
                    icon_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        subprocess.run(
                            [
                                "sips",
                                "-s",
                                "format",
                                "png",
                                str(app_path),
                                "--out",
                                str(icon_path),
                            ],
                            check=True,
                        )
                        return {"path": str(icon_path)}
                    except subprocess.CalledProcessError:
                        return None

            case "clearbiticon":
                domain = value.split("://")[-1].split("/")[0].split(":")[0]
                icon_url = f"https://logo.clearbit.com/{domain}"
                icon_path = self.icon_cache / f"{domain}.png"
                return self._download_icon(icon_url, icon_path)

            case "urlicon":
                clean_url = value.replace("/", "_")
                icon_path = self.icon_cache / f"{clean_url}.png"
                return self._download_icon(value, icon_path)

            case "favicon":
                value_url = urlsplit(value)

                def _get_favicon() -> tuple[str, str]:
                    try:
                        icon = favicon.get(value)[0]
                    except Exception:
                        icon = favicon.get(urlunsplit(value_url._replace(path="")))[0]

                    return (icon.url, f"favicon.{icon.format}")

                return self._download_icon(
                    _get_favicon,
                    self.icon_cache / value_url.netloc / "favicon.*",
                )

        return None

    def _download_icon(
        self,
        url: str | Callable[[], str] | Callable[[], tuple[str, str]],
        icon_path: Path,
    ) -> Optional[Dict[str, str]]:
        """Download icon from URL."""
        if icon_path.suffix == ".*" and (
            new_icon_path := next(icon_path.parent.glob(icon_path.name), None)
        ):
            icon_path = new_icon_path

        if icon_path.exists() and icon_path.stat().st_size > 20:
            return {"path": str(icon_path)}

        if callable(url):
            match url():
                case str(url):
                    pass
                case (str(url), str(filename)):
                    icon_path = icon_path.with_name(filename)

        try:
            icon_path.parent.mkdir(parents=True, exist_ok=True)

            response = requests.get(
                url,
                timeout=2,
                stream=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
                },
            )
            response.raise_for_status()
            with open(icon_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            if icon_path.stat().st_size <= 20:
                icon_path.unlink()
                return None
            return {"path": str(icon_path)}
        except Exception:
            return None

    def add_item(
        self,
        item_type: str,
        *,
        title: str,
        subtitle: str | None = None,
        arg: str | None = None,
        url: str | None = None,
        command: str | None = None,
        path: str | None = None,
        # Icon options
        icon: str | None = None,
        glyph: str | None = None,
        appicon: str | None = None,
        clearbiticon: str | None = None,
        urlicon: str | None = None,
        favicon: str | None = None,
        workflowicon: str | None = None,
        filetype: str | None = None,
        fileicon: str | None = None,
        utiicon: str | None = None,
        # Additional options
        uid: str | None = None,
        match: str | None = None,
        autocomplete: str | None = None,
        **kwargs,
    ) -> None:
        """Add a menu item based on type using keyword arguments."""
        item_args = {"title": title}
        icon_dict = None

        match item_type:
            case "easy":
                if not subtitle or not arg:
                    raise ValueError(
                        "easy items require 'title', 'subtitle', and 'arg'"
                    )
                item_args.update({"subtitle": subtitle, "arg": arg})

            case "url":
                if not url:
                    raise ValueError("url items require 'title' and 'url'")
                item_args.update(
                    {
                        "subtitle": subtitle or f"open {title} in browser",
                        "arg": f"open {url}",
                    }
                )
                # Default to favicon if no icon specified
                if not (
                    icon
                    or glyph
                    or appicon
                    or clearbiticon
                    or urlicon
                    or workflowicon
                    or filetype
                    or fileicon
                    or utiicon
                ):
                    favicon = url

            case "exec":
                if not command:
                    raise ValueError("exec items require 'title' and 'command'")
                item_args.update(
                    {"subtitle": subtitle or command, "arg": f"zsh://{command}"}
                )
                # Default to terminal glyph if no glyph specified
                if not (
                    icon
                    or glyph
                    or appicon
                    or clearbiticon
                    or urlicon
                    or workflowicon
                    or filetype
                    or fileicon
                    or utiicon
                ):
                    glyph = "terminal"

            case _:
                raise ValueError(f"unknown item type: '{item_type}'")

        # Handle path argument
        if path:
            path_obj = Path(path).expanduser()
            item_args.setdefault("uid", path)
            item_args.setdefault(
                "arg", str(path_obj.relative_to(self.home, walk_up=True))
            )
            item_args.setdefault("title", path_obj.name)

        # Process icon options (in priority order)
        for icon_type, icon_value in {
            "icon": icon,
            "glyph": glyph,
            "favicon": favicon,
            "appicon": appicon,
            "clearbiticon": clearbiticon,
            "urlicon": urlicon,
            "workflowicon": workflowicon,
            "filetype": filetype,
            "fileicon": fileicon,
            "utiicon": utiicon,
        }.items():
            if icon_value:
                icon_dict = self.process_icon(icon_type, icon_value, icon_dict)
                break

        # Set additional overrides
        if uid:
            item_args["uid"] = uid
        if match:
            item_args["match"] = match
        if autocomplete:
            item_args["autocomplete"] = autocomplete

        # Add any additional kwargs
        item_args.update(kwargs)

        # Generate UID and set defaults
        generated_uid = self.generate_uid(
            item_args.get("title", ""),
            item_args.get("subtitle", ""),
            item_args.get("arg", ""),
        )
        item_args.setdefault("uid", generated_uid)
        item_args.setdefault(
            "match",
            f"{item_args.get('title', '')} {item_args.get('subtitle', '')} {item_args.get('arg', '')}",
        )
        item_args.setdefault("autocomplete", item_args.get("arg", ""))

        # Create menu item
        menu_item = MenuItem(**item_args)
        if icon_dict:
            menu_item.icon = icon_dict

        self.menu_items.append(menu_item)

    def add_url(
        self,
        title: str,
        url: str,
        *,
        subtitle: str | None = None,
        # Icon options
        icon: str | None = None,
        glyph: str | None = None,
        appicon: str | None = None,
        clearbiticon: str | None = None,
        urlicon: str | None = None,
        workflowicon: str | None = None,
        filetype: str | None = None,
        fileicon: str | None = None,
        utiicon: str | None = None,
        # Additional options
        uid: str | None = None,
        match: str | None = None,
        autocomplete: str | None = None,
        **kwargs,
    ) -> None:
        """Add a URL menu item."""
        url = url.replace("http://", "https://")

        self.add_item(
            "url",
            title=title,
            url=url,
            subtitle=subtitle,
            icon=icon,
            glyph=glyph,
            appicon=appicon,
            clearbiticon=clearbiticon,
            urlicon=urlicon,
            workflowicon=workflowicon,
            filetype=filetype,
            fileicon=fileicon,
            utiicon=utiicon,
            uid=uid,
            match=match,
            autocomplete=autocomplete,
            **kwargs,
        )

    def add_exec(
        self,
        title: str,
        command: str,
        *,
        subtitle: str | None = None,
        # Icon options
        icon: str | None = None,
        glyph: str | None = None,
        appicon: str | None = None,
        clearbiticon: str | None = None,
        urlicon: str | None = None,
        workflowicon: str | None = None,
        filetype: str | None = None,
        fileicon: str | None = None,
        utiicon: str | None = None,
        # Additional options
        uid: str | None = None,
        match: str | None = None,
        autocomplete: str | None = None,
        **kwargs,
    ) -> None:
        """Add an executable command menu item."""
        self.add_item(
            "exec",
            title=title,
            command=command,
            subtitle=subtitle,
            icon=icon,
            glyph=glyph,
            appicon=appicon,
            clearbiticon=clearbiticon,
            urlicon=urlicon,
            workflowicon=workflowicon,
            filetype=filetype,
            fileicon=fileicon,
            utiicon=utiicon,
            uid=uid,
            match=match,
            autocomplete=autocomplete,
            **kwargs,
        )

    def add_easy(
        self,
        title: str,
        subtitle: str,
        arg: str,
        *,
        # Icon options
        icon: str | None = None,
        glyph: str | None = None,
        appicon: str | None = None,
        clearbiticon: str | None = None,
        urlicon: str | None = None,
        workflowicon: str | None = None,
        filetype: str | None = None,
        fileicon: str | None = None,
        utiicon: str | None = None,
        # Additional options
        uid: str | None = None,
        match: str | None = None,
        autocomplete: str | None = None,
        path: str | None = None,
        **kwargs,
    ) -> None:
        """Add a simple menu item with title, subtitle, and arg."""
        self.add_item(
            "easy",
            title=title,
            subtitle=subtitle,
            arg=arg,
            icon=icon,
            glyph=glyph,
            appicon=appicon,
            clearbiticon=clearbiticon,
            urlicon=urlicon,
            workflowicon=workflowicon,
            filetype=filetype,
            fileicon=fileicon,
            utiicon=utiicon,
            uid=uid,
            match=match,
            autocomplete=autocomplete,
            path=path,
            **kwargs,
        )

    def add_menu_items(self) -> None:
        """Add all menu items for MaxCare workflow."""
        _c = self.config

        # Service URLs
        self.add_url(
            "argocd",
            "https://argocd-ci.tailf01e20.ts.net/applications",
            clearbiticon="argoproj.io",
        )
        self.add_url(
            "pulumi",
            "https://app.pulumi.com/maxcare",
            urlicon="https://images.credly.com/images/b7fec661-b57c-4973-b519-32cc1c48c15a/blob.png",
        )
        self.add_url(
            "litellm",
            "https://litellm-litellm-ingress.tailf01e20.ts.net/ui/",
            urlicon="https://store-images.s-microsoft.com/image/apps.40025.ac0d3b4a-c67a-45ec-91a9-894c06eaf676.d766dfbe-f6e1-4b60-a237-b6e16bedf5e7.bb839fa9-72f3-43a0-81e1-1cc5aabe08e8",
        )
        self.add_url(
            "Biller Review",
            "https://biller-review.maxcare.ai",
            urlicon="https://www.maxcare.ai/_assets/v8/e05b2ce343d83dbf2ea16d4736b7900181b2d486.png",
        )
        self.add_url(
            "EzDerm Replication Status",
            "https://biller-review-server.tailf01e20.ts.net/metrics/replication-status",
            urlicon="https://www.maxcare.ai/_assets/v8/e05b2ce343d83dbf2ea16d4736b7900181b2d486.png",
        )
        self.add_url("Builds", "https://buildkite.com/maxcare/", subtitle="Buildkite")
        self.add_url(
            f"Builds {_c.buildkite_username}/*",
            f"https://buildkite.com/maxcare/monorepo/builds?branch={_c.buildkite_username}%2F%2A",
            subtitle="Buildkite",
        )
        self.add_url(
            "Comms",
            "https://maxcare-ai.slack.com",
            subtitle="Slack",
            clearbiticon="slack.com",
        )
        self.add_url(
            "Errors",
            "http://maxcare-ai.sentry.io",
            subtitle="Sentry",
            urlicon="https://avatars.slack-edge.com/2023-08-11/5742750680529_887c0a192e074f7cf3e1_512.png",
        )
        self.add_url(
            "Logs",
            "https://us3.datadoghq.com/logs",
            subtitle="DataDog",
            urlicon="https://astro-provider-logos.s3.us-east-2.amazonaws.com/apache-airflow-providers-datadog.png",
        )
        self.add_url(
            "LLM Traces",
            "https://us3.datadoghq.com/llm/traces",
            subtitle="DataDog",
            urlicon="https://astro-provider-logos.s3.us-east-2.amazonaws.com/apache-airflow-providers-datadog.png",
        )
        self.add_url("Temporal", "https://cloud.temporal.io", subtitle="Temporal")
        self.add_url(
            "Analytics",
            "https://metabase.tailf01e20.ts.net",
            subtitle="Metabase",
            clearbiticon="metabase.com",
        )
        self.add_url("Hiring", "https://app.dover.com/home", subtitle="Dover")

        self.add_url(
            "Chat",
            "https://chat.tailf01e20.ts.net/",
            subtitle="Open-WebUI",
            urlicon="https://chat.tailf01e20.ts.net/static/favicon.png",
        )

        # Repository links
        for repo in ["monorepo", "deployments"]:
            bk_url = f"https://buildkite.com/maxcare/{repo}"
            self.add_url(
                f"{repo}",
                bk_url,
                subtitle="buildkite",
            )
            self.add_url(
                f"{repo} @ main",
                f"{bk_url}/builds?branch=main",
                subtitle="buildkite all builds @ main",
            )
            self.add_url(
                f"{repo} latest build @ main",
                f"{bk_url}/builds/latest/steps/canvas",
                subtitle="buildkite latest build @ main",
            )

            self.add_url(f"github {repo}", f"https://github.com/maxcare-ai/{repo}")

        # Source code projects

        src_dirs = [
            _c.maxcare_src_dir,
            *_c.maxcare_src_dir.glob("*"),
            _c.src_dir / "litellm",
            _c.src_dir / "mise",
            _c.src_dir / "usage",
            *_c.src_dir.glob("pydantic*"),
        ]

        for src_dir in src_dirs:
            if not src_dir.exists():
                logger.warning(f"Source directory {src_dir} does not exist")
                continue

            # Check for workspace files
            if workspace_files := list(src_dir.glob("*.code-workspace")):
                workspace_path = workspace_files[0]
                relative_path = workspace_path.relative_to(self.home)
                self.add_easy(
                    src_dir.name,
                    f"code ~/{relative_path}",
                    f"open -a Cursor ~/{relative_path}",
                    appicon="Cursor",
                )
            else:
                relative_path = src_dir.relative_to(self.home)
                self.add_easy(
                    src_dir.name,
                    f"code ~/{relative_path}",
                    f"open -a Cursor {src_dir}",
                    appicon="Cursor",
                )

        # AWS access portal
        self.add_url(
            "AWS access portal",
            f"https://{_c.aws_domain}/start/",
            subtitle=f"AWS portal for {_c.aws_domain}",
            glyph="cloud",
            icon="./icons/aws.webp",
        )

        # AWS accounts
        for account in _c.aws_accounts:
            for role, service in product(
                account.role_names, ("home", *account.services)
            ):
                destination = ""
                service_display = ""
                if service == "home":
                    icon_kwargs = {"icon": "./icons/aws cube.png"}
                else:
                    icon_kwargs = {"icon": f"./icons/Arch_*{service.lower()}*"}
                    destination = f"&destination=https://{_c.aws_region}.console.aws.amazon.com/{service.lower()}"
                    service_display = f" — {service}"

                url = f"https://{_c.aws_domain}/start/#/console?account_id={account.id}&role_name={role}{destination}"
                subtitle = f"id: {account.id} — role: {role} — region: {_c.aws_region}{service_display}"

                self.add_url(
                    f"{account.name}{service_display}",
                    url,
                    subtitle=subtitle,
                    **icon_kwargs,
                )

    def add_config_items(self) -> None:
        """Add configuration menu items."""
        cache_path = self.icon_cache / "*"
        self.add_exec(
            "clear cache", f'[[ -d "{self.icon_cache}/" ]] && rm "{cache_path}"'
        )

    def output_menu(self) -> str:
        """Generate the complete Alfred menu JSON."""
        menu = AlfredMenu(
            cache=MenuCache(seconds=self.cache_ttl), items=self.menu_items
        )
        return menu.model_dump_json(indent=2, exclude_none=True)


def main() -> None:
    """Main entry point."""

    os.environ.setdefault(
        "AWS_ACCOUNTS",
        json.dumps(
            [
                {"id": "180294178811", "name": "Max AI (root)"},
                {"id": "577638356460", "name": "WorkloadDevelopment"},
                {
                    "id": "710271938220",
                    "name": "WorkloadProduction",
                    "services": ("Bedrock", "CloudWatch", "S3", "RDS"),
                },
                {"id": "054037096460", "name": "Deployment"},
                {"id": "970547381188", "name": "SecurityBreakglass"},
                {"id": "266735801805", "name": "SecurityTooling"},
                {"id": "349960126732", "name": "DeploymentBackup"},
                {"id": "491085404620", "name": "SecurityRO"},
                {"id": "619071347858", "name": "Logging"},
                {"id": "739275459603", "name": "Network"},
            ]
        ),
    )

    parser = argparse.ArgumentParser(description="Alfred MaxCare workflow generator")
    parser.add_argument(
        "--cache-ttl", type=int, default=3600, help="Cache TTL in seconds"
    )
    args = parser.parse_args()

    workflow = AlfredMaxcareWorkflow(config=Config(), cache_ttl=args.cache_ttl)
    workflow.add_menu_items()
    workflow.add_config_items()
    print(workflow.output_menu())


if __name__ == "__main__":
    main()
