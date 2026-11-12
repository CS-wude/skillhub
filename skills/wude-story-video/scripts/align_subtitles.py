#!/usr/bin/env python3
"""Align semantic subtitle phrases and named events to measured Edge word boundaries.

Standard library only. Input paths are relative to the input JSON. No speech is
generated and no times are inferred inside a speech token. See free-production.md.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import unicodedata


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', text) if c.isalnum())


def number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + ' must be a finite number')
    return float(value)


def stamp(seconds):
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3600000)
    minutes, millis = divmod(millis, 60000)
    secs, millis = divmod(millis, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02},{millis:03}'


def align(plan, base):
    fps = number(plan.get('fps', 30), 'fps')
    if fps <= 0 or not fps.is_integer():
        raise ValueError('fps must be a positive integer')
    scenes = plan.get('scenes', [])
    if not scenes:
        raise ValueError('No scenes supplied')
    cues, events, seen = [], [], set()
    previous_end = 0.0
    for scene in scenes:
        ident = scene['id']
        if not isinstance(ident, str) or not ident or ident in seen:
            raise ValueError('Scene IDs must be nonempty and unique')
        seen.add(ident)
        start = number(scene['start'], ident + '.start')
        duration = number(scene['duration'], ident + '.duration')
        delay = number(scene.get('voice_delay', 0), ident + '.voice_delay')
        if start < previous_end - 1e-7 or duration <= 0 or not 0 <= delay < duration:
            raise ValueError(ident + ': scenes overlap or duration/delay is invalid')
        if any(abs(t * fps - round(t * fps)) > 1e-5 for t in (start, duration)):
            raise ValueError(ident + ': start and duration must lie on frame boundaries')
        end = start + duration
        previous_end = end
        words_path = base / scene['words_file']
        words, token_positions, char_pos, last_end = [], {}, 0, 0.0
        for line in words_path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            word = json.loads(line)
            if word.get('type') != 'WordBoundary':
                continue
            token = normalized(word['text'])
            if not token:
                continue
            offset = number(word['offset'], 'word.offset') / 1e7
            length = number(word['duration'], 'word.duration') / 1e7
            if offset < last_end - 1e-6 or offset < 0 or length <= 0:
                raise ValueError(ident + ': unordered or invalid word timing')
            if delay + offset + length > duration + 1e-6:
                raise ValueError(ident + ': narration exceeds scene duration')
            token_positions[char_pos] = offset
            words.append({'token': token, 'offset': offset, 'duration': length})
            char_pos += len(token)
            last_end = offset + length
        text = scene['text']
        full = normalized(text)
        if not full or ''.join(w['token'] for w in words) != full:
            raise ValueError(ident + ': word boundaries do not cover the script in order')
        phrases = scene['phrases']
        if not phrases or any(not isinstance(p, str) or not normalized(p) for p in phrases):
            raise ValueError(ident + ': phrases must be nonempty speech strings')
        if ''.join(phrases) != text:
            raise ValueError(ident + ': phrases must reproduce the complete script exactly')
        cursor = 0
        for phrase in phrases:
            target, collected, first = normalized(phrase), '', cursor
            while len(collected) < len(target) and cursor < len(words):
                collected += words[cursor]['token']
                cursor += 1
            if collected != target:
                raise ValueError(ident + ': phrase boundary splits or misaligns a speech token: ' + phrase)
            a, b = words[first], words[cursor - 1]
            cues.append({'scene': ident, 'text': phrase,
                         'start': start + delay + a['offset'],
                         'end': min(end, start + delay + b['offset'] + b['duration'] + .12)})
        if cursor != len(words):
            raise ValueError(ident + ': unconsumed speech tokens')
        event_ids = set()
        for event in scene.get('events', []):
            event_id = event['id']
            if not isinstance(event_id, str) or not event_id or event_id in event_ids:
                raise ValueError(ident + ': event IDs must be nonempty and unique within a scene')
            event_ids.add(event_id)
            needle = normalized(event['text'])
            occurrence = event.get('occurrence', 1)
            if not needle or isinstance(occurrence, bool) or not isinstance(occurrence, int) or occurrence < 1:
                raise ValueError(ident + ': invalid event text or occurrence')
            position = -1
            for _ in range(occurrence):
                position = full.find(needle, position + 1)
                if position < 0:
                    raise ValueError(ident + ': event occurrence is absent: ' + event_id)
            if position not in token_positions:
                raise ValueError(ident + ': event must begin at a measured speech token: ' + event_id)
            time = start + delay + token_positions[position] + number(event.get('delta', 0), 'event.delta')
            if not start <= time < end:
                raise ValueError(ident + ': event falls outside its scene: ' + event_id)
            events.append({'scene': ident, 'id': event_id, 'text': event['text'],
                           'occurrence': occurrence, 'time': time})
    for a, b in zip(cues, cues[1:]):
        a['end'] = min(a['end'], b['start'] - .01)
    if any(not 0 <= c['start'] < c['end'] <= previous_end for c in cues):
        raise ValueError('Invalid subtitle range after overlap adjustment')
    return {'fps': int(fps), 'duration': previous_end,
            'frames': round(previous_end * fps), 'cues': cues, 'events': events}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--out-dir', required=True, type=Path)
    args = parser.parse_args()
    try:
        source = args.input.resolve()
        output = args.out_dir.resolve()
        if source in (output / 'aligned.json', output / '字幕.srt'):
            raise ValueError('Output must not overwrite the input plan')
        result = align(json.loads(source.read_text(encoding='utf-8')), source.parent)
        srt = '\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}'
                            for i, c in enumerate(result['cues'], 1)) + '\n'
        output.mkdir(parents=True, exist_ok=True)
        (output / 'aligned.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (output / '字幕.srt').write_text(srt, encoding='utf-8')
        print(json.dumps({'cues': len(result['cues']), 'events': len(result['events']),
                          'duration': result['duration'], 'output': str(output)}, ensure_ascii=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print('Alignment failed: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
