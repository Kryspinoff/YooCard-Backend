from contextlib import contextmanager

from sshtunnel import SSHTunnelForwarder

from app.core.config import settings


class SSHTunnelManager:
    def __init__(self):
        self.tunnel = None

    def start_tunnel(self):
        if not self.tunnel or not self.tunnel.is_active:
            self.tunnel = SSHTunnelForwarder(
                ssh_address_or_host=(settings.SSH_HOST, settings.SSH_PORT),
                ssh_username=settings.SSH_USERNAME,
                ssh_password=settings.SSH_PASSWORD,
                remote_bind_address=(settings.REMOTE_DB_HOST, settings.REMOTE_DB_PORT),
                local_bind_address=(settings.DB_HOST, settings.DB_PORT),
            )
            self.tunnel.start()

    def stop_tunnel(self):
        if self.tunnel and self.tunnel.is_active:
            self.tunnel.stop()

    @contextmanager
    def tunnel_context(self):
        self.start_tunnel()
        yield
        self.stop_tunnel()


ssh_tunnel_manager = SSHTunnelManager()
