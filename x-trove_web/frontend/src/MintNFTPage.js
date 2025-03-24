import React, { useState } from 'react';
import { useAccount } from './AccountContext';
import * as api from './api';

const MintNFTPage = () => {
  const { seed } = useAccount();
  const [uri, setUri] = useState('');
  const [flags, setFlags] = useState('');
  const [transferFee, setTransferFee] = useState('');
  const [taxon, setTaxon] = useState('');
  const [results, setResults] = useState('');
  const [qrCodeUrl, setQrCodeUrl] = useState('');

  const handleApiCall = async (apiCall, params) => {
    try {
      const response = await apiCall(params);
      if (!response || !response.data) throw new Error('응답 데이터가 없습니다.');
      const data = response.data;
      setResults(JSON.stringify(data, null, 2));

      if (data.TransactionResult === 'tesSUCCESS' && data.qr_code) {
        setQrCodeUrl(`http://localhost:5000/static/${data.qr_code}`);
        console.log('QR Code URL:', `http://localhost:5000/static/${data.qr_code}`);
      }
    } catch (error) {
      setResults(JSON.stringify({ error: error.response?.data?.error || error.message }, null, 2));
      setQrCodeUrl('');
    }
  };

  const handleMint = () => {
    if (!seed) {
      setResults(JSON.stringify({ error: "Seed가 필요합니다." }, null, 2));
      return;
    }
    handleApiCall(api.mintNft, { seed, uri, flags, transferFee, taxon });
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Mint NFT</h1>
      <div style={{ margin: '20px' }}>
        <label>
          NFT URI: <input value={uri} onChange={(e) => setUri(e.target.value)} style={{ padding: '5px' }} />
        </label>
      </div>
      <div style={{ margin: '20px' }}>
        <label>
          Flags: <input value={flags} onChange={(e) => setFlags(e.target.value)} style={{ padding: '5px' }} />
        </label>
      </div>
      <div style={{ margin: '20px' }}>
        <label>
          Transfer Fee: <input value={transferFee} onChange={(e) => setTransferFee(e.target.value)} style={{ padding: '5px' }} />
        </label>
      </div>
      <div style={{ margin: '20px' }}>
        <label>
          Taxon: <input value={taxon} onChange={(e) => setTaxon(e.target.value)} style={{ padding: '5px' }} />
        </label>
      </div>
      <button onClick={handleMint} disabled={!seed} style={{ padding: '10px 20px' }}>
        Mint NFT
      </button>
      <pre style={{ marginTop: '20px', textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>{results}</pre>
      {qrCodeUrl && (
        <div style={{ marginTop: '20px' }}>
          <h3>Generated QR Code:</h3>
          <img src={qrCodeUrl} alt="NFT QR Code" style={{ maxWidth: '200px' }} />
        </div>
      )}
    </div>
  );
};

export default MintNFTPage;