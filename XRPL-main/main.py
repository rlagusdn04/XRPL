# 필요한 패키지 설치 (Notebook 등 환경에서 실행할 경우)
# !pip install nest_asyncio xrpl-py

import nest_asyncio
nest_asyncio.apply()

# 동기 클라이언트 임포트
from xrpl.clients import JsonRpcClient
# 비동기 클라이언트는 xrpl.asyncio.clients에서 import 합니다.
from xrpl.asyncio.clients import AsyncJsonRpcClient

from xrpl.wallet import generate_faucet_wallet, Wallet
from xrpl.account import get_balance
from xrpl.models.requests import ServerInfo
from xrpl.models.transactions import NFTokenMint, Payment
from xrpl.transaction import submit_and_wait, autofill_and_sign
import xrpl.utils
import asyncio

# 추가 XRPL 모듈
from xrpl.core import keypairs, addresscodec
from xrpl.ledger import get_fee
from xrpl.asyncio.transaction import submit_and_wait as async_submit_and_wait
from xrpl.asyncio.ledger import get_latest_validated_ledger_sequence
from xrpl.asyncio.account import get_next_valid_seq_number

def register_nft_with_root_network(nft_details: dict):
    """
    NFT를 가상 API(The Root Network)에 등록하는 함수.
    실제 API 요청은 해당 문서를 참고하여 구현하세요.
    """
    print("NFT가 The Root Network에 등록되었습니다:", nft_details)

def nft_minting_example():
    # XRPL 테스트넷 연결
    testnet_url = "https://s.altnet.rippletest.net:51234/"
    client = JsonRpcClient(testnet_url)

    # 서버 정보 확인
    server_info = client.request(ServerInfo())
    print("서버 정보:", server_info.result)

    # Faucet을 이용해 새로운 테스트 지갑 생성
    wallet = generate_faucet_wallet(client)
    print(f"지갑 주소: {wallet.classic_address}")
    print(f"비밀키: {wallet.seed}")

    # 잔액 확인
    balance = get_balance(wallet.classic_address, client)
    print(f"잔액: {balance} XRP")

    # NFT 민팅 트랜잭션 생성 (Tokenization)
    nft_mint_tx = NFTokenMint(
        account=wallet.classic_address,
        nftoken_taxon=0,  # NFT 분류 (0: 기본 분류)
        uri=xrpl.utils.str_to_hex("https://example.com/nft/metadata.json"),
        flags=8  # 8: Transferable(양도가능) NFT 설정
    )
    print("NFT 민팅 중...")
    nft_response = submit_and_wait(nft_mint_tx, client, wallet)
    print("NFT 민팅 결과:", nft_response.result)

    # 민팅 결과에 hash가 포함되면 등록 처리
    if "hash" in nft_response.result:
        nft_hash = nft_response.result["hash"]
        nft_details = {
            "nft_hash": nft_hash,
            "metadata_uri": "https://example.com/nft/metadata.json",
            "owner": wallet.classic_address,
        }
        register_nft_with_root_network(nft_details)
    else:
        print("NFT 등록 실패")

class XRPLExample:
    """
    XRPL 테스트넷 연결, 지갑 생성, 트랜잭션 처리, 주소 변환 기능을 제공하는 클래스입니다.
    """
    def __init__(self, json_rpc_url):
        # 동기 및 비동기 클라이언트 초기화
        self.json_rpc_url = json_rpc_url
        self.client = JsonRpcClient(json_rpc_url)
        self.async_client = AsyncJsonRpcClient(json_rpc_url)

    def create_wallet_from_seed(self, seed):
        """
        기존 시드를 이용해 지갑(Wallet)을 생성합니다.
        """
        try:
            wallet = Wallet.from_seed(seed)
            print("Seed로 생성된 지갑 정보:")
            print(wallet)
            return wallet
        except Exception as e:
            print("Seed로 지갑 생성 실패:", e)
            return None

    def generate_faucet_wallet(self):
        """
        Faucet을 이용해 테스트 지갑을 생성합니다.
        """
        try:
            test_wallet = generate_faucet_wallet(self.client)
            print("Faucet으로 생성된 테스트 지갑의 클래식 주소:", test_wallet.classic_address)
            return test_wallet
        except Exception as e:
            print("Faucet 지갑 생성 실패:", e)
            return None

    def generate_new_keypair(self):
        """
        새로운 시드를 생성하여 공개키, 비공개키와 클래식 주소를 도출합니다.
        """
        try:
            seed = keypairs.generate_seed()
            public, private = keypairs.derive_keypair(seed)
            classic_address = keypairs.derive_classic_address(public)
            print("새로운 공개키:", public)
            print("새로운 비공개키:", private)
            print("새로운 클래식 주소:", classic_address)
            return {"seed": seed, "public": public, "private": private, "classic_address": classic_address}
        except Exception as e:
            print("새로운 키 쌍 생성 실패:", e)
            return None

    def get_current_fee(self):
        """
        현재 거래 수수료(fee)를 조회합니다.
        """
        try:
            fee = get_fee(self.client)
            print("현재 거래 수수료 (drops):", fee)
            return fee
        except Exception as e:
            print("거래 수수료 조회 실패:", e)
            return None

    def submit_payment_sync(self, test_wallet, amount, destination):
        """
        동기 방식으로 Payment 트랜잭션을 생성, 서명 및 제출합니다.
        - amount: drops 단위 (예: 2200000 drops = 2.2 XRP)
        - destination: 수신 계정 주소
        """
        try:
            payment = Payment(
                account=test_wallet.classic_address,
                amount=str(amount),
                destination=destination
            )
            # 자동으로 수수료, 시퀀스, 마지막 원장 시퀀스를 채워 서명
            payment_signed = autofill_and_sign(payment, self.client, test_wallet)
            print("서명된 Payment 트랜잭션:")
            print(payment_signed)
            response = submit_and_wait(payment_signed, self.client)
            print("동기 방식 트랜잭션 응답:")
            print(response)
            return response
        except Exception as e:
            print("동기 트랜잭션 제출 실패:", e)
            return None

    async def submit_payment_async(self, test_wallet, amount, destination):
        """
        비동기 방식으로 Payment 트랜잭션을 생성, 서명 및 제출합니다.
        """
        try:
            current_validated_ledger = await get_latest_validated_ledger_sequence(self.async_client)
            next_seq = await get_next_valid_seq_number(test_wallet.classic_address, self.async_client)
            payment = Payment(
                account=test_wallet.classic_address,
                amount=str(amount),
                destination=destination,
                last_ledger_sequence=current_validated_ledger + 20,
                sequence=next_seq,
                fee="10"
            )
            response = await async_submit_and_wait(payment, self.async_client, test_wallet)
            print("비동기 방식 트랜잭션 응답:")
            print(response)
            return response
        except Exception as e:
            print("비동기 트랜잭션 제출 실패:", e)
            return None

    def convert_classic_to_xaddress(self, classic_address, tag=0, is_test_network=True):
        """
        클래식 주소를 X-주소로 변환합니다.
        """
        try:
            xaddress = addresscodec.classic_address_to_xaddress(
                classic_address,
                tag=tag,
                is_test_network=is_test_network
            )
            print("변환된 X-주소:", xaddress)
            return xaddress
        except Exception as e:
            print("주소 변환 실패:", e)
            return None

def run_xrpl_example():
    """
    XRPLExample 클래스를 이용하여 전체 예제 코드를 실행합니다.
    """
    # 테스트넷 JSON-RPC URL 설정
    json_rpc_url = "https://s.altnet.rippletest.net:51234"
    xrpl_example = XRPLExample(json_rpc_url)

    # 1. 기존 시드로 지갑 생성 (안전한 시드를 사용하세요)
    sample_seed = "s████████████████████████████"  # 실제 시드를 입력하세요.
    wallet_from_seed = xrpl_example.create_wallet_from_seed(sample_seed)

    # 2. Faucet을 이용한 테스트 지갑 생성
    test_wallet = xrpl_example.generate_faucet_wallet()
    if test_wallet is None:
        return

    # 3. 새로운 시드로 키 쌍 생성 및 주소 도출
    xrpl_example.generate_new_keypair()

    # 4. 현재 거래 수수료 조회
    xrpl_example.get_current_fee()

    # 5. Payment 트랜잭션 생성, 서명 및 제출 (동기 방식)
    destination_address = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"  # 예시 수신 주소
    xrpl_example.submit_payment_sync(test_wallet, "2200000", destination_address)

    # 6. Payment 트랜잭션 제출 (비동기 방식)
    asyncio.run(xrpl_example.submit_payment_async(test_wallet, "2200000", destination_address))

    # 7. 클래식 주소를 X-주소로 변환 (예시 주소 사용)
    xrpl_example.convert_classic_to_xaddress("rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz", tag=0, is_test_network=True)

if __name__ == "__main__":
    # 실행할 예제 선택
    # 예제 1: NFT 민팅 예제 실행
    # nft_minting_example()

    # 예제 2: XRPL 기능 예제 실행
    run_xrpl_example()
