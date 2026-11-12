#!/usr/bin/env python3
"""Read-only delivery audit; manifest creation requires --write-manifest.

Uses only Python's standard library. ffprobe is optional and discovered on PATH.
Ignores Finder's .DS_Store files, reporting them separately.
Does not decode the complete video or assess content, sound, or visual quality.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def audit(root, probe, write=False, verify=False):
    report = {'root': str(root), 'files': [], 'errors': [], 'warnings': [],
              'ignored_metadata': [],
              'limits': ['No full media decode', 'No visual or listening review']}
    manifest = root / 'SHA256SUMS.txt'
    entries = {}
    media_count = 0
    # rglob does not traverse symlink directories; reject all symlink entries.
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            report['errors'].append('Symlink is not a self-contained asset: ' + rel)
            continue
        if not path.is_file() or path == manifest:
            continue
        if path.name == '.DS_Store':
            report['ignored_metadata'].append(rel)
            continue
        if any(c in rel for c in ('\n', '\r', '\\')):
            report['errors'].append('Unsupported manifest filename: ' + repr(rel))
            continue
        item = {'path': rel, 'bytes': path.stat().st_size, 'sha256': digest(path)}
        entries[rel] = item['sha256']
        if path.suffix.lower() == '.zip':
            try:
                with zipfile.ZipFile(path) as archive:
                    bad = archive.testzip()
                    if bad:
                        raise ValueError('Corrupt member: ' + bad)
                item['zip_integrity'] = 'passed'
            except Exception as exc:
                report['errors'].append(f'{rel}: ZIP integrity failed: {exc}')
        if path.suffix.lower() in ('.mp4', '.mov', '.mkv', '.webm'):
            media_count += 1
            if probe:
                try:
                    result = subprocess.run(
                        [probe, '-v', 'error', '-show_streams', '-show_format',
                         '-of', 'json', str(path)], capture_output=True,
                        text=True, timeout=120, check=True)
                    if result.stderr.strip():
                        raise ValueError(result.stderr.strip())
                    meta = json.loads(result.stdout)
                    duration = float(meta.get('format', {}).get('duration', 0))
                    video = [s for s in meta.get('streams', [])
                             if s.get('codec_type') == 'video']
                    audio = [s for s in meta.get('streams', [])
                             if s.get('codec_type') == 'audio']
                    if not video or not math.isfinite(duration) or duration <= 0:
                        raise ValueError('Missing video stream or valid duration')
                    if not audio:
                        report['warnings'].append(rel + ': no audio stream; check intent')
                    item['media'] = {'duration_seconds': duration,
                                     'width': video[0].get('width'),
                                     'height': video[0].get('height'),
                                     'frame_rate': video[0].get('avg_frame_rate'),
                                     'video_codec': video[0].get('codec_name'),
                                     'audio_streams': len(audio)}
                except Exception as exc:
                    report['errors'].append(f'{rel}: media probe failed: {exc}')
        report['files'].append(item)
    if not entries:
        report['errors'].append('No delivery files found')
    if media_count and not probe:
        report['warnings'].append('ffprobe unavailable: media metadata not checked')
    if verify:
        expected = {}
        try:
            for line in manifest.read_text(encoding='utf-8').splitlines():
                value, name = line.split('  ', 1)
                if len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
                    raise ValueError('Invalid SHA-256')
                name = name.removeprefix('./')
                if name in expected:
                    raise ValueError('Duplicate manifest entry: ' + name)
                expected[name] = value
            for name in sorted(set(entries) | set(expected)):
                if entries.get(name) != expected.get(name):
                    report['errors'].append('Manifest mismatch, missing or extra file: ' + name)
        except Exception as exc:
            report['errors'].append('Cannot verify manifest: ' + str(exc))
    if write and not report['errors']:
        manifest.write_text(''.join(f'{value}  {name}\n' for name, value in sorted(entries.items())),
                            encoding='utf-8')
        report['manifest_written'] = str(manifest)
    report['file_count'] = len(entries)
    report['total_bytes'] = sum(item['bytes'] for item in report['files'])
    report['checks_passed'] = not report['errors']
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--ffprobe', help='ffprobe executable; defaults to PATH')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write-manifest', action='store_true')
    mode.add_argument('--verify-manifest', action='store_true')
    args = parser.parse_args()
    if args.directory.is_symlink() or not args.directory.is_dir():
        parser.error('directory must be an existing real directory, not a symlink')
    root = args.directory.resolve()
    # Never overwrite a manifest symlink pointing outside the delivery directory.
    if (root / 'SHA256SUMS.txt').is_symlink():
        parser.error('root manifest must not be a symlink')
    report = audit(root, args.ffprobe or shutil.which('ffprobe'),
                   args.write_manifest, args.verify_manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['checks_passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
