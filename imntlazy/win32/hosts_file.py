import os
import subprocess

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
BEGIN_MARKER = "# imntlazy Block Begin"
END_MARKER = "# imntlazy Block End"


def read_hosts() -> str:
    if not os.path.exists(HOSTS_PATH):
        return ""
    with open(HOSTS_PATH, "r", encoding="ascii", errors="replace") as f:
        return f.read()


def write_hosts(content: str) -> None:
    # Remove read-only attribute if set
    try:
        attrs = os.stat(HOSTS_PATH).st_file_attributes
        import stat
        os.chmod(HOSTS_PATH, stat.S_IWRITE | stat.S_IREAD)
    except Exception:
        pass
    with open(HOSTS_PATH, "w", encoding="ascii", errors="replace") as f:
        f.write(content)


def _remove_section_from_string(content: str) -> str:
    begin_idx = content.find(BEGIN_MARKER)
    if begin_idx < 0:
        return content
    end_idx = content.find(END_MARKER, begin_idx)
    if end_idx < 0:
        return content
    end_idx += len(END_MARKER)
    before = content[:begin_idx].rstrip()
    after = content[end_idx:].lstrip()
    if before and after:
        return before + "\n" + after
    return before or after


def append_block_section(domains: list[str]) -> None:
    content = read_hosts()
    content = _remove_section_from_string(content)

    lines = [BEGIN_MARKER]
    for d in domains:
        d = d.strip().lower()
        if not d:
            continue
        lines.append(f"127.0.0.1  {d}")
        if not d.startswith("www."):
            lines.append(f"127.0.0.1  www.{d}")
    lines.append(END_MARKER)

    if content and not content.endswith("\n"):
        content += "\n"
    content += "\n" + "\n".join(lines) + "\n"
    write_hosts(content)


def remove_block_section() -> None:
    content = read_hosts()
    content = _remove_section_from_string(content)
    write_hosts(content)


def flush_dns() -> None:
    try:
        subprocess.run(
            ["ipconfig", "/flushdns"],
            capture_output=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except Exception:
        pass
