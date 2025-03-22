import tkinter as tk
import xrpl
import json
from web3 import Web3
import threading
from time import sleep
from datetime import datetime
import os  # 파일 저장용

# XRPL 모듈 임포트
from modules.mod1 import get_account, get_account_info, send_xrp
from modules.mod2 import create_trust_line, send_currency, get_balance, configure_account
from modules.mod3 import mint_token, get_tokens, burn_token

# Hardhat 로컬 네트워크 설정 (선택적 유지)
hardhat_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(hardhat_url))

# 스마트 컨트랙트 설정 (주소가 유효하지 않을 경우 예외 처리)
contract_address = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"  # 배포된 주소로 교체
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
window.title("XRPL NFT Platform with Server Upload")

# Rippling 변수
standbyRippling = tk.BooleanVar()
operationalRippling = tk.BooleanVar()

# 거래 내역 파일 경로 (서버 대체)
TRANSACTION_FILE = "transactions.json"

# 거래 내역 초기화
if os.path.exists(TRANSACTION_FILE):
    with open(TRANSACTION_FILE, "r") as f:
        transaction_history = json.load(f)
else:
    transaction_history = []

# Form 프레임
frm_form = tk.Frame(relief=tk.SUNKEN, borderwidth=3)
frm_form.pack()

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

def standby_burn_token():
    results = burn_token(ent_standby_seed.get(), ent_standby_nft_id.get())
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(results, indent=4))

# NFT 거래 함수 (소각/재발행으로 소유권 업데이트, 거래 내역 서버 업로드)
def transfer_nft():
    try:
        # XRP 결제: Standby -> Operational
        amount = ent_standby_amount.get()
        response = send_xrp(ent_standby_seed.get(), amount, ent_operational_account.get())
        if isinstance(response, dict) and "error" in response:
            raise Exception(response["error"])

        # 기존 NFT 소각
        nft_id = ent_standby_nft_id.get()
        if not nft_id:
            raise Exception("NFT ID가 필요합니다.")
        burn_token(ent_standby_seed.get(), nft_id)

        # 기존 URI 가져오기
        old_uri = ent_standby_uri.get() or '{"serial": "LUX123", "owner": "rStandbyAccount"}'
        old_data = json.loads(old_uri)
        old_data["owner"] = ent_operational_account.get()  # 소유권 업데이트

        # 새 NFT 발행 (Operational 계정에 기록)
        new_uri = json.dumps(old_data, indent=4)
        results = mint_token(ent_operational_seed.get(), new_uri, "0", "0", "1")

        # 거래 내역 생성 및 서버 업로드
        new_transaction = {
            "nft_id": nft_id,
            "from": ent_standby_account.get(),
            "to": ent_operational_account.get(),
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        transaction_history.append(new_transaction)
        with open(TRANSACTION_FILE, "w") as f:
            json.dump(transaction_history, f, indent=4)

        # 결과 출력
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", json.dumps(results, indent=4))
        text_operational_results.delete("1.0", tk.END)
        text_operational_results.insert("1.0", f"Transferred {amount} XRP and NFT to {ent_operational_account.get()}\nNew URI: {new_uri}")
        
        # 계정 정보 업데이트
        get_standby_account_info()
        get_operational_account_info()
    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"Error: {str(e)}")

# 거래 내역 조회 함수
def view_transaction_history():
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(transaction_history, indent=4))

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

# 스마트 컨트랙트 연결 확인 함수 (예외 처리 포함)
def check_contract_connection():
    try:
        if contract is None:
            raise ValueError("컨트랙트 연결이 초기화되지 않음")
        result = {
            "is_connected": web3.is_connected(),
            "contract_address": contract.address,
            "current_block": web3.eth.block_number
        }
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", json.dumps(result, indent=4))
    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"컨트랙트 연결 오류: {str(e)}. XRPL은 정상 작동합니다.")

# EVM 이벤트 핸들러 (예외 처리 포함)
def handle_evm_event(event):
    try:
        event_data = {
            "from": event["args"]["from"],
            "to": event["args"]["to"],
            "tokenId": event["args"]["tokenId"],
            "txHash": event["transactionHash"].hex()
        }
        print(f"감지된 이벤트: {json.dumps(event_data, indent=4)}")
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", json.dumps(event_data, indent=4))
    except Exception as e:
        print(f"EVM 이벤트 처리 오류: {str(e)}. XRPL은 정상 작동합니다.")

# 수정된 이벤트 리스닝 함수 (예외 처리 포함)
def listen_to_evm_events():
    if contract is None:
        print("컨트랙트 연결 없음. 이벤트 리스닝 건너뜀.")
        return
    last_block = web3.eth.block_number
    print(f"이벤트 리스닝 시작 - 초기 블록 번호: {last_block}")
    while True:
        try:
            current_block = web3.eth.block_number
            if current_block > last_block:
                events = contract.events.Transfer.get_all_entries()
                if events:
                    new_events = [event for event in events if event['blockNumber'] > last_block]
                    if new_events:
                        print(f"감지된 새 이벤트 수: {len(new_events)}")
                        for event in new_events:
                            window.after(0, handle_evm_event, event)
                last_block = current_block
            sleep(2)
        except Exception as e:
            print(f"이벤트 리스닝 오류: {str(e)}. XRPL은 정상 작동합니다.")
            sleep(2)

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
btn_standby_burn_token = tk.Button(master=frm_form, text="Burn NFT", command=standby_burn_token)
btn_standby_burn_token.grid(row=10, column=2, sticky="nsew")
btn_transfer_nft = tk.Button(master=frm_form, text="Transfer NFT >", command=transfer_nft)
btn_transfer_nft.grid(row=11, column=2, sticky="nsew")
btn_view_history = tk.Button(master=frm_form, text="View History", command=view_transaction_history)
btn_view_history.grid(row=12, column=2, sticky="nsew")
btn_check_contract = tk.Button(master=frm_form, text="Check Contract Connection", command=check_contract_connection)
btn_check_contract.grid(row=13, column=2, sticky="nsew")

btn_get_operational_account = tk.Button(master=frm_form, text="Get Operational Account", command=get_operational_account)
btn_get_operational_account.grid(row=0, column=3, sticky="nsew")
btn_get_op_account_info = tk.Button(master=frm_form, text="Get Op Account Info", command=get_operational_account_info)
btn_get_op_account_info.grid(row=1, column=3, sticky="nsew")
btn_op_send_xrp = tk.Button(master=frm_form, text="< Send XRP", command=operational_send_xrp)
btn_op_send_xrp.grid(row=2, column=3, sticky="nsew")

# 메인 루프 및 EVM 리스너 시작 (예외 처리로 안전하게)
if __name__ == "__main__":
    if contract is not None:
        evm_thread = threading.Thread(target=listen_to_evm_events, daemon=True)
        evm_thread.start()
    else:
        print("EVM 연결 없음. XRPL만 실행.")
    window.mainloop()