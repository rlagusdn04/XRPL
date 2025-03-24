from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from modules.mod1 import get_account, get_account_info, send_xrp
from modules.mod2 import create_trust_line, send_currency, get_balance, configure_account
from modules.mod3 import mint_token, get_tokens, transfer_token
from modules.mod4 import create_sell_offer, accept_sell_offer, create_buy_offer, accept_buy_offer, get_offers, \
    cancel_offer
import qrcode
import os

app = Flask(__name__, static_folder='backend/static', static_url_path='/static')
CORS(app)  # CORS 설정


def generate_qr_code(data, filepath):
    import qrcode
    img = qrcode.make(data)

    # 파일 경로에서 디렉터리 부분 추출
    directory = os.path.dirname(filepath)

    # 디렉터리가 존재하지 않으면 생성
    if not os.path.exists(directory):
        os.makedirs(directory)

    img.save(filepath)
    return filepath


@app.route('/api//get-account', methods=['POST'])
def api_get_account():
    data = request.json
    seed = data.get('seed', '') if isinstance(data, dict) else ''  # 프론트엔드에서 받은 seed 추출
    print(f"Received seed: {seed}")
    print(f"Data type: {type(data)}")

    try:
        wallet = get_account(seed)  # 받은 seed 전달
        return jsonify({'address': wallet.classic_address, 'seed': wallet.seed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 나머지 엔드포인트
@app.route('/api/account/info', methods=['POST'])
def api_get_account_info():
    data = request.json
    account_id = data.get('accountId')['accountId']
    print(f"Received accountId: {account_id}")
    info = get_account_info(account_id)
    print(info)
    return jsonify(info)  # 오류 메시지도 포함하여 반환


@app.route('/api/send-xrp', methods=['POST'])
def api_send_xrp():
    data = request.json
    print(f"Received xrp: {data}")
    seed = data.get('seed')
    amount = data.get('amount')
    print(f"Received seed: {seed}, Received amount: {amount}")
    destination = data.get('destination')
    result = send_xrp(seed, amount, destination)
    return jsonify(result.result if hasattr(result, 'result') else result)


@app.route('/api/trustline', methods=['POST'])
def api_create_trust_line():
    data = request.json
    seed = data.get('seed')['seed']
    issuer = data.get('issuer')['issuer']
    currency = data.get('currency')['currency']
    amount = data.get('amount')['amount']
    result = create_trust_line(seed, issuer, currency, amount)
    return jsonify(result.result if hasattr(result, 'result') else result)


@app.route('/api/send-currency', methods=['POST'])
def api_send_currency():
    data = request.json
    seed = data.get('seed')['seed']
    destination = data.get('destination')['destination']
    currency = data.get('currency')['currency']
    amount = data.get('amount')['amount']
    result = send_currency(seed, destination, currency, amount)
    return jsonify(result.result if hasattr(result, 'result') else result)


@app.route('/api/balance', methods=['POST'])
def api_get_balance():
    data = request.json['sbSeed']
    print(f"Received balance: {data}")
    sb_seed = data.get('sbSeed')
    op_seed = data.get('opSeed')
    result = get_balance(sb_seed, op_seed)
    return jsonify(result)


@app.route('/api/configure', methods=['POST'])
def api_configure_account():
    data = request.json
    seed = data.get('seed')['seed']
    default_setting = data.get('defaultSetting')['defaultSetting']
    result = configure_account(seed, default_setting)
    return jsonify(result.result if hasattr(result, 'result') else result)


@app.route('/api/mint-nft', methods=['POST'])
def api_mint_nft():
    data = request.json
    seed = data.get('seed')
    uri = data.get('uri')
    flags = data.get('flags')
    transfer_fee = data.get('transferFee')
    taxon = data.get('taxon')

    result = mint_token(seed, uri, flags, transfer_fee, taxon)

    # 트랜잭션 결과 확인
    transaction_result = result.get('meta', {}).get('TransactionResult')
    if isinstance(result, dict) and transaction_result == 'tesSUCCESS':
        nftoken_id = result.get('meta', {}).get('nftoken_id', 'unknown')  # 수정된 부분
        if nftoken_id == 'unknown':
            return jsonify({"error": "NFT ID를 찾을 수 없습니다.", "result": result})

        nft_url = f"https://testnet.xrpl.org/nft/{nftoken_id}"

        # QR 코드 생성
        qr_filename = generate_qr_code(nft_url, f"static/nft_{nftoken_id}_qr.png")  # 경로 명확히 지정
        print(f"QR 코드 생성 완료: {qr_filename}")  # 디버깅 출력

        result['qr_code'] = qr_filename

    return jsonify(result.result if hasattr(result, 'result') else result)


@app.route('/api/nfts', methods=['POST'])
def api_get_nfts():
    data = request.json['account']
    print(f'Received nfts: {data}')
    account = data.get('account')
    result = get_tokens(account)
    return jsonify(result)


@app.route('/api/transfer-nft', methods=['POST'])
def api_transfer_nft():
    try:
        data = request.json
        print(data)
        seed = data.get('seed')  # 보내는 계정의 seed
        nftoken_id = data.get('nftokenId')
        destination = data.get('destination')
        destination_seed = data.get('destinationSeed')  # 수신자 계정의 seed

        if not all([seed, nftoken_id, destination, destination_seed]):
            print(
                f"Missing parameters: seed={seed}, nftokenId={nftoken_id}, destination={destination}, destinationSeed={destination_seed}")
            return jsonify({"error": "Missing required parameters"}), 400

        result = transfer_token(seed, nftoken_id, destination, destination_seed)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sell-offer', methods=['POST'])
def api_create_sell_offer():
    data = request.json
    seed = data.get('seed')
    amount = data.get('amount')
    nftoken_id = data.get('nftokenId')
    expiration = data.get('expiration')
    destination = data.get('destination')
    result = create_sell_offer(seed, amount, nftoken_id, expiration, destination)
    return jsonify(result.result if hasattr(result, 'result') else result)


@app.route('/api/accept-sell', methods=['POST'])
def api_accept_sell_offer():
    data = request.json
    seed = data.get('seed')
    offer_index = data.get('offerIndex')
    result = accept_sell_offer(seed, offer_index)
    return jsonify(result.result if hasattr(result, 'result') else result)


@app.route('/api/buy-offer', methods=['POST'])
def api_create_buy_offer():
    data = request.json
    seed = data.get('seed')
    amount = data.get('amount')
    nft_id = data.get('nftId')
    owner = data.get('owner')
    expiration = data.get('expiration')
    destination = data.get('destination')
    result = create_buy_offer(seed, amount, nft_id, owner, expiration, destination)
    return jsonify(result.result if hasattr(result, 'result') else result)


@app.route('/api/accept-buy', methods=['POST'])
def api_accept_buy_offer():
    data = request.json
    seed = data.get('seed')
    offer_index = data.get('offerIndex')
    result = accept_buy_offer(seed, offer_index)
    return jsonify(result.result if hasattr(result, 'result') else result)


@app.route('/api/offers', methods=['POST'])
def api_get_offers():
    data = request.json
    nft_id = data.get('nftId')
    result = get_offers(nft_id)
    return jsonify(result)


@app.route('/api/cancel-offer', methods=['POST'])
def api_cancel_offer():
    data = request.json
    seed = data.get('seed')
    nftoken_offer_ids = data.get('nftokenOfferIds')
    result = cancel_offer(seed, nftoken_offer_ids)
    return jsonify(result.result if hasattr(result, 'result') else result)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('backend/static', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
