import xrpl

testnet_url = "https://s.devnet.rippletest.net:51234/"

def get_account(seed):
    """get_account - 지갑 생성 함수
    - seed 값이 없는 경우 faucet에서 새 지갑을 생성합니다.
    """
    print("get_account 함수 호출됨 - seed:", seed)
    client = xrpl.clients.JsonRpcClient(testnet_url)
    if seed == '':
        print("빈 seed가 입력되어, faucet에서 새 지갑을 생성합니다.")
        new_wallet = xrpl.wallet.generate_faucet_wallet(client)
    else:
        new_wallet = xrpl.wallet.Wallet.from_seed(seed)
    print("생성된 지갑 주소:", new_wallet.classic_address)
    return new_wallet

def get_account_info(accountId):
    """get_account_info - 계정 정보 조회 함수
    - 지정한 계정의 XRP 잔액 등 정보를 조회합니다.
    """
    print("get_account_info 함수 호출됨 - accountId:", accountId)
    client = xrpl.clients.JsonRpcClient(testnet_url)
    acct_info = xrpl.models.requests.account_info.AccountInfo(
        account=accountId,
        ledger_index="validated"
    )
    print("계정 정보 요청 전 - AccountInfo 객체:", acct_info)
    response = client.request(acct_info)
    print("계정 정보 응답:", response.result)
    return response.result['account_data']

def send_xrp(seed, amount, destination):
    """send_xrp - XRP 송금 함수
    - seed: 송금자의 시드
    - amount: 송금할 금액 (XRP)
    - destination: 수신자의 XRP 주소 (올바른 XRP 주소 형식이어야 함)
    """
    print("send_xrp 함수 호출됨")
    print("입력받은 seed:", seed)
    print("송금할 금액 (XRP):", amount)
    print("송금 대상 주소:", destination)
    
    try:
        # 1. 송금자 지갑 생성
        sending_wallet = xrpl.wallet.Wallet.from_seed(seed)
        print("지갑 생성 완료 - 주소:", sending_wallet.address)
        
        # 2. XRP 금액을 drops 단위로 변환
        drops = xrpl.utils.xrp_to_drops(int(amount))
        print("변환된 금액 (drops):", drops)
        
        # 3. Payment 트랜잭션 객체 생성 (destination 값이 올바른 XRP 주소인지 확인 필요)
        payment = xrpl.models.transactions.Payment(
            account=sending_wallet.address,
            amount=drops,
            destination=destination,
        )
        print("Payment 객체 생성 완료:", payment)
        
        # 4. 클라이언트 생성
        client = xrpl.clients.JsonRpcClient(testnet_url)
        print("JsonRpcClient 생성 완료:", client)
        
        # 5. 트랜잭션 제출 및 결과 대기
        print("트랜잭션 제출 시작...")
        response = xrpl.transaction.submit_and_wait(payment, client, sending_wallet)
        print("트랜잭션 제출 완료, 응답:", response)
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        print("XRPLReliableSubmissionException 발생:", e)
        response = f"Submit failed: {e}"
    except Exception as e:
        print("send_xrp 처리 중 예외 발생:", e)
        raise
    return response
