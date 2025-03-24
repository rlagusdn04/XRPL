import tkinter as tk
from tkinter import ttk
import xrpl
import json
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import NFTokenCreateOffer, NFTokenAcceptOffer, EscrowCreate, EscrowFinish, EscrowCancel
from xrpl.utils import xrp_to_drops
import threading
from datetime import datetime
import os
import qrcode  # QR 코드 생성용
from PIL import Image, ImageTk  # 이미지 표시용

# XRPL 테스트넷 URL
testnet_url = "https://s.devnet.rippletest.net:51234"
client = JsonRpcClient(testnet_url)

# XRPL 모듈 임포트
from modules.account import get_account, get_account_info, send_xrp
from modules.nft_mint import mint_token, get_tokens, burn_token

# data 폴더와 거래 내역 파일 경로 설정
DATA_DIR = "data"
TRANSACTION_FILE = os.path.join(DATA_DIR, "transactions.json")

# data 폴더가 없으면 생성
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 거래 내역 초기화
if os.path.exists(TRANSACTION_FILE):
    with open(TRANSACTION_FILE, "r") as f:
        transaction_history = json.load(f)
else:
    transaction_history = []

# Tkinter 창 생성
window = tk.Tk()
window.title("XRPL NFT Platform with Escrow Tester")

# Rippling 변수
standbyRippling = tk.BooleanVar()
operationalRippling = tk.BooleanVar()

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

# QR 코드 표시용 라벨 추가
lbl_qr_code = tk.Label(master=frm_form, text="NFT QR Code")
lbl_qr_code.grid(row=14, column=1, sticky="nw")
qr_image_label = tk.Label(master=frm_form)
qr_image_label.grid(row=15, column=1, sticky="nw")

# 잔액 확인 헬퍼 함수
def check_balance(seed, amount):
    wallet = Wallet.from_seed(seed)
    account_info = get_account_info(wallet.classic_address)
    balance = float(account_info["Balance"]) / 1_000_000  # drops -> XRP
    amount = float(amount) if amount else 0
    reserve = 10  # 최소 예비금 10 XRP
    fee = 0.00001  # 트랜잭션 수수료 약 10 drops
    if balance < reserve + amount + fee:
        raise Exception(f"Insufficient balance: {balance} XRP (required: {reserve + amount + fee} XRP)")
    return True

# 핸들러 정의
def get_standby_account():
    new_wallet = get_account(ent_standby_seed.get())
    ent_standby_account.delete(0, tk.END)
    ent_standby_seed.delete(0, tk.END)
    ent_standby_account.insert(0, new_wallet.classic_address)
    ent_standby_seed.insert(0, new_wallet.seed)

def get_standby_account_info():
    account_info = get_account_info(ent_standby_account.get())
    ent_standby_balance.delete(0, tk.END)
    ent_standby_balance.insert(0, str(float(account_info['Balance']) / 1_000_000))  # drops -> XRP
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(account_info, indent=4))

def standby_send_xrp():
    try:
        amount = ent_standby_amount.get()
        destination = ent_standby_destination.get()
        if not amount or not destination:
            raise Exception("Amount and Destination are required.")
        check_balance(ent_standby_seed.get(), amount)
        response = send_xrp(ent_standby_seed.get(), amount, destination)
        text_standby_results.delete("1.0", tk.END)
        if isinstance(response, str) and "Submit failed" in response:
            text_standby_results.insert("1.0", response)
        else:
            text_standby_results.insert("1.0", json.dumps(response.result, indent=4))
        get_standby_account_info()
        get_operational_account_info()
    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"Error: {str(e)}")

def standby_mint_token():
    try:
        check_balance(ent_standby_seed.get(), 0)  # 수수료만 확인
        results = mint_token(
            ent_standby_seed.get(),
            ent_standby_uri.get(),
            ent_standby_flags.get() or "0",
            ent_standby_transfer_fee.get() or "0",
            ent_standby_taxon.get() or "0"
        )
        text_standby_results.delete("1.0", tk.END)
        if isinstance(results, str) and "Submit failed" in results:
            text_standby_results.insert("1.0", results)
        else:
            text_standby_results.insert("1.0", json.dumps(results, indent=4))
    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"Error: {str(e)}")

def standby_get_tokens():
    try:
        results = get_tokens(ent_standby_account.get())
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", json.dumps(results.get("account_nfts", []), indent=4))
    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"Error: {str(e)}")

def get_operational_account():
    new_wallet = get_account(ent_operational_seed.get())
    ent_operational_account.delete(0, tk.END)
    ent_operational_account.insert(0, new_wallet.classic_address)
    ent_operational_seed.delete(0, tk.END)
    ent_operational_seed.insert(0, new_wallet.seed)

def get_operational_account_info():
    account_info = get_account_info(ent_operational_account.get())
    ent_operational_balance.delete(0, tk.END)
    ent_operational_balance.insert(0, str(float(account_info['Balance']) / 1_000_000))  # drops -> XRP
    text_operational_results.delete("1.0", tk.END)
    text_operational_results.insert("1.0", json.dumps(account_info, indent=4))

def operational_send_xrp():
    try:
        amount = ent_operational_amount.get()
        destination = ent_operational_destination.get()
        if not amount or not destination:
            raise Exception("Amount and Destination are required.")
        check_balance(ent_operational_seed.get(), amount)
        response = send_xrp(ent_operational_seed.get(), amount, destination)
        text_operational_results.delete("1.0", tk.END)
        if isinstance(response, str) and "Submit failed" in response:
            text_operational_results.insert("1.0", response)
        else:
            text_operational_results.insert("1.0", json.dumps(response.result, indent=4))
        get_standby_account_info()
        get_operational_account_info()
    except Exception as e:
        text_operational_results.delete("1.0", tk.END)
        text_operational_results.insert("1.0", f"Error: {str(e)}")

# NFT 전송 함수
def create_nft_offer(seed, nft_id, destination):
    wallet = Wallet.from_seed(seed)
    sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
    offer = NFTokenCreateOffer(
        account=wallet.classic_address,
        nftoken_id=nft_id,
        amount="0",
        destination=destination,
        flags=1,
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

def transfer_nft():
    try:
        nft_id = ent_standby_nft_id.get()
        if not nft_id:
            raise Exception("NFT ID가 필요합니다.")
        
        check_balance(ent_standby_seed.get(), 0)
        check_balance(ent_operational_seed.get(), 0)

        offer_response, offer_id = create_nft_offer(ent_standby_seed.get(), nft_id, ent_operational_account.get())
        if "error" in offer_response:
            raise Exception(offer_response["error"])
        if not offer_id:
            raise Exception("Failed to retrieve offer ID")

        accept_response = accept_nft_offer(ent_operational_seed.get(), offer_id)
        if "error" in accept_response:
            raise Exception(accept_response["error"])

        new_transaction = {
            "nft_id": nft_id,
            "from": ent_standby_account.get(),
            "to": ent_operational_account.get(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "offer_id": offer_id
        }
        transaction_history.append(new_transaction)
        with open(TRANSACTION_FILE, "w") as f:
            json.dump(transaction_history, f, indent=4)

        standby_nfts = get_tokens(ent_standby_account.get()).get("account_nfts", [])
        operational_nfts = get_tokens(ent_operational_account.get()).get("account_nfts", [])
        standby_has_nft = any(nft["NFTokenID"] == nft_id for nft in standby_nfts)
        operational_has_nft = any(nft["NFTokenID"] == nft_id for nft in operational_nfts)

        text_standby_results.delete("1.0", tk.END)
        if not standby_has_nft:
            text_standby_results.insert("1.0", f"Transferred NFT {nft_id} to {ent_operational_account.get()}\nOffer ID: {offer_id}")
        else:
            text_standby_results.insert("1.0", f"Error: NFT {nft_id} still in Standby account!")

        text_operational_results.delete("1.0", tk.END)
        if operational_has_nft:
            text_operational_results.insert("1.0", f"Received NFT {nft_id} from {ent_standby_account.get()}\nOffer ID: {offer_id}")
            ent_operational_nft_id.delete(0, tk.END)
            ent_operational_nft_id.insert(0, nft_id)
            ent_standby_nft_id.delete(0, tk.END)
        else:
            text_operational_results.insert("1.0", f"Error: NFT {nft_id} not received!")

        get_standby_account_info()
        get_operational_account_info()

    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"Error: {str(e)}")

# Escrow 함수
def create_escrow(seed, amount, destination, condition=None, cancel_after=None, finish_after=None):
    try:
        check_balance(seed, amount)
        wallet = Wallet.from_seed(seed)
        sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
        escrow_create = EscrowCreate(
            account=wallet.classic_address,
            amount=xrp_to_drops(float(amount)),
            destination=destination,
            condition=condition,
            cancel_after=int(cancel_after) if cancel_after else None,
            finish_after=int(finish_after) if finish_after else None,
            sequence=sequence
        )
        response = xrpl.transaction.submit_and_wait(escrow_create, client, wallet)
        text_create_results.delete("1.0", tk.END)
        text_create_results.insert("1.0", json.dumps(response.result, indent=4))
    except Exception as e:
        text_create_results.delete("1.0", tk.END)
        text_create_results.insert("1.0", f"Error: {str(e)}")

def finish_escrow(seed, owner, offer_sequence, condition=None):
    try:
        check_balance(seed, 0)
        wallet = Wallet.from_seed(seed)
        sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
        escrow_finish = EscrowFinish(
            account=wallet.classic_address,
            owner=owner,
            offer_sequence=int(offer_sequence),
            condition=condition,
            sequence=sequence
        )
        response = xrpl.transaction.submit_and_wait(escrow_finish, client, wallet)
        text_finish_results.delete("1.0", tk.END)
        text_finish_results.insert("1.0", json.dumps(response.result, indent=4))
    except Exception as e:
        text_finish_results.delete("1.0", tk.END)
        text_finish_results.insert("1.0", f"Error: {str(e)}")

def cancel_escrow(seed, owner, offer_sequence):
    try:
        check_balance(seed, 0)
        wallet = Wallet.from_seed(seed)
        sequence = xrpl.account.get_next_valid_seq_number(wallet.classic_address, client)
        escrow_cancel = EscrowCancel(
            account=wallet.classic_address,
            owner=owner,
            offer_sequence=int(offer_sequence),
            sequence=sequence
        )
        response = xrpl.transaction.submit_and_wait(escrow_cancel, client, wallet)
        text_cancel_results.delete("1.0", tk.END)
        text_cancel_results.insert("1.0", json.dumps(response.result, indent=4))
    except Exception as e:
        text_cancel_results.delete("1.0", tk.END)
        text_cancel_results.insert("1.0", f"Error: {str(e)}")

def view_transaction_history():
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(transaction_history, indent=4))

# QR 코드 관련 함수
def get_nft_info(account):
    nfts = get_tokens(account).get("account_nfts", [])
    if not nfts:
        return None
    nft = nfts[0]  # 첫 번째 NFT를 사용
    return {
        "nft_id": nft["NFTokenID"],
        "uri": nft.get("URI", "No URI"),
        "issuer": nft["Issuer"],
        "taxon": nft["NFTokenTaxon"]
    }

def generate_qr_code(nft_info, filename=os.path.join(DATA_DIR, "nft_qr.png")):
    base_url = "http://localhost:5000/nft"  # 예시 URL
    nft_query = f"?nft_id={nft_info['nft_id']}&uri={nft_info['uri']}&issuer={nft_info['issuer']}&taxon={nft_info['taxon']}"
    qr_data = base_url + nft_query

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)
    return filename

def create_and_show_qr():
    try:
        account = ent_standby_account.get()
        if not account:
            raise Exception("Standby Account가 필요합니다.")
        
        nft_info = get_nft_info(account)
        if not nft_info:
            raise Exception("NFT가 없습니다.")
        
        qr_filename = generate_qr_code(nft_info)
        
        img = Image.open(qr_filename)
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        qr_image_label.configure(image=photo)
        qr_image_label.image = photo  # 참조 유지
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"QR 코드 생성 완료: {qr_filename}")
    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"Error: {str(e)}")

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
btn_generate_qr = tk.Button(master=frm_form, text="Generate QR Code", command=create_and_show_qr)
btn_generate_qr.grid(row=13, column=2, sticky="nsew")

btn_get_operational_account = tk.Button(master=frm_form, text="Get Operational Account", command=get_operational_account)
btn_get_operational_account.grid(row=0, column=3, sticky="nsew")
btn_get_op_account_info = tk.Button(master=frm_form, text="Get Op Account Info", command=get_operational_account_info)
btn_get_op_account_info.grid(row=1, column=3, sticky="nsew")
btn_op_send_xrp = tk.Button(master=frm_form, text="< Send XRP", command=operational_send_xrp)
btn_op_send_xrp.grid(row=2, column=3, sticky="nsew")

# 메인 루프
if __name__ == "__main__":
    window.mainloop()