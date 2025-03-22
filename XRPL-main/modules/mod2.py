import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet

testnet_url = "https://s.devnet.rippletest.net:51234"

#####################
# create_trust_line #
#####################

def create_trust_line(seed, issuer, currency, amount):
    """create_trust_line - 신뢰 한도(Trust Line) 생성 함수
    - seed: 신뢰 한도를 설정할 계정의 시드
    - issuer: 발행자 주소
    - currency: 발행된 통화 종류
    - amount: 신뢰 한도의 최대 금액
    """
    print("create_trust_line 함수 호출됨")
    print(f"입력값 - seed: {seed}, issuer: {issuer}, currency: {currency}, amount: {amount}")

    # 1. 지갑 생성
    receiving_wallet = Wallet.from_seed(seed)
    print("신뢰 한도를 설정할 지갑 주소:", receiving_wallet.address)

    # 2. 클라이언트 생성
    client = JsonRpcClient(testnet_url)
    print("JsonRpcClient 생성 완료")

    # 3. TrustSet 트랜잭션 생성
    trustline_tx = xrpl.models.transactions.TrustSet(
        account=receiving_wallet.address,
        limit_amount=xrpl.models.amounts.IssuedCurrencyAmount(
            currency=currency,
            issuer=issuer,
            value=int(amount)
        )
    )
    print("TrustSet 트랜잭션 생성 완료:", trustline_tx)

    # 4. 트랜잭션 제출
    try:
        response = xrpl.transaction.submit_and_wait(trustline_tx, client, receiving_wallet)
        print("트랜잭션 제출 완료, 응답:", response.result)
    except Exception as e:
        print("create_trust_line 처리 중 예외 발생:", e)
        raise

    return response.result


#################
# send_currency #
#################

def send_currency(seed, destination, currency, amount):
    """send_currency - 발행된 통화를 송금하는 함수
    - seed: 송금자의 시드
    - destination: 수신자의 XRP 주소
    - currency: 송금할 통화 종류
    - amount: 송금할 금액
    """
    print("send_currency 함수 호출됨")
    print(f"입력값 - seed: {seed}, destination: {destination}, currency: {currency}, amount: {amount}")

    # 1. 송금자 지갑 생성
    sending_wallet = Wallet.from_seed(seed)
    print("송금자 지갑 주소:", sending_wallet.address)

    # 2. 클라이언트 생성
    client = JsonRpcClient(testnet_url)
    print("JsonRpcClient 생성 완료")

    # 3. Payment 트랜잭션 생성 (발행된 통화 송금)
    send_currency_tx = xrpl.models.transactions.Payment(
        account=sending_wallet.address,
        amount=xrpl.models.amounts.IssuedCurrencyAmount(
            currency=currency,
            value=int(amount),
            issuer=sending_wallet.address
        ),
        destination=destination
    )
    print("Payment 트랜잭션 생성 완료:", send_currency_tx)

    # 4. 트랜잭션 제출
    try:
        response = xrpl.transaction.submit_and_wait(send_currency_tx, client, sending_wallet)
        print("트랜잭션 제출 완료, 응답:", response.result)
    except Exception as e:
        print("send_currency 처리 중 예외 발생:", e)
        raise

    return response.result


###############
# get_balance #
###############

def get_balance(sb_account_seed, op_account_seed):
    """get_balance - 계정 잔액 조회 함수
    - sb_account_seed: Standby 계정 시드
    - op_account_seed: Operational 계정 시드
    """
    print("get_balance 함수 호출됨")
    print(f"입력값 - sb_account_seed: {sb_account_seed}, op_account_seed: {op_account_seed}")

    # 1. 지갑 생성
    wallet = Wallet.from_seed(sb_account_seed)
    opWallet = Wallet.from_seed(op_account_seed)
    print("Standby 계정 주소:", wallet.address)
    print("Operational 계정 주소:", opWallet.address)

    # 2. 클라이언트 생성
    client = JsonRpcClient(testnet_url)
    print("JsonRpcClient 생성 완료")

    # 3. 잔액 조회 요청
    balance_request = xrpl.models.requests.GatewayBalances(
        account=wallet.address,
        ledger_index="validated"
    )
    print("잔액 조회 요청 생성 완료:", balance_request)

    # 4. 요청 실행 및 응답 처리
    try:
        response = client.request(balance_request)
        print("잔액 조회 완료, 응답:", response.result)
    except Exception as e:
        print("get_balance 처리 중 예외 발생:", e)
        raise

    return response.result


#####################
# configure_account #
#####################

def configure_account(seed, default_setting):
    """configure_account - 계정 설정 변경 함수
    - seed: 계정의 시드
    - default_setting: True면 Allow Rippling 활성화, False면 비활성화
    """
    print("configure_account 함수 호출됨")
    print(f"입력값 - seed: {seed}, default_setting: {default_setting}")

    # 1. 지갑 생성
    wallet = Wallet.from_seed(seed)
    print("설정 변경할 계정 주소:", wallet.classic_address)

    # 2. 클라이언트 생성
    client = JsonRpcClient(testnet_url)
    print("JsonRpcClient 생성 완료")

    # 3. 계정 설정 트랜잭션 생성
    if default_setting:
        setting_tx = xrpl.models.transactions.AccountSet(
            account=wallet.classic_address,
            set_flag=xrpl.models.transactions.AccountSetAsfFlag.ASF_DEFAULT_RIPPLE
        )
        print("Allow Rippling 활성화 트랜잭션 생성 완료")
    else:
        setting_tx = xrpl.models.transactions.AccountSet(
            account=wallet.classic_address,
            clear_flag=xrpl.models.transactions.AccountSetAsfFlag.ASF_DEFAULT_RIPPLE
        )
        print("Allow Rippling 비활성화 트랜잭션 생성 완료")

    # 4. 트랜잭션 제출
    try:
        response = xrpl.transaction.submit_and_wait(setting_tx, client, wallet)
        print("계정 설정 변경 완료, 응답:", response.result)
    except Exception as e:
        print("configure_account 처리 중 예외 발생:", e)
        raise

    return response.result
