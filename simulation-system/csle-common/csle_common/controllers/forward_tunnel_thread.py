import threading
import time
from csle_common.controllers.forward_ssh_server import ForwardSSHServer
from csle_common.controllers.forward_ssh_handler import ForwardSSHHandler


class ForwardTunnelThread(threading.Thread):
    """
    Thread that starts up a SSH tunnel that forwards a local port to a remote machine
    """

    def __init__(self, local_port : int, remote_host : str, remote_port: int, transport):
        super().__init__()
        self.local_port = local_port
        self.remote_host = remote_host
        self.transport = transport
        self.remote_port = remote_port
        self.forward_server = ForwardSSHServer(("", local_port), ForwardSSHHandler)
        self.forward_server.ssh_transport = self.transport
        self.forward_server.chain_host = self.remote_host
        self.forward_server.chain_port = self.remote_port
        self.daemon = True

    def run(self):
        self.forward_server.serve_forever()

    def shutdown(self):
        self.forward_server.shutdown()
        time.sleep(0.5) # wait for server to shutdown