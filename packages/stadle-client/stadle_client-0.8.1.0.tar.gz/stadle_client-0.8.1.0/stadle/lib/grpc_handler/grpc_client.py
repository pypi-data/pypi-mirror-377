import asyncio
import grpc
import pickle
import itertools
import logging
import stadle.lib.grpc_handler.comm_pb2 as comm_pb2
import stadle.lib.grpc_handler.comm_pb2_grpc as comm_pb2_grpc

import base64
import uuid

from stadle.lib.logging.logger import Logger

log = Logger("GRPC Client")

class GRPCClient:
    def __init__(self, protocol, cert_path=None, max_retries=20, retry_base_delay=2, chunk_size=1024 * 1024):
        self.protocol = protocol

        self.ssl = (protocol == 'https')
        self.client_credentials = None

        # if cert_path is not None:
        #     self.cert_path = cert_path
        #     self.ssl = True

        #     with open(self.cert_path, 'rb') as f:
        #         trusted_certs = f.read()

        #     self.client_credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.chunk_size = chunk_size

        self.address_channels = {}

        self.sending_cnt = 0

        if (self.ssl):
            with open(cert_path, 'rb') as f:
                self.tls_cert = f.read()

    async def _get_channel_and_stub(self, address):
        if (address not in self.address_channels):
            # print(self.address_channels)
            log.logger.debug(f"Creating new gRPC channel ({address})")

            channel_options = [
                ("grpc.http2.initial_window_size", 16 * 1024 * 1024),   # per-stream window
                ("grpc.http2.max_frame_size", 16 * 1024 * 1024),
                ("grpc.max_send_message_length", 100 * 1024 * 1024),
                ("grpc.max_receive_message_length", 100 * 1024 * 1024),
                ("grpc.max_concurrent_streams", 1024),                  # allow more simultaneous streams
            ]

            if self.ssl:
                log.logger.debug('Using secure channel')
                channel = grpc.aio.secure_channel(
                    address,
                    grpc.ssl_channel_credentials(root_certificates=self.tls_cert),
                    options=channel_options + [
                        ('grpc.ssl_target_name_override', 'tieset.com')
                    ]
                )
            else:
                channel = grpc.aio.insecure_channel(
                    address,
                    options=channel_options
                )

            stub = comm_pb2_grpc.CommServiceStub(channel)
            self.address_channels[address] = (channel, stub)

            log.logger.debug('Channel created')

        return self.address_channels[address]

    def _chunk_data(self, message_id, data, ack_only=False, heavy=False):
        chunks = [data[i:i+self.chunk_size] for i in range(0, len(data), self.chunk_size)]
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            yield comm_pb2.ChunkMessage(
                message_id=message_id,
                chunk_index=i,
                total_chunks=total,
                chunk_data=chunk,
                ack_only=ack_only,
                heavy=(heavy if i == 0 else False)  # only first chunk carries heavy
            )

    def is_sending(self):
        return self.sending_cnt > 0

    async def send(self, msg, address, ack_only=False, heavy=False):
        data = pickle.dumps(msg)
        retries = 0
        self.sending_cnt += 1

        try:
            while retries < self.max_retries:
                message_id = f"msg-{str(uuid.uuid4())}"
                log.logger.debug(f"Sending message {message_id} to {address}")

                try:
                    channel, stub = await self._get_channel_and_stub(address)

                    async def req_stream():
                        for chunk in self._chunk_data(message_id, data, ack_only=ack_only, heavy=heavy):
                            yield chunk

                    call = stub.ChunkedMessageStream(req_stream(), wait_for_ready=True, timeout=600.0)

                    chunks = {}
                    total = None
                    early_ack_received = False

                    async for resp in call:
                        if resp.message_id != message_id:
                            continue

                        # Early ack or QUEUE_FULL handling
                        if resp.ack_only:
                            try:
                                obj = pickle.loads(resp.chunk_data)
                                if obj == {"ack": True}:
                                    early_ack_received = True
                                    # log.logger.info(f"Early ACK received for {message_id}")
                                elif obj.get("status") == "QUEUE_FULL":
                                    log.logger.warning(f"Server queue full for {message_id}, retrying...")
                                    retries += 1
                                    await asyncio.sleep(self.retry_base_delay * retries)
                                    break  # retry loop with new message_id
                            except Exception:
                                pass  # ignore if partial/unpicklable
                            continue

                        # Collect chunks for final response
                        chunks[resp.chunk_index] = resp.chunk_data
                        total = resp.total_chunks

                        if total is not None and len(chunks) == total:
                            full = b''.join(chunks[i] for i in range(total))
                            resp_obj = pickle.loads(full)

                            # If server sent an error status, raise
                            if isinstance(resp_obj, dict) and resp_obj.get("status") in ("ERROR", "FATAL_ERROR"):
                                raise RuntimeError(resp_obj.get("msg", "Server error"))

                            return resp_obj  # Final response

                    # If loop ended without returning, retry
                    retries += 1
                    await asyncio.sleep(self.retry_base_delay * retries)

                except grpc.aio.AioRpcError as e:
                    retries += 1
                    log.logger.warning(f"Retry {retries}/{self.max_retries} for msg {message_id}: {e.code()} - {e.details()}:{e.debug_error_string()}")
                    await asyncio.sleep(self.retry_base_delay * retries)

            raise RuntimeError(f"Failed to send message after {self.max_retries} retries.")

        finally:
            self.sending_cnt -= 1
