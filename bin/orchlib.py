"""Shared by orch-new and orch-resume: names, colors and the stop/resume steps of a background session."""
import glob
import json
import os
import re
import subprocess
import sys
import time

COLORS = ["blue", "purple", "orange", "cyan", "pink", "green", "red", "yellow"]
STATE = os.path.join(os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state"),
                     "claude-orchestrator", "topics.json")
SEP = " › "
JOBS = os.path.expanduser("~/.claude/jobs")
TRAILING = {"a", "al", "con", "de", "del", "el", "en", "la", "las", "lo", "los", "o", "para",
            "por", "sin", "un", "una", "y", "and", "for", "in", "of", "on", "the", "to", "with"}


def die(tool, msg):
    sys.exit(f"{tool}: {msg}")


def shorten(text, max_words, max_chars):
    """Only cut to fit: the caller writes a name that says what the task is about. Splitting at
    ':' kept prefixes like "Tuqui" from "Tuqui: catálogo ..." and lost the meaning."""
    m = re.match(r"\s*(\d+)\s+(.*)", text)
    tid, text = (m.group(1), m.group(2)) if m else (None, text)
    text = re.sub(r"^\s*(\[[^\]]*\]\s*)+", "", text).strip()
    words = text.split()[:max_words]
    while words and len(" ".join(words)) > max_chars:
        words.pop()
    while len(words) > 1 and words[-1].lower() in TRAILING:
        words.pop()
    short = " ".join(words) or text[:max_chars]
    return f"{tid} {short}" if tid else short


def full_name(name, topic):
    name = shorten(name, 7, 40)
    topic = shorten(topic, 3, 20) if topic else ""
    return topic, (f"{topic}{SEP}{name}" if topic else name)


def agents(all_=False, strict=False):
    """Sessions from `claude agents --json`; on unreadable output, [] (or None with strict)."""
    cmd = ["claude", "agents", "--json"] + (["--all"] if all_ else [])
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        return json.loads(out.stdout or "[]")
    except ValueError:
        return None if strict else []


def least_used(used):
    return min(COLORS, key=lambda c: (used.count(c), COLORS.index(c)))


def topic_color(topic, dry):
    try:
        with open(STATE) as f:
            topics = json.load(f)
    except (OSError, ValueError):
        topics = {}
    live = {s.get("name", "").split(SEP)[0] for s in agents() if SEP in (s.get("name") or "")}
    used = [topics[t] for t in live if t in topics and t != topic]
    color = topics.get(topic)
    if color not in COLORS or color in used:
        color = least_used(used)
    if not dry:
        topics[topic] = color
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        with open(STATE, "w") as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
    return color


def free_color(skip=""):
    """A session with no topic still gets a color: the one least used by the other live sessions."""
    return least_used([saved(s["id"], "color") for s in agents() if s.get("id") and s["id"] != skip])


def pick_color(color, topic, dry, skip=""):
    return color or (topic_color(topic, dry) if topic else free_color(skip))


def saved(job, key):
    """What Claude Code saved for a background session ("name", "color"): what agent view shows."""
    try:
        with open(os.path.join(JOBS, job, "state.json")) as f:
            return json.load(f).get(key) or ""
    except (OSError, ValueError):
        return ""


def launch(tool, args, cwd):
    out = subprocess.run(args, capture_output=True, text=True, cwd=cwd, timeout=120)
    text = out.stdout + out.stderr
    m = re.search(r"attach ([0-9a-f]{8})", text)
    if m:
        return m.group(1)
    if "not trusted" in text:
        die(tool, f"Claude Code does not trust {cwd} yet. Open `claude` once in that folder "
                  f"(cd {cwd} && claude), accept the trust prompt, exit, and run this again.")
    die(tool, f"claude did not start the session:\n{text}")


def row(job):
    return next((s for s in agents(all_=True) if s.get("id") == job), None)


def wait_saved(job, key, value, seconds):
    """Wait until `key` is saved as `value` and the session is idle; return its full session id.

    A new session reports status idle before it reads its first message, and the screen shows
    "Session color set" before the color is saved: stopping it then loses the color.
    """
    deadline = time.time() + seconds
    while time.time() < deadline:
        if saved(job, key) == value:
            s = row(job)
            if s and s.get("status") == "idle":
                return s.get("sessionId")
        time.sleep(1)
    return None


def last_color(session_id):
    """The last `/color` a session ran, from its transcripts (orphaned parts included, oldest first)."""
    color = ""
    paths = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session_id}*.jsonl"))
    for p in sorted(paths, key=os.path.getmtime):
        with open(p, errors="replace") as f:
            for line in f:
                if line.startswith('{"type":"agent-color"'):
                    try:
                        color = json.loads(line).get("agentColor") or color
                    except ValueError:
                        pass
    return color if color in COLORS else ""


def wait_first_color(job, color, seconds):
    """Wait until a new session ran its first `/color` and is idle; return its full session id.

    A new session writes the color to its transcript but often not to state.json until it restarts,
    so the transcript counts too; the caller restarts it with `/color` again when state.json lacks it.
    """
    deadline = time.time() + seconds
    while time.time() < deadline:
        s = row(job)
        sid = (s or {}).get("sessionId")
        if sid and s.get("status") == "idle" and (saved(job, "color") == color
                                                  or last_color(sid) == color):
            return sid
        time.sleep(1)
    return None


def stop(tool, job, seconds=20):
    """`claude stop` returns before the process exits; resuming before that starts a copy. A session
    in state done keeps that state after the stop: what counts is that it has no process."""
    subprocess.run(["claude", "stop", job], capture_output=True, timeout=30)
    deadline = time.time() + seconds
    while time.time() < deadline:
        rows = agents(all_=True, strict=True)
        s = next((r for r in rows or [] if r.get("id") == job), None)
        if rows is not None and (not s or s.get("state") == "stopped" or not s.get("pid")):
            time.sleep(0.5)
            return
        time.sleep(0.5)
    die(tool, f"session {job} did not stop in {seconds}s")


def resume(tool, session_id, message, cwd, job=None):
    """Continue a session in the background with `message` as the user's next message.

    No flags here: a background session keeps its saved options, and new flags would start a copy
    with another id instead of continuing this one.
    """
    again = launch(tool, ["claude", "--bg", "--resume", session_id, message], cwd)
    if job and again != job:
        die(tool, f"the message went to a copy ({again}) instead of {job}; check both with `claude agents`")
    return again


def apply(tool, job, session_id, command, key, value, cwd, seconds=60, tries=2):
    """Send a slash command that sets `key` (stop → resume → wait until saved), up to `tries` times.

    A command can run without being saved ("Session color set to" in the transcript only): a second
    stop and resume saves it.
    """
    for attempt in range(1, tries + 1):
        if attempt > 1 or (row(job) or {}).get("pid"):
            stop(tool, job)
        job = resume(tool, session_id, command, cwd, job)
        if wait_saved(job, key, value, seconds):
            return job
        if attempt < tries:
            print(f"{tool}: {job} did not save `{command}` in {seconds}s; trying once more", file=sys.stderr)
    die(tool, f"session {job} did not save `{command}`; check `claude logs {job}`")


def find_transcript(session_id):
    """The transcript of a session and the folder it was started in (where --resume finds it)."""
    paths = [p for p in glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session_id}*.jsonl"))
             if ".orphaned-" not in p]
    if len(paths) != 1:
        return None, None
    with open(paths[0], errors="replace") as f:
        for line in f:
            if '"cwd"' in line:
                try:
                    cwd = json.loads(line).get("cwd")
                except ValueError:
                    continue
                if cwd:
                    return os.path.basename(paths[0])[:-6], cwd
    return os.path.basename(paths[0])[:-6], None
