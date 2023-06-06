import socket

from fastapi import FastAPI

from blockchain.load import node_identifier
from blockchain.routers import api_router


def get_application():
    application = FastAPI(
        title=f"blockchain-{socket.gethostname()}",
        description=f"node_id={node_identifier}",
    )
    application.include_router(api_router)
    return application


app = get_application()
