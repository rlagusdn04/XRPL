# -*- coding: utf-8 -*-

#!git clone https://github.com/rlagusdn04/XRPL

import os
os.chdir("/content")  # 저장소 경로로 이동
#!pwd

from google.colab import drive
drive.mount('/content/drive')

# nest_asyncio와 xrpl-py 설치
#!pip install nest_asyncio xrpl-py

# Colab 환경의 asyncio event loop 문제 해결
#AsyncIO: 비동기 프로그래밍을 위한 모듈, CPU작업과 IO작업을 병렬 처리
import nest_asyncio
nest_asyncio.apply() # 병렬 처리 시 중첩된 event loop 사용을 허용

# 필요한 모듈 임포트
from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet
from xrpl.account import get_balance
from xrpl.models.requests import ServerInfo  # 요청 객체 임포트

# XRPL 테스트넷 엔드포인트 설정 및 연결 확인
testnet_url = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(testnet_url)

server_info = client.request(ServerInfo())  # dict 대신 ServerInfo() 객체 사용
print("서버 정보:", server_info.result)

# 새로운 테스트넷 지갑 생성 (Faucet 이용)
wallet = generate_faucet_wallet(client)
print(f"지갑 주소: {wallet.classic_address}")
print(f"비밀키: {wallet.seed}")

# 생성된 지갑의 XRP 잔액 조회
balance = get_balance(wallet.classic_address, client)
print(f"잔액: {balance} XRP")

