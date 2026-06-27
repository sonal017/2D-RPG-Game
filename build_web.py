from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / 'build' / 'web'

RUNTIME_FILES = [
    'debug.py',
    'enemy.py',
    'enemy2.py',
    'entity.py',
    'level.py',
    'level2.py',
    'magic.py',
    'main.py',
    'particle.py',
    'player.py',
    'settings.py',
    'support.py',
    'tile.py',
    'ui.py',
    'upgrade.py',
    'weapon.py',
]

UNUSED_GRAPHICS = {
    'arrowkey.png',
    'ekey.png',
    'leftctrl.png',
    'mkey.png',
    'qkey.png',
    'rock.png',
    'rock1.png',
    'space.png',
    'tutorial1.png',
    'bgimg/loginbg.jpeg',
    'player_death/death _right.png',
    'player_death/death_left.png',
}

BROWSERFS_TAG = '<script src="https://pygame-web.github.io/cdn/0.9.3/browserfs.min.js"></script>'

BROWSER_INPUT_BRIDGE_TAG = '''<script>
(() => {
    if (window.__hiroInputBridgeInstalled) {
        return;
    }

    window.__hiroInputBridgeInstalled = true;
    window.hiroStartRequested = false;

    const requestStart = () => {
        window.hiroStartRequested = true;
    };

    const handleKey = (event) => {
        if (event.code === 'Space' || event.code === 'Enter') {
            window.hiroStartRequested = true;
            event.preventDefault();
        }
    };

    window.addEventListener('pointerdown', requestStart, { passive: true });
    window.addEventListener('keydown', handleKey);
    document.addEventListener('pointerdown', requestStart, { passive: true });
    document.addEventListener('keydown', handleKey);
})();
</script>'''

SCREEN_IMAGE_REPLACEMENTS = {
    './graphics/bgimg/homebg.png': './graphics/bgimg/homebg.jpg',
    './graphics/bgimg/game_over_neon_lights_hd_game_over.png': './graphics/bgimg/game_over_neon_lights_hd_game_over.jpg',
    './graphics/bgimg/victory1.png': './graphics/bgimg/victory1.jpg',
    './graphics/tutorial11.png': './graphics/tutorial11.jpg',
    './graphics/tutorial12.png': './graphics/tutorial12.jpg',
}


def should_copy_graphics(path):
    rel_path = path.relative_to(ROOT / 'graphics').as_posix()
    return rel_path not in UNUSED_GRAPHICS


def copy_browser_runtime(app_dir):
    app_dir.mkdir(parents=True, exist_ok=True)

    for filename in RUNTIME_FILES:
        shutil.copy2(ROOT / filename, app_dir / filename)

    graphics_src = ROOT / 'graphics'
    graphics_dst = app_dir / 'graphics'
    for source_path in graphics_src.rglob('*'):
        if not source_path.is_file() or not should_copy_graphics(source_path):
            continue

        destination_path = graphics_dst / source_path.relative_to(graphics_src)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)


def optimize_images(app_dir):
    try:
        from PIL import Image
    except ImportError:
        print('Pillow is not installed; skipping image recompression.')
        return

    for image_path in (app_dir / 'graphics').rglob('*'):
        if image_path.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
            continue

        original_size = image_path.stat().st_size
        temp_path = image_path.with_name(f'{image_path.stem}.tmp{image_path.suffix}')

        try:
            with Image.open(image_path) as image:
                save_kwargs = {}
                if image_path.suffix.lower() == '.png':
                    save_kwargs = {'optimize': True, 'compress_level': 9}
                else:
                    save_kwargs = {'optimize': True, 'quality': 82, 'progressive': True}

                image.save(temp_path, **save_kwargs)

            if temp_path.stat().st_size < original_size:
                temp_path.replace(image_path)
            else:
                temp_path.unlink()
        except Exception as exc:
            if temp_path.exists():
                temp_path.unlink()
            print(f'Skipping image optimization for {image_path}: {exc}')


def convert_screen_images(app_dir):
    try:
        from PIL import Image
    except ImportError:
        print('Pillow is not installed; skipping screen image conversion.')
        return

    for source, target in SCREEN_IMAGE_REPLACEMENTS.items():
        source_path = app_dir / source.removeprefix('./')
        target_path = app_dir / target.removeprefix('./')
        if not source_path.exists():
            continue

        try:
            with Image.open(source_path) as image:
                image = image.convert('RGB')
                image.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                image.save(
                    target_path,
                    'JPEG',
                    quality=82,
                    optimize=True,
                    progressive=True,
                )
            source_path.unlink()
        except Exception as exc:
            print(f'Skipping JPG conversion for {source_path}: {exc}')


def patch_web_asset_paths(app_dir):
    main_path = app_dir / 'main.py'
    source = main_path.read_text(encoding='utf-8')
    for old_path, new_path in SCREEN_IMAGE_REPLACEMENTS.items():
        source = source.replace(old_path, new_path)
    main_path.write_text(source, encoding='utf-8')


def patch_browserfs_load_order(build_dir):
    index_path = build_dir / 'index.html'
    html = index_path.read_text(encoding='utf-8')

    if BROWSERFS_TAG in html.split('pythons.js', 1)[0]:
        return

    html = html.replace('<html lang="en-us">', f'<html lang="en-us">{BROWSERFS_TAG}', 1)
    index_path.write_text(html, encoding='utf-8')


def patch_static_input_bridge(build_dir):
    index_path = build_dir / 'index.html'
    html = index_path.read_text(encoding='utf-8')

    if 'window.__hiroInputBridgeInstalled' in html:
        return

    html = html.replace('<html lang="en-us">', f'<html lang="en-us">{BROWSER_INPUT_BRIDGE_TAG}', 1)
    index_path.write_text(html, encoding='utf-8')


def patch_canvas_focus_mode(build_dir):
    index_path = build_dir / 'index.html'
    html = index_path.read_text(encoding='utf-8')
    html = html.replace('data-os="vtx,snd,gui"', 'data-os="snd,gui"', 1)
    html = html.replace('xtermjs : "1"', 'xtermjs : "0"', 1)
    html = html.replace('gui_debug : 2', 'gui_debug : 0', 1)
    html = html.replace('console : 10', 'console : 0', 1)
    html = html.replace('pyconsole.hidden = debug_hidden', 'pyconsole.hidden = true', 1)
    index_path.write_text(html, encoding='utf-8')


def patch_archive_cache_buster(build_dir):
    index_path = build_dir / 'index.html'
    html = index_path.read_text(encoding='utf-8')
    cache_token = str((build_dir / 'game.tar.gz').stat().st_mtime_ns)
    html = html.replace(
        'platform.fopen("game.tar.gz", "rb")',
        f'platform.fopen("game.tar.gz?v={cache_token}", "rb")',
    )
    html = html.replace(
        'platform.fopen("game.apk", "rb")',
        f'platform.fopen("game.apk?v={cache_token}", "rb")',
    )
    index_path.write_text(html, encoding='utf-8')


def patch_browser_window_injection(build_dir):
    index_path = build_dir / 'index.html'
    html = index_path.read_text(encoding='utf-8')
    injection = '    __import__("__main__").hiro_browser_window = platform.window\n'
    needle = '    await shell.source(main, callback=ui_callback)'

    if injection in html:
        return

    html = html.replace(needle, injection + needle, 1)
    index_path.write_text(html, encoding='utf-8')


def run_pygbag(app_dir):
    subprocess.check_call([
        sys.executable,
        '-m',
        'pygbag',
        '--build',
        '--ume_block',
        '0',
        '--CONSOLE',
        '0',
        '--disable-sound-format-error',
        str(app_dir),
    ])


def publish_build(app_dir):
    staged_build = app_dir / 'build' / 'web'
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(staged_build, OUTPUT_DIR)
    patch_browserfs_load_order(OUTPUT_DIR)
    patch_static_input_bridge(OUTPUT_DIR)
    patch_canvas_focus_mode(OUTPUT_DIR)
    patch_archive_cache_buster(OUTPUT_DIR)
    patch_browser_window_injection(OUTPUT_DIR)


def main():
    with tempfile.TemporaryDirectory(prefix='hiro-web-build-') as temp_dir:
        app_dir = Path(temp_dir) / 'game'
        copy_browser_runtime(app_dir)
        optimize_images(app_dir)
        convert_screen_images(app_dir)
        patch_web_asset_paths(app_dir)
        run_pygbag(app_dir)
        publish_build(app_dir)


if __name__ == '__main__':
    main()
