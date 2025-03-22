import tkinter as tk
import xrpl
import json
from web3 import Web3
import threading
from time import sleep

# XRPL 모듈 임포트 (modules 디렉토리 기준)
from modules.mod1 import get_account, get_account_info, send_xrp
from modules.mod2 import (
    create_trust_line,
    send_currency,
    get_balance,
    configure_account,
)
from modules.mod3 import (
    mint_token,
    get_tokens,
    burn_token,
)

# Hardhat 로컬 네트워크 RPC URL 설정
hardhat_url = "http://127.0.0.1:8545"  # Hardhat 노드 기본 URL

# Web3 인스턴스 초기화
web3 = Web3(Web3.HTTPProvider(hardhat_url))

# Hardhat 로컬 네트워크에 배포된 스마트 컨트랙트 주소
# Hardhat 배포 후 얻은 주소를 여기에 입력하세요
contract_address = "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9"

# 컨트랙트 ABI (OwnershipTransferred 이벤트 포함)
contract_abi = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "tokenId", "type": "uint256"},
            {"indexed": False, "name": "assetId", "type": "string"}
        ],
        "name": "OwnershipTransferred",
        "type": "event"
    }
]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# 연결 확인 (선택 사항)
print("Web3 연결 상태:", web3.is_connected())

# Tkinter 창 생성
window = tk.Tk()
window.title("Quickstart Module")

# Rippling 변수
standbyRippling = tk.BooleanVar()
operationalRippling = tk.BooleanVar()

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

# Standby 필드 배치 (mod4 관련 필드 제거)
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

# Operational 계정 필드 (mod4 관련 필드 제거)
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

# 핸들러 정의 (mod4 관련 함수 제거)
## Module 3 핸들러
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
    results = burn_token(
        ent_standby_seed.get(),
        ent_standby_nft_id.get()
    )
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(results, indent=4))

def operational_mint_token():
    results = mint_token(
        ent_operational_seed.get(),
        ent_operational_uri.get(),
        ent_operational_flags.get(),
        ent_operational_transfer_fee.get(),
        ent_operational_taxon.get()
    )
    text_operational_results.delete("1.0", tk.END)
    text_operational_results.insert("1.0", json.dumps(results, indent=4))

def operational_get_tokens():
    results = get_tokens(ent_operational_account.get())
    text_operational_results.delete("1.0", tk.END)
    text_operational_results.insert("1.0", json.dumps(results, indent=4))

def operational_burn_token():
    results = burn_token(
        ent_operational_seed.get(),
        ent_operational_nft_id.get()
    )
    text_operational_results.delete("1.0", tk.END)
    text_operational_results.insert("1.0", json.dumps(results, indent=4))

## Module 2 핸들러
def standby_create_trust_line():
    results = create_trust_line(
        ent_standby_seed.get(),
        ent_standby_destination.get(),
        ent_standby_currency.get(),
        ent_standby_amount.get()
    )
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(results, indent=4))

def standby_send_currency():
    results = send_currency(
        ent_standby_seed.get(),
        ent_standby_destination.get(),
        ent_standby_currency.get(),
        ent_standby_amount.get()
    )
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(results, indent=4))

def standby_configure_account():
    results = configure_account(
        ent_standby_seed.get(),
        standbyRippling.get()
    )
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(results, indent=4))

def operational_create_trust_line():
    results = create_trust_line(
        ent_operational_seed.get(),
        ent_operational_destination.get(),
        ent_operational_currency.get(),
        ent_operational_amount.get()
    )
    text_operational_results.delete("1.0", tk.END)
    text_operational_results.insert("1.0", json.dumps(results, indent=4))

def operational_send_currency():
    results = send_currency(
        ent_operational_seed.get(),
        ent_operational_destination.get(),
        ent_operational_currency.get(),
        ent_operational_amount.get()
    )
    text_operational_results.delete("1.0", tk.END)
    text_operational_results.insert("1.0", json.dumps(results, indent=4))

def operational_configure_account():
    results = configure_account(
        ent_operational_seed.get(),
        operationalRippling.get()
    )
    text_operational_results.delete("1.0", tk.END)
    text_operational_results.insert("1.0", json.dumps(results, indent=4))

def get_balances():
    results = get_balance(ent_operational_account.get(), ent_standby_account.get())
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(results, indent=4))
    results = get_balance(ent_standby_account.get(), ent_operational_account.get())
    text_operational_results.delete("1.0", tk.END)
    text_operational_results.insert("1.0", json.dumps(results, indent=4))

## Module 1 핸들러
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

# EVM 이벤트 핸들러
def handle_evm_event(event):
    print(f"EVM Event - From: {event['args']['from']}, To: {event['args']['to']}, Token ID: {event['args']['tokenId']}")
    uri = json.dumps({
        "from": event["args"]["from"],
        "to": event["args"]["to"],
        "tokenId": event["args"]["tokenId"],
        "assetId": event["args"]["assetId"],
        "txHash": event["transactionHash"].hex()
    })
    try:
        results = mint_token(ent_standby_seed.get(), uri, "0", "0", "1")
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", json.dumps(results, indent=4))
    except Exception as e:
        text_standby_results.delete("1.0", tk.END)
        text_standby_results.insert("1.0", f"EVM NFT Mint Error: {str(e)}")

def listen_to_evm_events():
    try:
        event_filter = contract.events.OwnershipTransferred.createFilter(fromBlock='latest')
        print("이벤트 필터 생성 완료:", event_filter)
        while True:
            events = event_filter.get_new_entries()
            if events:
                print(f"감지된 이벤트 수: {len(events)}")
                for event in events:
                    window.after(0, handle_evm_event, event)
            sleep(2)
    except Exception as e:
        print(f"이벤트 리스닝 오류: {str(e)}")

# 스마트 컨트랙트 연결 확인 함수
def check_contract_connection():
    result = {}
    result["is_connected"] = web3.is_connected()
    result["contract_address"] = contract.address
    result["current_block"] = web3.eth.block_number
    text_standby_results.delete("1.0", tk.END)
    text_standby_results.insert("1.0", json.dumps(result, indent=4))

# 버튼 설정 (mod4 버튼 제거, 연결 확인 버튼 추가)
btn_get_standby_account = tk.Button(master=frm_form, text="Get Standby Account", command=get_standby_account)
btn_get_standby_account.grid(row=0, column=2, sticky="nsew")
btn_get_standby_account_info = tk.Button(master=frm_form, text="Get Standby Account Info", command=get_standby_account_info)
btn_get_standby_account_info.grid(row=1, column=2, sticky="nsew")
btn_standby_send_xrp = tk.Button(master=frm_form, text="Send XRP >", command=standby_send_xrp)
btn_standby_send_xrp.grid(row=2, column=2, sticky="nsew")
btn_standby_create_trust_line = tk.Button(master=frm_form, text="Create Trust Line", command=standby_create_trust_line)
btn_standby_create_trust_line.grid(row=4, column=2, sticky="nsew")
btn_standby_send_currency = tk.Button(master=frm_form, text="Send Currency >", command=standby_send_currency)
btn_standby_send_currency.grid(row=5, column=2, sticky="nsew")
btn_standby_get_balances = tk.Button(master=frm_form, text="Get Balances", command=get_balances)
btn_standby_get_balances.grid(row=6, column=2, sticky="nsew")
btn_standby_configure_account = tk.Button(master=frm_form, text="Configure Account", command=standby_configure_account)
btn_standby_configure_account.grid(row=7, column=0, sticky="nsew")
btn_standby_mint_token = tk.Button(master=frm_form, text="Mint NFT", command=standby_mint_token)
btn_standby_mint_token.grid(row=8, column=2, sticky="nsew")
btn_standby_get_tokens = tk.Button(master=frm_form, text="Get NFTs", command=standby_get_tokens)
btn_standby_get_tokens.grid(row=9, column=2, sticky="nsew")
btn_standby_burn_token = tk.Button(master=frm_form, text="Burn NFT", command=standby_burn_token)
btn_standby_burn_token.grid(row=10, column=2, sticky="nsew")

btn_get_operational_account = tk.Button(master=frm_form, text="Get Operational Account", command=get_operational_account)
btn_get_operational_account.grid(row=0, column=3, sticky="nsew")
btn_get_op_account_info = tk.Button(master=frm_form, text="Get Op Account Info", command=get_operational_account_info)
btn_get_op_account_info.grid(row=1, column=3, sticky="nsew")
btn_op_send_xrp = tk.Button(master=frm_form, text="< Send XRP", command=operational_send_xrp)
btn_op_send_xrp.grid(row=2, column=3, sticky="nsew")
btn_op_create_trust_line = tk.Button(master=frm_form, text="Create Trust Line", command=operational_create_trust_line)
btn_op_create_trust_line.grid(row=4, column=3, sticky="nsew")
btn_op_send_currency = tk.Button(master=frm_form, text="< Send Currency", command=operational_send_currency)
btn_op_send_currency.grid(row=5, column=3, sticky="nsew")
btn_op_get_balances = tk.Button(master=frm_form, text="Get Balances", command=get_balances)
btn_op_get_balances.grid(row=6, column=3, sticky="nsew")
btn_op_configure_account = tk.Button(master=frm_form, text="Configure Account", command=operational_configure_account)
btn_op_configure_account.grid(row=7, column=4, sticky="nsew")
btn_op_mint_token = tk.Button(master=frm_form, text="Mint NFT", command=operational_mint_token)
btn_op_mint_token.grid(row=8, column=3, sticky="nsew")
btn_op_get_tokens = tk.Button(master=frm_form, text="Get NFTs", command=operational_get_tokens)
btn_op_get_tokens.grid(row=9, column=3, sticky="nsew")
btn_op_burn_token = tk.Button(master=frm_form, text="Burn NFT", command=operational_burn_token)
btn_op_burn_token.grid(row=10, column=3, sticky="nsew")

# 스마트 컨트랙트 연결 확인 버튼 추가
btn_check_contract = tk.Button(master=frm_form, text="Check Contract Connection", command=check_contract_connection)
btn_check_contract.grid(row=11, column=2, columnspan=2, sticky="nsew")

# 메인 루프 및 EVM 리스너 시작
if __name__ == "__main__":
    evm_thread = threading.Thread(target=listen_to_evm_events, daemon=True)
    evm_thread.start()
    window.mainloop()