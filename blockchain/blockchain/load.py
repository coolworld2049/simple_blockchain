import os
from uuid import uuid4

from blockchain.blockchain import Blockchain
from dotenv import load_dotenv

node_identifier = str(uuid4()).replace("-", "")

load_dotenv()

BLOCKCHAIN_NODES = os.getenv("BLOCKCHAIN_NODES")
BLOCKCHAIN_NODES = (
    set(BLOCKCHAIN_NODES.replace(" ", "").split(",")) if BLOCKCHAIN_NODES else None
)

blockchain = Blockchain(node=BLOCKCHAIN_NODES)
