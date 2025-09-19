import asyncio
import logging
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import msgspec.json

try:
    import fastnanoid
    import zmq.asyncio
    import tnetstring

    _zmq_available = True
except ModuleNotFoundError:
    _zmq_available = False

from programming_game.protocol import ClientProtocol

logger = logging.getLogger(__name__)


@asynccontextmanager
async def setup_pyzmq(client: "ZMQMixin", zmq_event_push_url: str) -> AsyncGenerator[None, None]:
    """
    Ein asynchroner Context Manager, der ZMQ-Sockets einrichtet und einen
    Hintergrund-Task zum Empfangen von Nachrichten startet.
    """
    logger.info("---> Betrete PyZMQ Context Manager")

    ctx = zmq.asyncio.Context()
    receiver_task: asyncio.Task | None = None

    try:
        if zmq_event_push_url:
            # PUSH-Socket
            client.socket_push = ctx.socket(zmq.PUSH)
            client.socket_push.connect(zmq_event_push_url)
            logger.info(f"Sender-Socket (PUSH) an '{zmq_event_push_url}' verbunden.")

        # PUB-Socket
        client.socket_publish = ctx.socket(zmq.PUB)
        client.socket_publish.bind("inproc://game_events")
        logger.info("Sender-Socket (PUB) an 'inproc://game_events' gebunden.")

        # SUBSCRIBE-Socket zum Empfangen
        client.socket_subscribe = ctx.socket(zmq.SUBSCRIBE)
        client.socket_subscribe.connect("inproc://game_events")
        logger.info("Receiver-Socket (SUBSCRIBE) mit 'inproc://game_events' verbunden.")

        # Starte den Nachrichtenempfänger als Hintergrund-Task
        receiver_task = None  # asyncio.create_task(message_receiver_loop(client))

        # Kontrolle an den `async with`-Block übergeben
        yield

    finally:
        logger.info("<--- Verlasse PyZMQ Context Manager")

        # Beende den Hintergrund-Task sicher
        if receiver_task and not receiver_task.done():
            receiver_task.cancel()
            try:
                await receiver_task
            except asyncio.CancelledError:
                pass  # Erwartetes Verhalten beim Abbrechen

        # Sockets sicher schließen
        if client.socket_push and not client.socket_push.closed:
            client.socket_push.close()
            logger.info("Push-Socket geschlossen.")
        if client.socket_publish and not client.socket_publish.closed:
            client.socket_publish.close()
            logger.info("Sender-Socket geschlossen.")
        if client.socket_subscribe and not client.socket_subscribe.closed:
            client.socket_subscribe.close()
            logger.info("Receiver-Socket geschlossen.")

        # Kontext beenden
        if not ctx.closed:
            ctx.term()
            logger.info("ZMQ-Kontext beendet.")

        # Referenzen im Client-Objekt aufräumen
        client.sender = None
        client.receiver = None
        logger.info("Client-Referenzen aufgeräumt.")


if _zmq_available:

    class ZMQMixin(ClientProtocol):
        socket_push: zmq.asyncio.Socket | None = None
        socket_publish: zmq.asyncio.Socket | None = None
        socket_subscribe: zmq.asyncio.Socket | None = None

        def __init__(self, zmq: bool = False, zmq_event_push_url: str | None = None, **kwargs):
            super().__init__(**kwargs)
            self._zmq_topic = fastnanoid.generate(size=5)
            if zmq:
                self._zmq_enabled = True
                self.context_managers.append(setup_pyzmq(self, zmq_event_push_url))
            else:
                logger.warning("No ZMQ socket available to send binary data.")

        async def zmq_push_event(self, message: str, channel: str | None = None):
            if self.socket_push:
                msg = {
                    "channel": channel or self._zmq_topic,
                    "id": fastnanoid.generate(size=8),
                    "formats": {"ws-message": {"content": message}},
                }
                encoded = b"J" + msgspec.json.encode(msg)
                await self.socket_push.send(encoded)
            else:
                logger.warning("No ZMQ socket available to send binary data.")

        async def zmq_send_action(self, topic: str, action: str):
            if self.socket_push:
                msg = {
                    "channel": topic,
                    "id": uuid.uuid4().hex,
                    "formats": {"ws-message": {"action": action}},
                }
                encoded = b"J" + msgspec.json.encode(msg)
                await self.socket_push.send(encoded)
            else:
                logger.warning("No ZMQ socket available to send binary data.")

        async def zmq_send_binary(self, topic: str, data: bytes):
            if self.socket_push:
                # Use tnetstring format for better performance (no ID needed)
                msg = {
                    b"channel": topic.encode(),
                    b"formats": {
                        b"ws-message": {
                            b"content-bin": data  # Direct binary data in tnetstring
                        }
                    },
                }

                # Encode with tnetstring and 'T' prefix
                encoded = b"T" + tnetstring.dumps(msg)
                await self.socket_push.send(encoded)
            else:
                logger.warning("No ZMQ socket available to send binary data.")

        @property
        def zmq_topic(self):
            return self._zmq_topic

else:

    class ZMQMixin(ClientProtocol):
        pass
