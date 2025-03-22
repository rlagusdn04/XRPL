import tkinter as tk
from tkinter import ttk
import xrpl
import json
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import NFTokenCreateOffer, NFTokenAcceptOffer, EscrowCreate, EscrowFinish, EscrowCancel
from xrpl.utils import xrp_to_drops
from web3 import Web3
import threading
from time import sleep
from datetime import datetime
import os

# XRPL 테스트넷 클라이언트 설정
client = JsonRpcClient("https://s.altnet.rippletest.net:51234")

# XRPL 모듈 임포트 (가정된 모듈)
from modules.mod1 import get_account, get_account_info, send_xrp
from modules.mod2 import create_trust_line, send_currency, get_balance, configure_account
from modules.mod3 import mint_token, get_tokens, burn_token

# Hardhat 로컬 네트워크 설정
hardhat_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(hardhat_url))

# 스마트 컨트랙트 설정
contract_address = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"
contract_abi = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": True, "name": "tokenId", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "inputs": [{"name": "to", "type": "address"}],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

try:
    if web3.is_connected() and web3.is_address(contract_address):
        contract = web3.eth.contract(address=contract_address, abi=contract_abi)
        print("Web3 연결 상태: True, 컨트랙트 주소 유효")
    else:
        raise ValueError("컨트랙트 주소가 유효하지 않거나 네트워크에 연결되지 않음")
except Exception as e:
    contract = None
    print(f"사이드체인 연결 오류: {str(e)}. XRPL만으로 작동합니다.")

# Tkinter 창 생성
window = tk.Tk()
window.title("XRPL NFT Platform with Escrow Tester")

# Rippling 변수
standbyRippling = tk.BooleanVar()
operationalRippling = tk.BooleanVar()

# 거래 내역 파일 경로
TRANSACTION_FILE = "transactions.json"

# 거래 내역 초기화
if os.path.exists(TRANSACTION_FILE):
    with open(TRANSACTION_FILE, "r") as f:
        transaction_history = json.load(f)
else:
    transaction_history = []

# Notebook 위젯 생성 (탭 관리)
notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

# Accounts & NFTs 탭
frm_form = tk.Frame(notebook)
notebook.add(frm_form, text="Accounts & NFTs")

# Escrow 탭
frm_escrow = tk.Frame(notebook)
notebook.add(frm_escrow, text="Escrow")

# Standby 계정 필드
lbl_standby_seed = tk.Label(master=frm_form, text="Standby Seed")
ent_standby_seed = tk.Entry(master=frm_form, width=50)
lbl_standby_account = tk.Label(master=frm_form, text="Standby Account")
ent_standby_account = tk.Entry(master=frm_form, width=50)
lbl_standby_amount = tk.Label(master=frm_form, text="Amount")
ent_standby_amount = tk.Entry(master=frm_form, width=50)
lbl_standby_destination = tk.Label(master=frm_form, text="Destination")
ent_standby_destination = tk.Entry(master=frm_form, width=50)
lbl_standby_balance = tk.Label(master=frm_form, text="XRP Balance")
ent_standby_balance = tk.Entry(master=frm_form, width=50)
lbl_standby_currency = tk.Label(master=frm_form, text="Currency")
ent_standby_currency = tk.Entry(master=frm_form, width=50)
cb_standby_allow_rippling = tk.Checkbutton(master=frm_form, text="Allow Rippling", variable=standbyRippling, onvalue=True, offvalue=False)
lbl_standby_uri = tk.Label(master=frm_form, text="NFT URI")
ent_standby_uri = tk.Entry(master=frm_form, width=50)
lbl_standby_flags = tk.Label(master=frm_form, text="Flags")
ent_standby_flags = tk.Entry(master=frm_form, width=50)
lbl_standby_transfer_fee = tk.Label(master=frm_form, text="Transfer Fee")
ent_standby_transfer_fee = tk.Entry(master=frm_form, width=50)
lbl_standby_taxon = tk.Label(master=frm_form, text="Taxon")
ent_standby_taxon = tk.Entry(master=frm_form, width=50)
lbl_standby_nft_id = tk.Label(master=frm_form, text="NFT ID")
ent_standby_nft_id = tk.Entry(master=frm_form, width=50)
lbl_standby_results = tk.Label(master=frm_form, text='Results')
text_standby_results = tk.Text(master=frm_form, height=20, width=65)

# Standby 필드 배치
lbl_standby_seed.grid(row=0, column=0, sticky="w")
ent_standby_seed.grid(row=0, column=1)
lbl_standby_account.grid(row=2, column=0, sticky="e")
ent_standby_account.grid(row=2, column=1)
lbl_standby_amount.grid(row=3, column=0, sticky="e")
ent_standby_amount.grid(row=3, column=1)
lbl_standby_destination.grid(row=4, column=0, sticky="e")
ent_standby_destination.grid(row=4, column=1)
lbl_standby_balance.grid(row=5, column=0, sticky="e")
ent_standby_balance.grid(row=5, column=1)
lbl_standby_currency.grid(row=6, column=0, sticky="e")
ent_standby_currency.grid(row=6, column=1)
cb_standby_allow_rippling.grid(row=7, column=1, sticky="w")
lbl_standby_uri.grid(row=8, column=0, sticky="e")
ent_standby_uri.grid(row=8, column=1, sticky="w")
lbl_standby_flags.grid(row=9, column=0, sticky="e")
ent_standby_flags.grid(row=9, column=1, sticky="w")
lbl_standby_transfer_fee.grid(row=10, column=0, sticky="e")
ent_standby_transfer_fee.grid(row=10, column=1, sticky="w")
lbl_standby_taxon.grid(row=11, column=0, sticky="e")
ent_standby_taxon.grid(row=11, column=1, sticky="w")
lbl_standby_nft_id.grid(row=12, column=0, sticky="e")
ent_standby_nft_id.grid(row=12, column=1, sticky="w")
lbl_standby_results.grid(row=13, column=0, sticky="ne")
text_standby_results.grid(row=13, column=1, sticky="nw")

cb_standby_allow_rippling.select()

# Operational 계정 필드
lbl_operational_seed = tk.Label(master=frm_form, text="Operational Seed")
ent_operational_seed = tk.Entry(master=frm_form, width=50)
lbl_operational_account = tk.Label(master=frm_form, text="Operational Account")
ent_operational_account = tk.Entry(master=frm_form, width=50)
lbl_operational_amount = tk.Label(master=frm_form, text="Amount")
ent_operational_amount = tk.Entry(master=frm_form, width=50)
lbl_operational_destination = tk.Label(master=frm_form, text="Destination")
ent_operational_destination = tk.Entry(master=frm_form, width=50)
lbl_operational_balance = tk.Label(master=frm_form, text="XRP Balance")
ent_operational_balance = tk.Entry(master=frm_form, width=50)
lbl_operational_currency = tk.Label(master=frm_form, text="Currency")
ent_operational_currency = tk.Entry(master=frm_form, width=50)
cb_operational_allow_rippling = tk.Checkbutton(master=frm_form, text="Allow Rippling", variable=operationalRippling, onvalue=True, offvalue=False)
lbl_operational_uri = tk.Label(master=frm_form, text="NFT URI")
ent_operational_uri = tk.Entry(master=frm_form, width=50)
lbl_operational_flags = tk.Label(master=frm_form, text="Flags")
ent_operational_flags = tk.Entry(master=frm_form, width=50)
lbl_operational_transfer_fee = tk.Label(master=frm_form, text="Transfer Fee")
ent_operational_transfer_fee = tk.Entry(master=frm_form, width=50)
lbl_operational_taxon = tk.Label(master=frm_form, text="Taxon")
ent_operational_taxon = tk.Entry(master=frm_form, width=50)
lbl_operational_nft_id = tk.Label(master=frm_form, text="NFT ID")
ent_operational_nft_id = tk.Entry(master=frm_form, width=50)
lbl_operational_results = tk.Label(master=frm_form, text="Results")
text_operational_results = tk.Text(master=frm_form, height=20, width=65)

# Operational 필드 배치
lbl_operational_seed.grid(row=0, column=4, sticky="e")
ent_operational_seed.grid(row=0, column=5, sticky="w")
lbl_operational_account.grid(row=2, column=4, sticky="e")
ent_operational_account.grid(row=2, column=5, sticky="w")
lbl_operational_amount.grid(row=3, column=4, sticky="e")
ent_operational_amount.grid(row=3, column=5, sticky="w")
lbl_operational_destination.grid(row=4, column=4, sticky="e")
ent_operational_destination.grid(row=4, column=5, sticky="w")
lbl_operational_balance.grid(row=5, column=4, sticky="e")
ent_operational_balance.grid(row=5, column=5, sticky="w")
lbl_operational_currency.grid(row=6, column=4, sticky="e")
ent_operational_currency.grid(row=6, column=5)
cb_operational_allow_rippling.grid(row=7, column=5, sticky="w")
lbl_operational_uri.grid(row=8, column=4, sticky="e")
ent_operational_uri.grid(row=8, column=5, sticky="w")
lbl_operational_flags.grid(row=9, column=4, sticky="e")
ent_operational_flags.grid(row=9, column=5, sticky="w")
lbl_operational_transfer_fee.grid(row=10, column=4, sticky="e")
ent_operational_transfer_fee.grid(row=10, column=5, sticky="w")
lbl_operational_taxon.grid(row=11, column=4, sticky="e")
ent_operational_taxon.grid(row=11, column=5, sticky="w")
lbl_operational_nft_id.grid(row=12, column=4, sticky="e")
ent_operational_nft_id.grid(row=12, column=5, sticky="w")
lbl_operational_results.grid(row=13, column=4, sticky="ne")
text_operational_results.grid(row=13, column=5, sticky="nw")

cb_operational_allow_rippling.select()

# Escrow 탭 필드
lbl_create_seed = tk.Label(frm_escrow, text="Seed")
ent_create_seed = tk.Entry(frm_escrow, width=50)
lbl_create_amount = tk.Label(frm_escrow, text="Amount (XRP)")
ent_create_amount = tk.Entry(frm_escrow, width=50)
lbl_create_destination = tk.Label(frm_escrow, text="Destination")
ent_create_destination = tk.Entry(frm_escrow, width=50)
lbl_create_condition = tk.Label(frm_escrow, text="Condition")
ent_create_condition = tk.Entry(frm_escrow, width=50)
lbl_create_cancel_after = tk.Label(frm_escrow, text="Cancel After (ripple epoch)")
ent_create_cancel_after = tk.Entry(frm_escrow, width=50)
lbl_create_finish_after = tk.Label(frm_escrow, text="Finish After (ripple epoch)")
ent_create_finish_after = tk.Entry(frm_escrow, width=50)
btn_create_escrow = tk.Button(frm_escrow, text="Create Escrow", command=lambda: create_escrow(
    ent_create_seed.get(),
    ent_create_amount.get(),
    ent_create_destination.get(),
    ent_create_condition.get() or None,
    ent_create_cancel_after.get() or None,
    ent_create_finish_after.get() or None
))
text_create_results = tk.Text(frm_escrow, height=10, width=65)

lbl_finish_seed = tk.Label(frm_escrow, text="Seed")
ent_finish_seed = tk.Entry(frm_escrow, width=50)
lbl_finish_owner = tk.Label(frm_escrow, text="Owner")
ent_finish_owner = tk.Entry(frm_escrow, width=50)
lbl_finish_sequence = tk.Label(frm_escrow, text="Offer Sequence")
ent_finish_sequence = tk.Entry(frm_escrow, width=50)
lbl_finish_condition = tk.Label(frm_escrow, text="Condition")
ent_finish_condition = tk.Entry(frm_escrow, width=50)
btn_finish_escrow = tk.Button(frm_escrow, text="Finish Escrow", command=lambda: finish_escrow(
    ent_finish_seed.get(),
    ent_finish_owner.get(),
    ent_finish_sequence.get(),
    ent_finish_condition.get() or None
))
text_finish_results = tk.Text(frm_escrow, height=10, width=65)

lbl_cancel_seed = tk.Label(frm_escrow, text="Seed")
ent_cancel_seed = tk.Entry(frm_escrow, width=50)
lbl_cancel_owner = tk.Label(frm_escrow, text="Owner")
ent_cancel_owner = tk.Entry(frm_escrow, width=50)
lbl_cancel_sequence = tk.Label(frm_escrow, text="Offer Sequence")
ent_cancel_sequence = tk.Entry(frm_escrow, width=50)
btn_cancel_escrow = tk.Button(frm_escrow, text="Cancel Escrow", command=lambda: cancel_escrow(
    ent_cancel_seed.get(),
    ent_cancel_owner.get(),
    ent_cancel_sequence.get()
))
text_cancel_results = tk.Text(frm_escrow, height=10, width=65)

# Escrow 필드 배치
lbl_create_seed.grid(row=0, column=0, sticky="e")
ent_create_seed.grid(row=0, column=1)
lbl_create_amount.grid(row=1, column=0, sticky="e")
ent_create_amount.grid(row=1, column=1)
lbl_create_destination.grid(row=2, column=0, sticky="e")
ent_create_destination.grid(row=2, column=1)
lbl_create_condition.grid(row=3, column=0, sticky="e")
ent_create_condition.grid(row=3, column=1)
lbl_create_cancel_after.grid(row=4, column=0, sticky="e")
ent_create_cancel_after.grid(row=4, column=1)
lbl_create_finish_after.grid(row=5, column=0, sticky="e")
ent_create_finish_after.grid(row=5, column=1)
btn_create_escrow.grid(row=6, column=0, columnspan=2)
text_create_results.grid(row=7, column=0, columnspan=2)

lbl_finish_seed.grid(row=8, column=0, sticky="e")
ent_finish_seed.grid(row=8, column=1)
lbl_finish_owner.grid(row=9, column=0, sticky="e")
ent_finish_owner.grid(row=9, column=1)
lbl_finish_sequence.grid(row=10, column=0, sticky="e")
ent_finish_sequence.grid(row=10, column=1)
lbl_finish_condition.grid(row=11, column=0, sticky="e")
ent_finish_condition.grid(row=11, column=1)
btn_finish_escrow.grid(row=12, column=0, columnspan=2)
text_finish_results.grid(row=13, column=0, columnspan=2)

lbl_cancel_seed.grid(row=14, column=0, sticky="e")
ent_cancel_seed.grid(row=14, column=1)
lbl_cancel_owner.grid(row=15, column=0, sticky="e")
ent_cancel_owner.grid(row=15, column=1)
lbl_cancel_sequence.grid(row=16, column=0, sticky="e")
ent_cancel_sequence.grid(row=16, column=1)
btn_cancel_escrow.grid(row=17, column=0, columnspan=2)
text_cancel_results.grid(row=18, column=0, columnspan=2)

# 핸들러 정의
def get_standby_account():
    new_wallet = get_account(ent_standby_seed.get())
    ent_standby_account.delete(0, tk.END)
    ent_standby_seed.delete(0, tk.END)
    ent_standby_account.insert(0, new_wallet.classic_address)
    ent_standby_seed.insert(0, new_wallet.seed)

def get_standby_account_info():
    accountInfo = get_account_info(ent_standby_account.get())
    ent_standby_balance.delete(0, tk.END)
    ent_standby_balance.insert(0, accountInfo['Balance'])
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(accountInfo, indent=4))

def standby_send_xrp():
    try:
        response = send_xrp(ent_standby_seed.get(), ent_standby_amount.get(), ent_standby_destination.get())
        text_standby_results.delete("1.0", tk.END)
        if isinstance(response, dict) and "error" in response:
            text_standby_results.insert("1.0", response["error"])
        else:
            text_standby_results.insert("1.0", json.dumps(response.result, indent=4))
        get_standby_account_info()
        get_operational_account_info()
    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"Error: {str(e)}")

def standby_mint_token():
    results = mint_token(
        ent_standby_seed.get(),
        ent_standby_uri.get(),
        ent_standby_flags.get(),
        ent_standby_transfer_fee.get(),
        ent_standby_taxon.get()
    )
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(results, indent=4))

def standby_get_tokens():
    results = get_tokens(ent_standby_account.get())
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(results, indent=4))

def get_operational_account():
    new_wallet = get_account(ent_operational_seed.get())
    ent_operational_account.delete(0, tk.END)
    ent_operational_account.insert(0, new_wallet.classic_address)
    ent_operational_seed.delete(0, tk.END)
    ent_operational_seed.insert(0, new_wallet.seed)

def get_operational_account_info():
    accountInfo = get_account_info(ent_operational_account.get())
    ent_operational_balance.delete(0, tk.END)
    ent_operational_balance.insert(0, accountInfo['Balance'])
    text_operational_results.delete("1.0", tk.END)
    text_operational_results.insert("1.0", json.dumps(accountInfo, indent=4))

def operational_send_xrp():
    try:
        response = send_xrp(ent_operational_seed.get(), ent_operational_amount.get(), ent_operational_destination.get())
        text_operational_results.delete("1.0", tk.END)
        if isinstance(response, dict) and "error" in response:
            text_operational_results.insert("1.0", response["error"])
        else:
            text_operational_results.insert("1.0", json.dumps(response.result, indent=4))
        get_standby_account_info()
        get_operational_account_info()
    except Exception as e:
        text_operational_results.delete("1.0", tk.END)
        text_operational_results.insert("1.0", f"Error: {str(e)}")

# NFT 전송 함수
def create_nft_offer(seed, nft_id, amount, destination):
    wallet = Wallet.from_seed(seed)
    sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
    offer = NFTokenCreateOffer(
        account=wallet.classic_address,
        nftoken_id=nft_id,
        amount=xrp_to_drops(amount),
        destination=destination,
        flags=1,  # tfSellNFToken 플래그로 판매 오퍼 생성
        sequence=sequence
    )
    try:
        response = xrpl.transaction.submit_and_wait(offer, client, wallet)
        return response.result
    except Exception as e:
        return {"error": str(e)}

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

def transfer_nft():
    try:
        # XRP 결제: Standby -> Operational
        amount = ent_standby_amount.get()
        response_xrp = send_xrp(ent_standby_seed.get(), amount, ent_operational_account.get())
        if isinstance(response_xrp, dict) and "error" in response_xrp:
            raise Exception(response_xrp["error"])

        # NFT ID 확인
        nft_id = ent_standby_nft_id.get()
        if not nft_id:
            raise Exception("NFT ID가 필요합니다.")

        # 1. Standby 계정에서 NFT 판매 오퍼 생성
        offer_response = create_nft_offer(ent_standby_seed.get(), nft_id, amount, ent_operational_account.get())
        if "error" in offer_response:
            raise Exception(offer_response["error"])
        
        offer_id = offer_response["tx_json"]["hash"]  # 실제 오퍼 ID 추출 필요

        # 2. Operational 계정에서 오퍼 수락
        accept_response = accept_nft_offer(ent_operational_seed.get(), offer_id)
        if "error" in accept_response:
            raise Exception(accept_response["error"])

        # 거래 내역 생성 및 JSON 파일 저장
        new_transaction = {
            "nft_id": nft_id,
            "from": ent_standby_account.get(),
            "to": ent_operational_account.get(),
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "offer_id": offer_id
        }
        transaction_history.append(new_transaction)
        with open(TRANSACTION_FILE, "w") as f:
            json.dump(transaction_history, f, indent=4)

        # NFT 전송 확인
        standby_nfts = get_tokens(ent_standby_account.get())
        operational_nfts = get_tokens(ent_operational_account.get())
        standby_has_nft = any(nft["NFTokenID"] == nft_id for nft in standby_nfts)
        operational_has_nft = any(nft["NFTokenID"] == nft_id for nft in operational_nfts)

        # 결과 출력
        text_standby_results.delete("1.0", tk.END)
        if not standby_has_nft:
            text_standby_results.insert("1.0", f"Transferred NFT {nft_id} and {amount} XRP to {ent_operational_account.get()}\nOffer ID: {offer_id}")
        else:
            text_standby_results.insert("1.0", f"Error: NFT {nft_id} still in Standby account!")

        text_operational_results.delete("1.0", tk.END)
        if operational_has_nft:
            text_operational_results.insert("1.0", f"Received NFT {nft_id} and {amount} XRP from {ent_standby_account.get()}\nOffer ID: {offer_id}")
            ent_operational_nft_id.delete(0, tk.END)
            ent_operational_nft_id.insert(0, nft_id)
            ent_standby_nft_id.delete(0, tk.END)
        else:
            text_operational_results.insert("1.0", f"Error: NFT {nft_id} not received!")

        # 계정 정보 업데이트
        get_standby_account_info()
        get_operational_account_info()

    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"Error: {str(e)}")

# Escrow 함수
def create_escrow(seed, amount, destination, condition=None, cancel_after=None, finish_after=None):
    wallet = Wallet.from_seed(seed)
    sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
    escrow_create = EscrowCreate(
        account=wallet.classic_address,
        amount=xrp_to_drops(amount),
        destination=destination,
        condition=condition,
        cancel_after=int(cancel_after) if cancel_after else None,
        finish_after=int(finish_after) if finish_after else None,
        sequence=sequence
    )
    try:
        response = xrpl.transaction.submit_and_wait(escrow_create, client, wallet)
        text_create_results.delete("1.0", tk.END)
        text_create_results.insert("1.0", json.dumps(response.result, indent=4))
    except Exception as e:
        text_create_results.delete("1.0", tk.END)
        text_create_results.insert("1.0", f"Error: {str(e)}")

def finish_escrow(seed, owner, offer_sequence, condition=None):
    wallet = Wallet.from_seed(seed)
    sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
    escrow_finish = EscrowFinish(
        account=wallet.classic_address,
        owner=owner,
        offer_sequence=int(offer_sequence),
        condition=condition,
        sequence=sequence
    )
    try:
        response = xrpl.transaction.submit_and_wait(escrow_finish, client, wallet)
        text_finish_results.delete("1.0", tk.END)
        text_finish_results.insert("1.0", json.dumps(response.result, indent=4))
    except Exception as e:
        text_finish_results.delete("1.0", tk.END)
        text_finish_results.insert("1.0", f"Error: {str(e)}")

def cancel_escrow(seed, owner, offer_sequence):
    wallet = Wallet.from_seed(seed)
    sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
    escrow_cancel = EscrowCancel(
        account=wallet.classic_address,
        owner=owner,
        offer_sequence=int(offer_sequence),
        sequence=sequence
    )
    try:
        response = xrpl.transaction.submit_and_wait(escrow_cancel, client, wallet)
        text_cancel_results.delete("1.0", tk.END)
        text_cancel_results.insert("1.0", json.dumps(response.result, indent=4))
    except Exception as e:
        text_cancel_results.delete("1.0", tk.END)
        text_cancel_results.insert("1.0", f"Error: {str(e)}")

def view_transaction_history():
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(transaction_history, indent=4))

# 버튼 설정
btn_get_standby_account = tk.Button(master=frm_form, text="Get Standby Account", command=get_standby_account)
btn_get_standby_account.grid(row=0, column=2, sticky="nsew")
btn_get_standby_account_info = tk.Button(master=frm_form, text="Get Standby Account Info", command=get_standby_account_info)
btn_get_standby_account_info.grid(row=1, column=2, sticky="nsew")
btn_standby_send_xrp = tk.Button(master=frm_form, text="Send XRP >", command=standby_send_xrp)
btn_standby_send_xrp.grid(row=2, column=2, sticky="nsew")
btn_standby_mint_token = tk.Button(master=frm_form, text="Mint NFT", command=standby_mint_token)
btn_standby_mint_token.grid(row=8, column=2, sticky="nsew")
btn_standby_get_tokens = tk.Button(master=frm_form, text="Get NFTs", command=standby_get_tokens)
btn_standby_get_tokens.grid(row=9, column=2, sticky="nsew")
btn_transfer_nft = tk.Button(master=frm_form, text="Transfer NFT >", command=transfer_nft)
btn_transfer_nft.grid(row=11, column=2, sticky="nsew")
btn_view_history = tk.Button(master=frm_form, text="View History", command=view_transaction_history)
btn_view_history.grid(row=12, column=2, sticky="nsew")

btn_get_operational_account = tk.Button(master=frm_form, text="Get Operational Account", command=get_operational_account)
btn_get_operational_account.grid(row=0, column=3, sticky="nsew")
btn_get_op_account_info = tk.Button(master=frm_form, text="Get Op Account Info", command=get_operational_account_info)
btn_get_op_account_info.grid(row=1, column=3, sticky="nsew")
btn_op_send_xrp = tk.Button(master=frm_form, text="< Send XRP", command=operational_send_xrp)
btn_op_send_xrp.grid(row=2, column=3, sticky="nsew")

# 메인 루프
if __name__ == "__main__":
    if contract is not None:
        evm_thread = threading.Thread(target=lambda: None, daemon=True)  # EVM 리스너 생략
        evm_thread.start()
    else:
        print("EVM 연결 없음. XRPL만 실행.")
    window.mainloop()