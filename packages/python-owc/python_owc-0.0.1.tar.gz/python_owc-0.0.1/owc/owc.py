from __future__ import annotations

import asyncio
import datetime


owc_processes = dict()


def end_process(uuid: str) -> None:
    owc_processes[uuid].stop_process = True
    owc_processes.pop(uuid)


def add_process(uuid: str, process: OWC) -> None:
    owc_processes[uuid] = process


class OWC:
    def __init__(self, uuid: str, expires: int = None, delay: int = 60) -> None:
        self.expires = None
        if expires:
            self.expires = datetime.datetime.now() + datetime.timedelta(seconds=expires)
        self.delay = delay
        self.uuid = uuid
        self.stop_process = False
        add_process(self.uuid, self)

    def verify_stop_conditions(self) -> None:
        if self.expires and datetime.datetime.now() >= self.expires:
            self.stop_process = True
            return

    def __aiter__(self) -> OWC:
        return self

    async def __anext__(self) -> None:
        self.verify_stop_conditions()
        if self.stop_process:
            end_process(self.uuid)
            raise StopAsyncIteration
        print("from owc")
        await asyncio.sleep(self.delay)

    def __repr__(self) -> str:
        return "OWC()"
