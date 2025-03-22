from web3 import Web3

# 이더리움 네트워크 연결 (예: Infura, Local Ganache)
w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"))

# 지갑 정보
my_address = "0xYourAddress"
private_key = "YourPrivateKey"

# 컴파일된 스마트 컨트랙트 ABI & Bytecode 로드
with open('contracts/NFT_abi.json') as f:
    nft_abi = f.read()

contract_address = "0xYourContractAddress"
nft_contract = w3.eth.contract(address=contract_address, abi=nft_abi)

# NFT 민팅 함수
def mint_nft(to_address):
    tx = nft_contract.functions.mint(to_address).build_transaction({
        'from': my_address,
        'nonce': w3.eth.get_transaction_count(my_address),
        'gas': 200000,
        'gasPrice': w3.to_wei('5', 'gwei')
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"NFT Minted! Transaction hash: {tx_hash.hex()}")

# 실행 예제
mint_nft("0xRecipientAddress")
