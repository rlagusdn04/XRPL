import os
import logging
import nest_asyncio
import asyncio

from xrpl.clients import JsonRpcClient
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.wallet import generate_faucet_wallet, Wallet
from xrpl.account import get_balance
from xrpl.models.requests import ServerInfo
from xrpl.models.transactions import NFTokenMint, Payment
from xrpl.transaction import submit_and_wait, autofill_and_sign
import xrpl.utils
from xrpl.core import keypairs, addresscodec
from xrpl.ledger import get_fee
from xrpl.asyncio.transaction import submit_and_wait as async_submit_and_wait
from xrpl.asyncio.ledger import get_latest_validated_ledger_sequence
from xrpl.asyncio.account import get_next_valid_seq_number

from modules import config # config.py 파일 import

# 로깅 설정: 시간, 로그 레벨, 메시지 출력
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Nest AsyncIO 적용 (Notebook, Jupyter 등에서 event loop 중첩 문제 해결)
nest_asyncio.apply()

def register_nft_with_root_network(nft_details: dict) -> None:
    """
    NFT를 가상 API(The Root Network)에 등록하는 함수.
    실제 API 요청은 해당 문서를 참고하여 구현하세요.
    """
    logger.info("NFT가 The Root Network에 등록되었습니다: %s", nft_details)

def nft_minting_example() -> None:
    """
    Devnet에 연결하여 NFT 민팅 트랜잭션을 처리하는 예제 함수.
    """
    # Devnet URL 연결 (config에 정의된 값 사용)
    devnet_url = config.DEVNET_URL + "/"
    client = JsonRpcClient(devnet_url)

    # 서버 정보 확인
    server_info = client.request(ServerInfo())
    logger.info("서버 정보: %s", server_info.result)

    # Faucet을 이용해 새로운 테스트 지갑 생성
    wallet = generate_faucet_wallet(client)
    logger.info("지갑 주소: %s", wallet.classic_address)
    logger.info("비밀키: %s", wallet.seed)

    # 잔액 확인
    balance = get_balance(wallet.classic_address, client)
    logger.info("잔액: %s XRP", balance)

    # NFT 민팅 트랜잭션 생성 (Tokenization)
    nft_mint_tx = NFTokenMint(
        account=wallet.classic_address,
        nftoken_taxon=0,  # NFT 분류 (0: 기본 분류)
        uri=xrpl.utils.str_to_hex("https://example.com/nft/metadata.json"),
        flags=8  # 8: Transferable(양도가능) NFT 설정
    )
    logger.info("NFT 민팅 중...")
    nft_response = submit_and_wait(nft_mint_tx, client, wallet)
    logger.info("NFT 민팅 결과: %s", nft_response.result)

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
        logger.error("NFT 등록 실패")

class XRPLExample:
    """
    XRPL Devnet 연결, 지갑 생성, 트랜잭션 처리, 주소 변환 기능을 제공하는 클래스.
    """
    def __init__(self, json_rpc_url: str) -> None:
        # 동기 및 비동기 클라이언트 초기화
        self.json_rpc_url = json_rpc_url
        self.client = JsonRpcClient(json_rpc_url)
        self.async_client = AsyncJsonRpcClient(json_rpc_url)

    def create_wallet_from_seed(self, seed: str) -> Wallet:
        """
        기존 시드를 이용해 지갑(Wallet)을 생성합니다.
        """
        try:
            wallet = Wallet.from_seed(seed)
            logger.info("Seed로 생성된 지갑 정보: %s", wallet)
            return wallet
        except Exception as e:
            logger.error("Seed로 지갑 생성 실패: %s", e)
            raise

    def generate_faucet_wallet(self) -> Wallet:
        """
        Faucet을 이용해 테스트 지갑을 생성합니다.
        """
        try:
            test_wallet = generate_faucet_wallet(self.client)
            logger.info("Faucet으로 생성된 테스트 지갑의 클래식 주소: %s", test_wallet.classic_address)
            return test_wallet
        except Exception as e:
            logger.error("Faucet 지갑 생성 실패: %s", e)
            raise

    def generate_new_keypair(self) -> dict:
        """
        새로운 시드를 생성하여 공개키, 비공개키와 클래식 주소를 도출합니다.
        """
        try:
            seed = keypairs.generate_seed()
            public, private = keypairs.derive_keypair(seed)
            classic_address = keypairs.derive_classic_address(public)
            logger.info("새로운 공개키: %s", public)
            logger.info("새로운 비공개키: %s", private)
            logger.info("새로운 클래식 주소: %s", classic_address)
            return {"seed": seed, "public": public, "private": private, "classic_address": classic_address}
        except Exception as e:
            logger.error("새로운 키 쌍 생성 실패: %s", e)
            raise

    def get_current_fee(self) -> str:
        """
        현재 거래 수수료(fee)를 조회합니다.
        """
        try:
            fee = get_fee(self.client)
            logger.info("현재 거래 수수료 (drops): %s", fee)
            return fee
        except Exception as e:
            logger.error("거래 수수료 조회 실패: %s", e)
            raise

    def submit_payment_sync(self, test_wallet: Wallet, amount: str, destination: str) -> dict:
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
            payment_signed = autofill_and_sign(payment, self.client, test_wallet)
            logger.info("서명된 Payment 트랜잭션: %s", payment_signed)
            response = submit_and_wait(payment_signed, self.client)
            logger.info("동기 방식 트랜잭션 응답: %s", response)
            return response.result
        except Exception as e:
            logger.error("동기 트랜잭션 제출 실패: %s", e)
            raise

    async def submit_payment_async(self, test_wallet: Wallet, amount: str, destination: str) -> dict:
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
            logger.info("비동기 방식 트랜잭션 응답: %s", response)
            return response.result
        except Exception as e:
            logger.error("비동기 트랜잭션 제출 실패: %s", e)
            raise

    def convert_classic_to_xaddress(self, classic_address: str, tag: int = 0, is_test_network: bool = True) -> str:
        """
        클래식 주소를 X-주소로 변환합니다.
        """
        try:
            xaddress = addresscodec.classic_address_to_xaddress(
                classic_address,
                tag=tag,
                is_test_network=is_test_network
            )
            logger.info("변환된 X-주소: %s", xaddress)
            return xaddress
        except Exception as e:
            logger.error("주소 변환 실패: %s", e)
            raise

def run_xrpl_example() -> None:
    """
    XRPLExample 클래스를 이용하여 전체 예제 코드를 실행합니다.
    """
    # Devnet JSON-RPC URL (config.DEVNET_URL 사용)
    json_rpc_url = config.DEVNET_URL
    xrpl_example = XRPLExample(json_rpc_url)

    # 1. 기존 시드로 지갑 생성 (config.SAMPLE_SEED 사용)
    try:
        wallet_from_seed = xrpl_example.create_wallet_from_seed(config.SAMPLE_SEED)
    except Exception:
        logger.warning("Seed 지갑 생성에 실패하여 진행하지 않습니다.")
        return

    # 2. Faucet을 이용한 테스트 지갑 생성
    try:
        test_wallet = xrpl_example.generate_faucet_wallet()
    except Exception:
        logger.warning("Faucet 지갑 생성에 실패하여 진행하지 않습니다.")
        return

    # 3. 새로운 시드로 키 쌍 생성 및 주소 도출
    xrpl_example.generate_new_keypair()

    # 4. 현재 거래 수수료 조회
    xrpl_example.get_current_fee()

    # 5. Payment 트랜잭션 생성, 서명 및 제출 (동기 방식)
    destination_address = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"
    try:
        xrpl_example.submit_payment_sync(test_wallet, "2200000", destination_address)
    except Exception:
        logger.error("동기 Payment 트랜잭션 제출 중 오류 발생")

    # 6. Payment 트랜잭션 제출 (비동기 방식)
    try:
        asyncio.run(xrpl_example.submit_payment_async(test_wallet, "2200000", destination_address))
    except Exception:
        logger.error("비동기 Payment 트랜잭션 제출 중 오류 발생")

    # 7. 클래식 주소를 X-주소로 변환 (예시 주소 사용)
    xrpl_example.convert_classic_to_xaddress("rMPUKmzmDWEX1tQhzQ8oGFNfAEhnWNFwz", tag=0, is_test_network=True)

if __name__ == "__main__":
    # 선택한 예제 실행: nft_minting_example() 또는 run_xrpl_example()
    # nft_minting_example()
    run_xrpl_example()
