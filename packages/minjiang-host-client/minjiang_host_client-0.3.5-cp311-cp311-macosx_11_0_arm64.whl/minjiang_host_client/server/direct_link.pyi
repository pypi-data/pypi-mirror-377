import multiprocessing
from _typeshed import Incomplete
from fastapi import Query as Query
from minjiang_host_client.base.channel import Channel as Channel
from minjiang_host_client.base.server import Server as Server
from minjiang_host_client.utils.direct_link import DirectLinkManager as DirectLinkManager
from pydantic import BaseModel

class UploadExpRequest(BaseModel):
    device_group_name: str
    space_name: str
    title: str
    description: str
    exp_obj: dict
    exp_id: int | None

class UploadExpResponse(BaseModel):
    direct_exp_id: int

class UploadResultRequest(BaseModel):
    direct_exp_id: int
    result: str

class UploadResultResponse(BaseModel):
    status: str

class GetResultResponse(BaseModel):
    result: str
    created_at: float
    expires_at: float

class DirectLinkServer(Server):
    server_host: str
    server_port: Incomplete
    group_name: Incomplete
    sock: Incomplete
    dev_mgr: Incomplete
    token: Incomplete
    process: multiprocessing.Process | None
    def __init__(self, name: str, group_name: str, in_chl: Channel = None, out_chl: Channel = None, direct_link_port: int = 6887) -> None: ...
    def finished_starting(self) -> None: ...
    def start_server(self): ...
    def cleanup(self) -> None: ...
    def stop(self) -> None: ...
    def __del__(self) -> None: ...
