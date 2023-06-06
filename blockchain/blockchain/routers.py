from pprint import pprint
from typing import Any

from fastapi import APIRouter
from fastapi.params import Query
from loguru import logger
from pydantic import BaseModel

from blockchain.load import blockchain, node_identifier

api_router = APIRouter()


class Transaction(BaseModel):
    sender: Any
    recipient: Any
    amount: Any


@api_router.get("/mine")
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.create_transaction(sender="0", recipient=node_identifier, amount=1)

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    logger.debug(f"new_block: {block}")

    response = {
        "index": block["index"],
        "transaction": block["transaction"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }
    return response


@api_router.get("/transaction")
def current_transactions():
    return blockchain.current_transaction


@api_router.post("/transaction")
def create_transaction(transaction: Transaction):
    index = blockchain.create_transaction(
        transaction.sender, transaction.recipient, transaction.amount
    )
    response = {"message": f"Transaction will be added to Block {index}"}
    return response


@api_router.get("/chain")
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return response


@api_router.get("/node")
def get_nodes():
    response = {
        "node": {i: node for i, node in enumerate(blockchain.node)},
    }
    return response


@api_router.post("/node")
def register_nodes(address: str = Query(description="`http://node_ip:node_port`")):
    message = blockchain.register_node(address)
    response = {
        "message": message,
    }
    return response


@api_router.get("/node/consensus")
def consensus():
    replaced = blockchain.consensus()
    if replaced:
        response = {
            "message": "Our chain was replaced",
            "new_chain": blockchain.chain,
        }
    else:
        response = {
            "message": "Our chain is authoritative",
            "chain": blockchain.chain,
        }
    return response
