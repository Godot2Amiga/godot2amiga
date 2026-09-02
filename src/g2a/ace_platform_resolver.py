"""Resolve package display policy into unified ACE main configuration."""

from __future__ import annotations

from pathlib import Path

from g2a.ace_main_composer import AceMainPlatformConfig
from g2a.assets import AssetManifestError, load_manifest
from g2a.package_display import PackageDisplayError, load_package_display_contract
from g2a.runtime_render_node import RenderNodeKind, RuntimeRenderNode


class AcePlatformResolutionError(ValueError):
    """Raised when package display policy cannot serve its runtime render nodes."""


def _referenced_bitmap_ids(nodes: tuple[RuntimeRenderNode, ...]) -> tuple[str, ...]:
    referenced: set[str] = set()
    for node in nodes:
        if node.kind is RenderNodeKind.SPRITE:
            if node.texture_id is None:
                raise AcePlatformResolutionError(
                    f"static runtime node '{node.node_id}' has no texture id"
                )
            referenced.add(node.texture_id)
            continue

        animation = node.animation
        if animation is None:
            raise AcePlatformResolutionError(
                f"animated runtime node '{node.node_id}' has no animation"
            )
        referenced.update(frame.texture_id for clip in animation.clips for frame in clip.frames)
    return tuple(sorted(referenced))


def resolve_ace_main_platform_config(
    package: Path,
    nodes: tuple[RuntimeRenderNode, ...],
) -> AceMainPlatformConfig:
    """Resolve and validate the explicit display for unified ACE generation."""
    package = package.expanduser().resolve()
    try:
        display = load_package_display_contract(package)
    except PackageDisplayError as error:
        raise AcePlatformResolutionError(str(error)) from error
    if display is None:
        raise AcePlatformResolutionError(
            "package has no explicit display contract required for unified ACE generation"
        )

    try:
        manifest = load_manifest(package)
    except AssetManifestError as error:
        raise AcePlatformResolutionError(f"invalid assets manifest: {error}") from error

    palettes = {palette.asset_id: palette for palette in manifest.palettes}
    selected_palette = palettes.get(display.palette)
    if selected_palette is None:
        raise AcePlatformResolutionError(
            f"display palette '{display.palette}' has no matching palette asset"
        )

    bitmaps = {bitmap.asset_id: bitmap for bitmap in manifest.bitmaps}
    for asset_id in _referenced_bitmap_ids(nodes):
        bitmap = bitmaps.get(asset_id)
        if bitmap is None:
            if asset_id in palettes:
                raise AcePlatformResolutionError(
                    f"runtime texture '{asset_id}' resolves to a palette, not a bitmap"
                )
            raise AcePlatformResolutionError(
                f"runtime texture '{asset_id}' has no matching bitmap asset"
            )
        if bitmap.palette_id != display.palette:
            raise AcePlatformResolutionError(
                f"runtime bitmap '{asset_id}' uses palette '{bitmap.palette_id}' "
                f"but display selects '{display.palette}'"
            )

    return AceMainPlatformConfig(
        palette_path=(Path("data") / selected_palette.output).as_posix(),
        bitplane_depth=display.bitplane_depth,
        color_count=1 << display.bitplane_depth,
        interleaved=display.interleaved,
        double_buffered=display.double_buffered,
    )


__all__ = [
    "AcePlatformResolutionError",
    "resolve_ace_main_platform_config",
]
