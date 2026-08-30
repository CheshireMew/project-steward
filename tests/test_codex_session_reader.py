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


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


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
                for projection in manifest["projections"].values():
                    self.assertEqual(projection["records"], 0)
                    self.assertTrue(Path(projection["path"]).is_file())

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

    def test_projections_separate_public_context_and_process_without_reasoning(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / f"rollout-projection-{THREAD_ID}.jsonl"
            records = [
                {
                    "type": "response_item",
                    "timestamp": "2026-01-01T00:00:00Z",
                    "payload": {
                        "type": "message",
                        "id": "public-user",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "real request"}],
                    },
                },
                {
                    "type": "response_item",
                    "timestamp": "2026-01-01T00:00:01Z",
                    "payload": {
                        "type": "message",
                        "id": "injected-user-role",
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "<environment_context>"}
                        ],
                    },
                },
                {
                    "type": "response_item",
                    "timestamp": "2026-01-01T00:00:02Z",
                    "payload": {
                        "type": "message",
                        "id": "developer-context",
                        "role": "developer",
                        "content": [{"type": "input_text", "text": "host policy"}],
                    },
                },
                {
                    "type": "event_msg",
                    "timestamp": "2026-01-01T00:00:03Z",
                    "payload": {
                        "type": "item_completed",
                        "item": {
                            "type": "UserMessage",
                            "id": "public-user",
                            "client_id": "client-user",
                            "content": {"type": "text", "text": "real request"},
                        },
                    },
                },
                {
                    "type": "event_msg",
                    "timestamp": "2026-01-01T00:00:04Z",
                    "payload": {
                        "type": "item_completed",
                        "item": {
                            "type": "AgentMessage",
                            "id": "public-agent",
                            "phase": "commentary",
                            "content": {"type": "Text", "text": "visible update"},
                        },
                    },
                },
                {
                    "type": "event_msg",
                    "timestamp": "2026-01-01T00:00:05Z",
                    "payload": {
                        "type": "item_completed",
                        "item": {
                            "type": "Reasoning",
                            "id": "hidden-reasoning",
                            "raw_content": "must never enter a projection",
                        },
                    },
                },
                {
                    "type": "event_msg",
                    "timestamp": "2026-01-01T00:00:06Z",
                    "payload": {
                        "type": "item_completed",
                        "item": {
                            "type": "CommandExecution",
                            "id": "command-1",
                            "status": "failed",
                            "exit_code": 1,
                            "command": "verify target",
                            "stdout": "failed output",
                            "stderr": "",
                        },
                    },
                },
                {
                    "type": "event_msg",
                    "timestamp": "2026-01-01T00:00:07Z",
                    "payload": {
                        "type": "item_completed",
                        "item": {
                            "type": "FileChange",
                            "id": "change-1",
                            "status": "completed",
                            "changes": {"example.py": {"type": "update"}},
                        },
                    },
                },
                {
                    "type": "event_msg",
                    "timestamp": "2026-01-01T00:00:08Z",
                    "payload": {
                        "type": "item_completed",
                        "item": {
                            "type": "ContextCompaction",
                            "id": "compaction-1",
                        },
                    },
                },
            ]
            source.write_text(
                "".join(json.dumps(record) + "\n" for record in records),
                encoding="utf-8",
            )

            completed = run_reader(
                "--thread-id",
                THREAD_ID,
                "--source",
                str(source),
                "--output-dir",
                str(root / "snapshots"),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            projections = json.loads(completed.stdout)["projections"]
            public = read_jsonl(Path(projections["public_dialogue"]["path"]))
            context = read_jsonl(Path(projections["context_sources"]["path"]))
            process = read_jsonl(Path(projections["process_events"]["path"]))

            self.assertEqual(
                [(item["speaker"], item["message_id"]) for item in public],
                [("user", "public-user"), ("assistant", "public-agent")],
            )
            self.assertEqual(
                {item["message_id"] for item in context},
                {"injected-user-role", "developer-context"},
            )
            self.assertEqual(
                [item["item_type"] for item in process],
                ["CommandExecution", "FileChange", "ContextCompaction"],
            )
            self.assertEqual(process[0]["record_line"], 7)
            self.assertEqual(process[0]["status"], "failed")
            self.assertEqual(process[0]["item"]["exit_code"], 1)
            combined = "\n".join(
                Path(projection["path"]).read_text(encoding="utf-8")
                for projection in projections.values()
            )
            self.assertNotIn("must never enter a projection", combined)
            self.assertEqual(projections["public_dialogue"]["records"], 2)
            self.assertEqual(projections["context_sources"]["records"], 2)
            self.assertEqual(projections["process_events"]["records"], 3)
            self.assertEqual(
                projections["public_dialogue"]["source_record_cursor"],
                {"first_line": 4, "last_line": 5},
            )
            self.assertEqual(
                projections["context_sources"]["source_record_cursor"],
                {"first_line": 2, "last_line": 3},
            )
            self.assertEqual(
                projections["process_events"]["source_record_cursor"],
                {"first_line": 7, "last_line": 9},
            )

    def test_malformed_public_message_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / f"rollout-malformed-{THREAD_ID}.jsonl"
            source.write_text(
                json.dumps(
                    {
                        "type": "event_msg",
                        "payload": {
                            "type": "item_completed",
                            "item": {"type": "UserMessage", "id": "broken"},
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            completed = run_reader(
                "--thread-id",
                THREAD_ID,
                "--source",
                str(source),
                "--output-dir",
                str(root / "snapshots"),
            )
            self.assertEqual(completed.returncode, 2)
            error = json.loads(completed.stderr)["error"]
            self.assertEqual(error["code"], "session_projection_invalid")


if __name__ == "__main__":
    unittest.main()
