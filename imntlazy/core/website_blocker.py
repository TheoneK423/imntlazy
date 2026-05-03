from ..win32.hosts_file import append_block_section, remove_block_section, flush_dns


class WebsiteBlocker:
    def __init__(self):
        self._blocked_domains: list[str] = []
        self._is_blocking = False

    @property
    def is_blocking(self) -> bool:
        return self._is_blocking

    def load_domains(self, domains: list[str]) -> None:
        self._blocked_domains = list(domains)

    def block(self):
        if self._is_blocking:
            return
        # Clean stale markers first, then write fresh
        remove_block_section()
        append_block_section(self._blocked_domains)
        flush_dns()
        self._is_blocking = True

    def unblock(self):
        if not self._is_blocking:
            # Still clean up in case of stale entries from a crash
            remove_block_section()
            flush_dns()
            return
        remove_block_section()
        flush_dns()
        self._is_blocking = False
