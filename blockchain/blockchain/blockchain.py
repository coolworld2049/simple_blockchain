import hashlib
import json
from time import time
from urllib.parse import urlparse

import requests
from loguru import logger


class Blockchain:
    def __init__(self, node=None, chain=None):
        if chain is None:
            chain = []
        if node is None:
            node = set()
        self.current_transaction = []
        self.chain = chain
        self.node = node
        self.new_block(previous_hash="1", proof=100)

    def register_node(self, address):
        try:
            response = requests.get(f"{address}/node")
            if response.status_code == 200:
                parsed_url = urlparse(address)
                if parsed_url.netloc:
                    self.node.add(parsed_url.netloc)
                elif parsed_url.path:
                    self.node.add(parsed_url.path)
                else:
                    raise
                return f"The URL {address} is reachable"
            else:
                return f"The URL {address} returned a status code of {response.status_code}"
        except Exception as e:
            raise ValueError(f"An error occurred while trying to reach the URL: {e}")

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            logger.debug(f"{current_index}: last_block: {last_block}")
            logger.debug(f"{current_index}: block: {block}")

            last_block_hash = self.hash(last_block)
            if block["previous_hash"] != last_block_hash:
                return False

            if not self.valid_proof(
                last_block["proof"], block["proof"], last_block_hash
            ):
                return False

            last_block = block
            current_index += 1

        return True

    def consensus(self):
        new_chain = None
        max_length = len(self.chain)
        for node in self.node:
            try:
                response = requests.get(f"http://{node}/chain")
            except Exception as e:
                logger.error(f"node:{node}, error: {e.args}")
                continue
            logger.debug(f"node:{node}, status_code: {response.status_code}")
            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]
                is_chain_valid = self.valid_chain(chain)
                logger.debug(f"node:{node}, is_chain_valid: {is_chain_valid}")
                if length > max_length and is_chain_valid:
                    max_length = length
                    new_chain = chain
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False

    def new_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transaction": self.current_transaction,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transaction = []
        self.chain.append(block)
        return block

    def create_transaction(self, sender, recipient, amount):
        self.current_transaction.append(
            {
                "sender": sender,
                "recipient": recipient,
                "amount": amount,
            }
        )
        return self.last_block["index"] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
        """
        last_proof = last_block["proof"]
        last_hash = self.hash(last_block)
        is_valid, guess_hash = False, None
        proof = 0
        while is_valid is False:
            is_valid, guess_hash = self.valid_proof(last_proof, proof, last_hash)
            proof += 1
        logger.debug(f"last_proof: {last_proof}, proof: {proof}, last_hash: {last_hash}")
        logger.debug(f"guess_hash: {guess_hash}")
        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        guess = f"{last_proof}{proof}{last_hash}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000", guess_hash
