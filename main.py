import json
import nest_asyncio
import xrpl.utils
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.account import get_balance
from xrpl.models.requests import ServerInfo
from xrpl.models.transactions import NFTokenMint
from xrpl.transaction import submit_and_wait

# asyncio event loop 문제 해결
nest_asyncio.apply()

def register_nft_with_root_network(nft_details: dict):
    #NFT를 가상 API(The Root Network)에 등록
    print("NFT가 The Root Network에 등록되었습니다:", nft_details)

def main():
    # XRPL 테스트넷에 연결
    testnet_url = "https://s.altnet.rippletest.net:51234/"
    client = JsonRpcClient(testnet_url)

    # 서버 정보 확인
    server_info = client.request(ServerInfo())
    print("서버 정보:", server_info.result)

    # 새로운 테스트넷 지갑 생성 (Faucet 이용)
    wallet = generate_faucet_wallet(client)
    print(f"지갑 주소: {wallet.classic_address}")
    print(f"비밀키: {wallet.seed}")

    # 잔액 확인
    balance = get_balance(wallet.classic_address, client)
    print(f"잔액: {balance} XRP")

    # 로컬 metadata.json 파일 읽기
    with open("metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    # JSON 데이터를 문자열로 변환한 후, hex로 인코딩 (NFT 민팅 시 uri 필드에 사용)
    metadata_str = json.dumps(metadata)
    metadata_hex = xrpl.utils.str_to_hex(metadata_str)

    # NFT 민팅 트랜잭션 생성
    nft_mint_tx = NFTokenMint(
        account=wallet.classic_address,
        nftoken_taxon=0,  # NFT 분류 (0: 기본 분류)
        uri=metadata_hex,
        flags=8  # 8: Transferable(양도가능) NFT 설정
    )
    print("NFT 민팅 중...")
    nft_response = submit_and_wait(nft_mint_tx, client, wallet)
    print("NFT 민팅 결과:", nft_response.result)

    # NFT 민팅 결과가 성공적이면, The Root Network에 등록
    if "hash" in nft_response.result:
        nft_hash = nft_response.result["hash"]
        nft_details = {
            "nft_hash": nft_hash,
            "metadata": metadata,  # JSON 파일 내용
            "owner": wallet.classic_address,
        }
        register_nft_with_root_network(nft_details)
    else:
        print("NFT 등록 실패")

if __name__ == "__main__":
    main()
