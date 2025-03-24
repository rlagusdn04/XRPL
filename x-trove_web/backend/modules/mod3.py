import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import NFTokenCreateOffer, NFTokenAcceptOffer
from xrpl.models.requests import AccountNFTs
from xrpl.transaction import submit_and_wait
import json
from datetime import datetime

testnet_url = "https://s.devnet.rippletest.net:51234"
client = JsonRpcClient(testnet_url)


def mint_token(seed, uri, flags, transfer_fee, taxon):
    """mint_token - NFT 발행 함수
    - seed: 발행자의 시드
    - uri: NFT와 연결된 메타데이터 URI (16진수로 변환됨)
    - flags: NFT 설정 플래그 (정수)
    - transfer_fee: 전송 수수료 (정수)
    - taxon: NFT 분류용 태그 (정수)
    """
    # uri = 'userinput'
    # flags = 8
    # transfer_fee = 1
    # taxon = 100

    print("mint_token 함수 호출됨")
    print("입력받은 seed:", seed)
    print("입력받은 uri:", uri)
    print("입력받은 flags:", flags)
    print("입력받은 transfer_fee:", transfer_fee)
    print("입력받은 taxon:", taxon)

    try:
        # 1. 지갑 생성 및 클라이언트 준비
        minter_wallet = Wallet.from_seed(seed)
        print("지갑 생성 완료 - 주소:", minter_wallet.address)
        client = JsonRpcClient(testnet_url)
        print("JsonRpcClient 생성 완료:", client)

        # 2. NFT 발행 트랜잭션 생성
        mint_tx = xrpl.models.transactions.NFTokenMint(
            account=minter_wallet.address,
            uri=xrpl.utils.str_to_hex(uri),
            flags=int(flags),
            transfer_fee=int(transfer_fee),
            nftoken_taxon=int(taxon)
        )
        print("NFTokenMint 객체 생성 완료:", mint_tx)

        # 3. 트랜잭션 제출
        print("트랜잭션 제출 시작...")
        response = xrpl.transaction.submit_and_wait(mint_tx, client, minter_wallet)
        print("트랜잭션 제출 완료, 응답:", response.result)

        # 오류 원인 분석 출력
        transaction_result = str(response.status.value)
        if transaction_result != 'success':
            print("오류 발생: 트랜잭션 상태가 성공이 아님")
            if 'error' in response.result:
                error_msg = response.result['error']
                print("원인 분석 - 에러 메시지:", error_msg)
        return response.result

    except xrpl.transaction.XRPLReliableSubmissionException as e:
        print("XRPLReliableSubmissionException 발생:", e)
        print("원인 분석: 제출 실패 - 네트워크 또는 서버 문제일 수 있습니다.")
        return f"Submit failed: {e}"
    except Exception as e:
        print("mint_token 처리 중 예외 발생:", e)
        print("원인 분석: 트랜잭션 제출 또는 기타 문제일 수 있습니다.")
        raise


def get_tokens(account):
    """get_tokens - 계정의 NFT 조회 함수
    - account: 조회할 계정의 XRP 주소
    """
    print("get_tokens 함수 호출됨 - account:", account)
    try:
        client = JsonRpcClient(testnet_url)
        print("JsonRpcClient 생성 완료:", client)

        acct_nfts = AccountNFTs(
            account=account
        )
        print("AccountNFTs 요청 객체 생성 완료:", acct_nfts)

        response = client.request(acct_nfts)
        print("NFT 조회 응답:", response.result)
        return response.result
    except Exception as e:
        print("get_tokens 처리 중 예외 발생:", e)
        print("원인 분석: NFT 조회 또는 네트워크 문제일 수 있습니다.")
        raise


def create_nft_offer(seed, nft_id, destination):
    wallet = Wallet.from_seed(seed)
    sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
    offer = NFTokenCreateOffer(
        account=wallet.classic_address,
        nftoken_id=nft_id,
        amount="0",  # XRP 이동 없이 무료로 오퍼 생성
        destination=destination,
        flags=1,  # tfSellNFToken 플래그
        sequence=sequence
    )
    try:
        response = xrpl.transaction.submit_and_wait(offer, client, wallet)
        offer_id = None
        for node in response.result["meta"]["AffectedNodes"]:
            if "CreatedNode" in node and node["CreatedNode"]["LedgerEntryType"] == "NFTokenOffer":
                offer_id = node["CreatedNode"]["LedgerIndex"]
                break
        if not offer_id:
            raise Exception("Failed to extract NFTokenOffer ID")
        return response.result, offer_id
    except Exception as e:
        return {"error": str(e)}, None


def accept_nft_offer(seed, offer_id):
    wallet = Wallet.from_seed(seed)
    sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
    accept = NFTokenAcceptOffer(
        account=wallet.classic_address,
        nftoken_sell_offer=offer_id,
        sequence=sequence
    )
    try:
        response = xrpl.transaction.submit_and_wait(accept, client, wallet)
        return response.result
    except Exception as e:
        return {"error": str(e)}


def transfer_token(seed, nftoken_id, destination, destination_seed):
    print("call transfer_token")
    try:
        # 보내는 계정의 월렛 생성
        sender_wallet = Wallet.from_seed(seed)

        # NFT 소유권 확인
        account_nfts = get_account_nfts(sender_wallet.classic_address)
        if not any(nft["NFTokenID"] == nftoken_id for nft in account_nfts):
            raise Exception("NFT not found in sender's account")

        # NFT 판매 오퍼 생성 (Transfer용)
        nft_offer = NFTokenCreateOffer(
            account=sender_wallet.classic_address,
            nftoken_id=nftoken_id,
            amount="0",  # 전송은 0 XRP로 설정
            destination=destination,
            flags=1  # tfSellNFToken 플래그
        )

        # 오퍼 제출
        offer_response = submit_and_wait(nft_offer, client, sender_wallet)
        if not offer_response.is_successful():
            raise Exception(f"Failed to create offer: {offer_response.result.get('error_message')}")

        offer_id = offer_response.result["meta"]["offer_id"]
        print(f"Offer created with ID: {offer_id}")

        # 수신자 계정의 월렛 생성
        receiver_wallet = Wallet.from_seed(destination_seed)

        # 오퍼 수락 트랜잭션 생성
        accept_tx = NFTokenAcceptOffer(
            account=receiver_wallet.classic_address,
            nftoken_sell_offer=offer_id
        )

        # 오퍼 수락 제출
        accept_response = submit_and_wait(accept_tx, client, receiver_wallet)
        if not accept_response.is_successful():
            raise Exception(f"Failed to accept offer: {accept_response.result.get('error_message')}")

        # 결과 저장
        result = {
            "status": "success",
            "nft_id": nftoken_id,
            "from": sender_wallet.classic_address,
            "to": destination,
            "offer_id": offer_id,
            "tx_hash": accept_response.result["hash"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": "NFT transfer completed."
        }

        save_transaction(result)
        return result

    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_account_nfts(account):
    """계정의 NFT 목록 조회"""
    from xrpl.models.requests import AccountNFTs
    request = AccountNFTs(account=account)
    response = client.request(request)
    return response.result.get("account_nfts", [])


def save_transaction(transaction):
    """거래 내역 파일에 저장"""
    TRANSACTION_FILE = "transactions.json"
    try:
        with open(TRANSACTION_FILE, "r") as f:
            history = json.load(f)
    except:
        history = []

    history.append(transaction)
    with open(TRANSACTION_FILE, "w") as f:
        json.dump(history, f, indent=4)
