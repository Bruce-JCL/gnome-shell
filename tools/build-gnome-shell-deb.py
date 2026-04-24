#!/usr/bin/env python3

import gzip
import hashlib
import math
import shutil
import subprocess
import sys
from pathlib import Path


PACKAGE_NAME = 'gnome-shell'

MESON_STAGE_MAP = [
    ('/etc/xdg/autostart/gnome-shell-overrides-migration.desktop', '/etc/xdg/autostart/gnome-shell-overrides-migration.desktop'),
    ('/usr/bin/gnome-extensions', '/usr/bin/gnome-extensions'),
    ('/usr/bin/gnome-shell', '/usr/bin/gnome-shell'),
    ('/usr/bin/gnome-shell-extension-tool', '/usr/bin/gnome-shell-extension-tool'),
    ('/usr/bin/gnome-shell-perf-tool', '/usr/bin/gnome-shell-perf-tool'),
    ('/usr/lib/gnome-shell/Gvc-1.0.typelib', '/usr/lib/aarch64-linux-gnu/gnome-shell/Gvc-1.0.typelib'),
    ('/usr/lib/gnome-shell/Shell-0.1.typelib', '/usr/lib/aarch64-linux-gnu/gnome-shell/Shell-0.1.typelib'),
    ('/usr/lib/gnome-shell/St-1.0.typelib', '/usr/lib/aarch64-linux-gnu/gnome-shell/St-1.0.typelib'),
    ('/usr/lib/gnome-shell/girepository-1.0/Shew-0.typelib', '/usr/lib/aarch64-linux-gnu/gnome-shell/girepository-1.0/Shew-0.typelib'),
    ('/usr/lib/gnome-shell/libgnome-shell-menu.so', '/usr/lib/aarch64-linux-gnu/gnome-shell/libgnome-shell-menu.so'),
    ('/usr/lib/gnome-shell/libgnome-shell.so', '/usr/lib/aarch64-linux-gnu/gnome-shell/libgnome-shell.so'),
    ('/usr/lib/gnome-shell/libgvc.so', '/usr/lib/aarch64-linux-gnu/gnome-shell/libgvc.so'),
    ('/usr/lib/gnome-shell/libshew-0.so', '/usr/lib/aarch64-linux-gnu/gnome-shell/libshew-0.so'),
    ('/usr/lib/gnome-shell/libst-1.0.so', '/usr/lib/aarch64-linux-gnu/gnome-shell/libst-1.0.so'),
    ('/usr/libexec/gnome-shell-calendar-server', '/usr/libexec/gnome-shell-calendar-server'),
    ('/usr/libexec/gnome-shell-hotplug-sniffer', '/usr/libexec/gnome-shell-hotplug-sniffer'),
    ('/usr/libexec/gnome-shell-overrides-migration.sh', '/usr/libexec/gnome-shell-overrides-migration.sh'),
    ('/usr/libexec/gnome-shell-perf-helper', '/usr/libexec/gnome-shell-perf-helper'),
    ('/usr/libexec/gnome-shell-portal-helper', '/usr/libexec/gnome-shell-portal-helper'),
    ('/usr/share/applications/evolution-calendar.desktop', '/usr/share/applications/evolution-calendar.desktop'),
    ('/usr/share/applications/org.gnome.Shell.Extensions.desktop', '/usr/share/applications/org.gnome.Shell.Extensions.desktop'),
    ('/usr/share/applications/org.gnome.Shell.PortalHelper.desktop', '/usr/share/applications/org.gnome.Shell.PortalHelper.desktop'),
    ('/usr/share/applications/org.gnome.Shell.desktop', '/usr/share/applications/org.gnome.Shell.desktop'),
    ('/usr/share/bash-completion/completions/gnome-extensions', '/usr/share/bash-completion/completions/gnome-extensions'),
    ('/usr/share/dbus-1/services/org.gnome.Extensions.service', '/usr/share/dbus-1/services/org.gnome.Extensions.service'),
    ('/usr/share/dbus-1/services/org.gnome.ScreenSaver.service', '/usr/share/dbus-1/services/org.gnome.ScreenSaver.service'),
    ('/usr/share/dbus-1/services/org.gnome.Shell.CalendarServer.service', '/usr/share/dbus-1/services/org.gnome.Shell.CalendarServer.service'),
    ('/usr/share/dbus-1/services/org.gnome.Shell.Extensions.service', '/usr/share/dbus-1/services/org.gnome.Shell.Extensions.service'),
    ('/usr/share/dbus-1/services/org.gnome.Shell.HotplugSniffer.service', '/usr/share/dbus-1/services/org.gnome.Shell.HotplugSniffer.service'),
    ('/usr/share/dbus-1/services/org.gnome.Shell.Notifications.service', '/usr/share/dbus-1/services/org.gnome.Shell.Notifications.service'),
    ('/usr/share/dbus-1/services/org.gnome.Shell.PortalHelper.service', '/usr/share/dbus-1/services/org.gnome.Shell.PortalHelper.service'),
    ('/usr/share/dbus-1/services/org.gnome.Shell.Screencast.service', '/usr/share/dbus-1/services/org.gnome.Shell.Screencast.service'),
    ('/usr/share/man/man1/gnome-extensions.1.gz', '/usr/share/man/man1/gnome-extensions.1'),
    ('/usr/share/man/man1/gnome-shell.1.gz', '/usr/share/man/man1/gnome-shell.1'),
    ('/usr/share/xdg-desktop-portal/portals/gnome-shell.portal', '/usr/share/xdg-desktop-portal/portals/gnome-shell.portal'),
]

SYSTEM_COPY_PATHS = [
    '/usr/share/bug/gnome-shell/control',
    '/usr/share/doc/gnome-shell/changelog.Debian.gz',
    '/usr/share/doc/gnome-shell/copyright',
    '/usr/share/glib-2.0/schemas/10_gnome-shell.gschema.override',
    '/usr/share/lintian/overrides/gnome-shell',
]

SOURCE_COPY_MAP = [
    ('/usr/share/doc/gnome-shell/NEWS.gz', 'NEWS'),
    ('/usr/share/doc/gnome-shell/README.md', 'README.md'),
]

DIRECTORIES = [
    '/usr/lib/gnome-shell',
    '/usr/lib/gnome-shell/girepository-1.0',
    '/usr/share/bug/gnome-shell',
    '/usr/share/doc/gnome-shell',
]

CONTROL_FIELDS = [
    'Package',
    'Version',
    'Section',
    'Priority',
    'Architecture',
    'Maintainer',
    'Original-Maintainer',
    'Depends',
    'Recommends',
    'Suggests',
    'Provides',
    'Breaks',
    'Description',
    'Homepage',
]


def fail(message: str) -> None:
    print(f'error: {message}', file=sys.stderr)
    raise SystemExit(1)


def run_command(command, *, capture_output=False):
    return subprocess.run(
        command,
        check=False,
        text=True,
        capture_output=capture_output,
    )


def parse_control_fields(text: str):
    fields = {}
    current_key = None

    for line in text.splitlines():
        if not line:
            continue
        if line[0].isspace():
            if current_key is None:
                fail('unexpected continuation line in dpkg metadata')
            fields[current_key] += '\n' + line
            continue

        key, value = line.split(':', 1)
        current_key = key
        fields[key] = value.lstrip()

    return fields


def format_control_field(key: str, value: str) -> str:
    lines = value.splitlines()
    if len(lines) == 1:
        return f'{key}: {lines[0]}\n'
    return f'{key}: {lines[0]}\n' + ''.join(f'{line}\n' for line in lines[1:])


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def gzip_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open('rb') as input_file, destination.open('wb') as output_file:
        with gzip.GzipFile(filename='', mode='wb', fileobj=output_file, mtime=0) as gz_file:
            shutil.copyfileobj(input_file, gz_file)


def stage_meson_output(install_root: Path, package_root: Path, destination: str, source_path: str) -> None:
    source = install_root / source_path.lstrip('/')
    if not source.exists():
        fail(f'missing installed file for packaging: {source}')

    target = package_root / destination.lstrip('/')
    if destination.endswith('.gz'):
        gzip_file(source, target)
    else:
        copy_file(source, target)


def stage_system_file(package_root: Path, source_path: str) -> None:
    source = Path(source_path)
    if not source.exists():
        fail(f'missing required system file: {source}')
    copy_file(source, package_root / source_path.lstrip('/'))


def stage_source_file(source_root: Path, package_root: Path, destination: str, source_path: str) -> None:
    source = source_root / source_path
    if not source.exists():
        fail(f'missing required source file: {source}')

    target = package_root / destination.lstrip('/')
    if destination.endswith('.gz'):
        gzip_file(source, target)
    else:
        copy_file(source, target)


def compute_installed_size_kib(package_root: Path) -> int:
    total_bytes = 0
    for path in package_root.rglob('*'):
        if 'DEBIAN' in path.parts:
            continue
        if path.is_file() and not path.is_symlink():
            total_bytes += path.stat().st_size
    return max(1, math.ceil(total_bytes / 1024))


def write_md5sums(package_root: Path) -> None:
    md5_lines = []
    for path in sorted(package_root.rglob('*')):
        if not path.is_file() or path.is_symlink() or 'DEBIAN' in path.parts:
            continue
        digest = hashlib.md5(path.read_bytes()).hexdigest()
        md5_lines.append(f'{digest}  {path.relative_to(package_root).as_posix()}')

    (package_root / 'DEBIAN' / 'md5sums').write_text('\n'.join(md5_lines) + '\n', encoding='utf-8')


def query_package_metadata():
    result = run_command(['dpkg-query', '-s', PACKAGE_NAME], capture_output=True)
    if result.returncode != 0:
        fail(f'failed to query installed package metadata: {result.stderr.strip()}')
    return parse_control_fields(result.stdout)


def write_control(package_root: Path, metadata) -> None:
    metadata = dict(metadata)
    metadata['Installed-Size'] = str(compute_installed_size_kib(package_root))

    fields = CONTROL_FIELDS[:5] + ['Installed-Size'] + CONTROL_FIELDS[5:]
    control_text = ''.join(
        format_control_field(field, metadata[field])
        for field in fields
        if field in metadata and metadata[field]
    )
    (package_root / 'DEBIAN' / 'control').write_text(control_text, encoding='utf-8')


def write_conffiles(package_root: Path, metadata) -> None:
    conffiles = metadata.get('Conffiles')
    if not conffiles:
        return

    lines = []
    for line in conffiles.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lines.append(stripped.split()[0])

    if lines:
        (package_root / 'DEBIAN' / 'conffiles').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main(argv):
    if len(argv) != 4:
        fail('usage: build-gnome-shell-deb.py <source_root> <build_root> <output_path>')

    source_root = Path(argv[1]).resolve()
    build_root = Path(argv[2]).resolve()
    output_path = Path(argv[3]).resolve()

    install_root = build_root / 'deb-install-root'
    package_root = build_root / 'deb-package-root' / PACKAGE_NAME

    if install_root.exists():
        shutil.rmtree(install_root)
    if package_root.exists():
        shutil.rmtree(package_root)

    install_root.mkdir(parents=True)
    (package_root / 'DEBIAN').mkdir(parents=True)

    install_result = run_command(
        ['meson', 'install', '-C', str(build_root), '--destdir', str(install_root), '--no-rebuild', '--quiet']
    )
    if install_result.returncode != 0:
        fail('meson install failed; run ninja -C build first so packaging can reuse existing build outputs')

    metadata = query_package_metadata()

    for directory in DIRECTORIES:
        (package_root / directory.lstrip('/')).mkdir(parents=True, exist_ok=True)

    for destination, source_path in MESON_STAGE_MAP:
        stage_meson_output(install_root, package_root, destination, source_path)

    for source_path in SYSTEM_COPY_PATHS:
        stage_system_file(package_root, source_path)

    for destination, source_path in SOURCE_COPY_MAP:
        stage_source_file(source_root, package_root, destination, source_path)

    write_control(package_root, metadata)
    write_conffiles(package_root, metadata)
    write_md5sums(package_root)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    build_result = run_command(
        ['dpkg-deb', '--root-owner-group', '--build', str(package_root), str(output_path)]
    )
    if build_result.returncode != 0:
        fail('dpkg-deb failed to create the package')


if __name__ == '__main__':
    main(sys.argv)