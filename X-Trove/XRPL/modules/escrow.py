import xrpl
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import EscrowCreate, EscrowFinish, EscrowCancel
from xrpl.utils import xrp_to_drops

# XRPL 테스트넷 클라이언트 설정
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

def create_escrow(seed, amount, destination, condition=None, cancel_after=None, finish_after=None):
    """
    Escrow를 생성합니다.
    
    :param seed: 계정의 시드
    :param amount: Escrow에 잠글 XRP 양 (XRP 단위)
    :param destination: Escrow 완료 시 자산을 받을 계정
    :param condition: Escrow 완료를 위한 조건 (Fulfillment)
    :param cancel_after: Escrow 취소 가능 시간 (ripple epoch)
    :param finish_after: Escrow 완료 가능 시간 (ripple epoch)
    :return: 트랜잭션 결과
    """
    wallet = Wallet(seed=seed, sequence=0)  # sequence는 실제 계정의 현재 sequence로 설정 필요
    escrow_create = EscrowCreate(
        account=wallet.classic_address,
        amount=xrp_to_drops(amount),  # XRP를 drops 단위로 변환
        destination=destination,
        condition=condition,
        cancel_after=cancel_after,
        finish_after=finish_after
    )
    try:
        response = xrpl.transaction.submit_and_wait(escrow_create, client, wallet)
        return response.result
    except Exception as e:
        return {"error": str(e)}

def finish_escrow(seed, owner, offer_sequence, condition=None):
    """
    Escrow를 완료합니다.
    
    :param seed: 계정의 시드
    :param owner: Escrow를 생성한 계정
    :param offer_sequence: EscrowCreate 트랜잭션의 시퀀스 번호
    :param condition: Escrow 완료를 위한 조건 (Fulfillment)
    :return: 트랜잭션 결과
    """
    wallet = Wallet(seed=seed, sequence=0)  # sequence는 실제 계정의 현재 sequence로 설정 필요
    escrow_finish = EscrowFinish(
        account=wallet.classic_address,
        owner=owner,
        offer_sequence=offer_sequence,
        condition=condition
    )
    try:
        response = xrpl.transaction.submit_and_wait(escrow_finish, client, wallet)
        return response.result
    except Exception as e:
        return {"error": str(e)}

def cancel_escrow(seed, owner, offer_sequence):
    """
    Escrow를 취소합니다.
    
    :param seed: 계정의 시드
    :param owner: Escrow를 생성한 계정
    :param offer_sequence: EscrowCreate 트랜잭션의 시퀀스 번호
    :return: 트랜잭션 결과
    """
    wallet = Wallet(seed=seed, sequence=0)  # sequence는 실제 계정의 현재 sequence로 설정 필요
    escrow_cancel = EscrowCancel(
        account=wallet.classic_address,
        owner=owner,
        offer_sequence=offer_sequence
    )
    try:
        response = xrpl.transaction.submit_and_wait(escrow_cancel, client, wallet)
        return response.result
    except Exception as e:
        return {"error": str(e)}