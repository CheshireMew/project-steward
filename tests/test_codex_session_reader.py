from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "read_codex_session.py"
THREAD_ID = "11111111-2222-4333-8444-555555555555"


def run_reader(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )


def open_shared_writer(path: Path):
    if os.name != "nt":
        return path.open("r+b")

    import msvcrt
    from ctypes import wintypes

    create_file = ctypes.WinDLL("kernel32", use_last_error=True).CreateFileW
    create_file.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    )
    create_file.restype = wintypes.HANDLE
    handle = create_file(
        str(path),
        0x80000000 | 0x40000000,
        0x00000001 | 0x00000002 | 0x00000004,
        None,
        3,
        0x00000080,
        None,
    )
    if handle == ctypes.c_void_p(-1).value:
        raise OSError(ctypes.get_last_error(), "CreateFileW failed")
    descriptor = msvcrt.open_osfhandle(handle, os.O_RDWR | os.O_BINARY)
    return os.fdopen(descriptor, "r+b", closefd=True)


class CodexSessionReaderTests(unittest.TestCase):
    def test_active_writer_is_read_once_at_a_complete_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / f"rollout-sample-{THREAD_ID}.jsonl"
            complete = b'{"type":"first"}\n{"type":"second"}\n'
            incomplete = b'{"type":"still-writing"'
            source.write_bytes(complete + incomplete)

            with open_shared_writer(source) as writer:
                completed = run_reader(
                    "--thread-id",
                    THREAD_ID,
                    "--source",
                    str(source),
                    "--output-dir",
                    str(root / "snapshots"),
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                manifest = json.loads(completed.stdout)
                snapshot = Path(manifest["snapshot"])
                self.assertEqual(snapshot.read_bytes(), complete)
                self.assertEqual(manifest["complete_records"], 2)
                self.assertEqual(
                    manifest["trailing_incomplete_bytes"],
                    len(incomplete),
                )
                self.assertEqual(manifest["parse_errors"], 0)

                writer.seek(0, os.SEEK_END)
                writer.write(b'}\n')
                writer.flush()
                self.assertEqual(snapshot.read_bytes(), complete)

    def test_exact_identity_succeeds_and_duplicate_identity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_home = root / "codex"
            sessions = codex_home / "sessions"
            first = sessions / "2026" / "01" / "01"
            first.mkdir(parents=True)
            (first / f"rollout-a-{THREAD_ID}.jsonl").write_text(
                '{"type":"one"}\n',
                encoding="utf-8",
            )
            arguments = (
                "--thread-id",
                THREAD_ID,
                "--codex-home",
                str(codex_home),
                "--output-dir",
                str(root / "snapshots"),
            )
            completed = run_reader(*arguments)
            self.assertEqual(completed.returncode, 0, completed.stderr)

            second = sessions / "2026" / "01" / "02"
            second.mkdir(parents=True)
            (second / f"rollout-b-{THREAD_ID}.jsonl").write_text(
                '{"type":"two"}\n',
                encoding="utf-8",
            )
            ambiguous = run_reader(*arguments)
            self.assertEqual(ambiguous.returncode, 2)
            error = json.loads(ambiguous.stderr)["error"]
            self.assertEqual(error["code"], "session_record_ambiguous")


if __name__ == "__main__":
    unittest.main()
