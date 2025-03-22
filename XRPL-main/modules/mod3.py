import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.requests import AccountNFTs

testnet_url = "https://s.devnet.rippletest.net:51234"

def mint_token(seed, uri, flags, transfer_fee, taxon):
    """mint_token - NFT 발행 함수
    - seed: 발행자의 시드
    - uri: NFT와 연결된 메타데이터 URI (16진수로 변환됨)
    - flags: NFT 설정 플래그 (정수)
    - transfer_fee: 전송 수수료 (정수)
    - taxon: NFT 분류용 태그 (정수)
    """
    print("mint_token 함수 호출됨")
    print("입력받은 seed:", seed)
    print("입력받은 uri:", uri)
    print("입력받은 flags:", flags)
    print("입력받은 transfer_fee:", transfer_fee)
    print("입력받은 taxon:", taxon)
    
    # Get the client
    minter_wallet = Wallet.from_seed(seed)
    print("지갑 생성 완료 - 주소:", minter_wallet.address)
    client = JsonRpcClient(testnet_url)
    print("JsonRpcClient 생성 완료:", client)
    
    # Define the mint transaction
    mint_tx = xrpl.models.transactions.NFTokenMint(
        account=minter_wallet.address,
        uri=xrpl.utils.str_to_hex(uri),
        flags=int(flags),
        transfer_fee=int(transfer_fee),
        nftoken_taxon=int(taxon)
    )
    print("NFTokenMint 객체 생성 완료:", mint_tx)
    
    # Submit the transaction and get results
    reply = ""
    try:
        print("트랜잭션 제출 시작...")
        response = xrpl.transaction.submit_and_wait(mint_tx, client, minter_wallet)
        print("트랜잭션 제출 완료, 응답:", response.result)
        reply = response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        print("XRPLReliableSubmissionException 발생:", e)
        reply = f"Submit failed: {e}"
    except Exception as e:
        print("mint_token 처리 중 예외 발생:", e)
        raise
    return reply


def get_tokens(account):
    """get_tokens - 계정의 NFT 조회 함수
    - account: 조회할 계정의 XRP 주소
    """
    print("get_tokens 함수 호출됨 - account:", account)
    
    client = JsonRpcClient(testnet_url)
    print("JsonRpcClient 생성 완료:", client)
    
    acct_nfts = AccountNFTs(
        account=account
    )
    print("AccountNFTs 요청 객체 생성 완료:", acct_nfts)
    
    response = client.request(acct_nfts)
    print("NFT 조회 응답:", response.result)
    return response.result


def burn_token(seed, nftoken_id):
    """burn_token - NFT 소각 함수
    - seed: 소각자의 시드
    - nftoken_id: 소각할 NFT의 고유 ID
    """
    print("burn_token 함수 호출됨")
    print("입력받은 seed:", seed)
    print("입력받은 nftoken_id:", nftoken_id)
    
    # Get the client
    owner_wallet = Wallet.from_seed(seed)
    print("지갑 생성 완료 - 주소:", owner_wallet.address)
    client = JsonRpcClient(testnet_url)
    print("JsonRpcClient 생성 완료:", client)
    
    # Define the burn transaction
    burn_tx = xrpl.models.transactions.NFTokenBurn(
        account=owner_wallet.address,
        nftoken_id=nftoken_id    
    )
    print("NFTokenBurn 객체 생성 완료:", burn_tx)
    
    # Submit the transaction and get results
    reply = ""
    try:
        print("트랜잭션 제출 시작...")
        response = xrpl.transaction.submit_and_wait(burn_tx, client, owner_wallet)
        print("트랜잭션 제출 완료, 응답:", response.result)
        reply = response.result
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        print("XRPLReliableSubmissionException 발생:", e)
        reply = f"Submit failed: {e}"
    except Exception as e:
        print("burn_token 처리 중 예외 발생:", e)
        raise
    return reply