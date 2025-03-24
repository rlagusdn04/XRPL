from web3 import Web3
import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
import json

# EVM 설정
web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))
contract_address = "0xYourContractAddress"
contract_abi = [...]  # 위에서 정의한 ABI
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# XRPL 설정
testnet_url = "https://s.devnet.rippletest.net:51234"
xrpl_seed = "sEd7edi6UkZgLG7hKBGyB4Cq4shT6wJ"

def handle_event(event):
    # EVM 이벤트 처리
    print(f"Event detected: {event['args']}")
    
    # XRPL NFT 발행
    minter_wallet = Wallet.from_seed(xrpl_seed)
    client = JsonRpcClient(testnet_url)
    metadata = {
        "from": event["args"]["from"],
        "to": event["args"]["to"],
        "tokenId": event["args"]["tokenId"],
        "assetId": event["args"]["assetId"]
    }
    uri = xrpl.utils.str_to_hex(json.dumps(metadata))
    mint_tx = xrpl.models.transactions.NFTokenMint(
        account=minter_wallet.address,
        uri=uri,
        flags=0,
        transfer_fee=0,
        nftoken_taxon=1
    )
    response = xrpl.transaction.submit_and_wait(mint_tx, client, minter_wallet)
    print(f"NFT Minted: {response.result}")

# 실시간 감지
event_filter = contract.events.OwnershipTransferred.create_filter(fromBlock='latest')
while True:
    for event in event_filter.get_new_entries():
        handle_event(event)
    sleep(2)