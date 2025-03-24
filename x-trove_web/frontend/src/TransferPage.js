import React, { useState } from 'react';
import { useAccount } from './AccountContext';
import * as api from './api';

const TransferPage = () => {
  const { seed, account } = useAccount();
  const [destination, setDestination] = useState('rNCFfQ8mB4miBfbYSnX9agwS8kN9NxKTxY');
  const [amount, setAmount] = useState('10');
  const [nftId, setNftId] = useState('');
  const [results, setResults] = useState('');

  const handleApiCall = async (apiCall, params) => {
    console.log('Sending API request:', { api: apiCall.name, params });
    try {
      const response = await apiCall(params);
      if (!response || !response.data) throw new Error('응답 데이터가 없습니다.');
      setResults((prev) => prev + '\n' + JSON.stringify(response.data, null, 2));
      return response.data;
    } catch (error) {
      console.error('API call failed:', error.response?.data || error.message);
      setResults((prev) => prev + '\n' + JSON.stringify({ error: error.response?.data?.error || error.message }, null, 2));
      throw error;
    }
  };

  const handleTransfer = async () => {
    if (!seed || !account || !destination || !amount || !nftId) {
      setResults(JSON.stringify({ error: "모든 필수 값이 필요합니다." }, null, 2));
      return;
    }

    setResults('');
    try {
      // 1. XRP 전송
      await handleApiCall(api.sendXrp, { seed, amount, destination });

      // 2. NFT 전송 오퍼 생성
      const destinationSeed = 'sYourTestDestinationSeed'; // 실제 시드로 교체 필요
      const nftOffer = await handleApiCall(api.transferNft, { seed: destinationSeed, nftokenId: nftId, destination: account });
      const offerId = nftOffer.offer_id;

      // 3. NFT 오퍼 수락
      await handleApiCall(api.acceptNftOffer, { seed, offerId });
    } catch (error) {
      // 에러는 handleApiCall에서 처리됨
    }
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Transfer XRP & Receive NFT</h1>
      <div style={{ margin: '20px' }}>
        <label>
          Destination: <input value={destination} onChange={(e) => setDestination(e.target.value)} style={{ padding: '5px' }} />
        </label>
      </div>
      <div style={{ margin: '20px' }}>
        <label>
          XRP Amount: <input value={amount} onChange={(e) => setAmount(e.target.value)} style={{ padding: '5px' }} />
        </label>
      </div>
      <div style={{ margin: '20px' }}>
        <label>
          NFT ID (상대방 소유): <input value={nftId} onChange={(e) => setNftId(e.target.value)} style={{ padding: '5px' }} />
        </label>
      </div>
      <button onClick={handleTransfer} disabled={!seed || !account || !destination || !amount || !nftId} style={{ padding: '10px 20px' }}>
        Transfer XRP & Receive NFT
      </button>
      <pre style={{ marginTop: '20px', textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>{results}</pre>
    </div>
  );
};

export default TransferPage;