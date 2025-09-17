# Module Name: connection/sftp_paramiko.py
# Author: (wattleflow@outlook.com)
# Copyright: (c) 2022-2024 WattleFlow
# License: Apache 2 Licence
# Description: This modul contains concrete sftp connection class.


# --------------------------------------------------------------------------- #
# IMPORTANT:
# This connection requires the paramiko library.
# The library is used for the connection with a SFTP server.
#   pip install paramiko
# --------------------------------------------------------------------------- #

from contextlib import contextmanager
from paramiko import (
    AutoAddPolicy,
    AuthenticationException,
    BadHostKeyException,
    SSHClient,
    SFTPClient,
    SSHException,
)
from typing import Generator
from wattleflow.core import T
from wattleflow.concrete import AuditException, GenericConnection
from wattleflow.constants import Event


class SFTPConnectionError(AuditException):
    pass


class SFTParamiko(GenericConnection[SFTPClient]):
    @contextmanager
    def connect(self) -> Generator[T, None, None]:
        self.debug(
            msg=Event.Connecting.value,
            connection=self._connection_name,
            status=Event.Authenticating.value,
        )

        try:
            self._engine = SSHClient()
            self._engine.set_missing_host_key_policy(AutoAddPolicy())
            self._engine.connect(
                hostname=self.host,
                port=int(self.port),
                username=self.user,
                password=self.password,
                passphrase=self.passphrase,
                key_filename=self.key_filename,
                look_for_keys=self.look_for_keys,
            )  # type: ignore

            self._connection: SFTPClient = self._engine.open_sftp()
            self._connected = True

            self.info(
                msg=Event.Connected.value,
                connected=self._connected,
            )

            yield self._connection

        except AuthenticationException as e:
            raise SFTPConnectionError(
                caller=self, error=f"Authentication failed: {e}"
            ) from e
        except BadHostKeyException as e:
            raise SFTPConnectionError(
                caller=self, error=f"Bad host exception: {e}"
            ) from e
        except SSHException as e:
            raise SFTPConnectionError(caller=self, error=f"SSH Exception: {e}") from e
        except Exception as e:
            raise SFTPConnectionError(
                caller=self, error=f"Connection error: {e}"
            ) from e

    def disconnect(self):
        self.debug(
            msg=Event.Disconnecting.value,
            status=f"{'connected' if self._connected else 'disconnected'}",
        )

        if not self._connected:
            return

        if self._connection:
            self._connection.close()

        self._client.close()
        self._connected = False

        self.debug(
            msg=Event.Disconnected.value,
            connected=self._connected,
        )
