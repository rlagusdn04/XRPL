import React from 'react';
import { useAccount } from './AccountContext';
import { useNavigate } from 'react-router-dom';

const MainPage = () => {
  const { seed, setSeed, account, setAccount } = useAccount();
  const navigate = useNavigate();

  const handleCheck = () => {
    if (!seed || !account) {
      alert('Seed와 Account를 모두 입력해주세요.');
      return;
    }
    // 여기서 추가 검증 로직 넣을 수 있음 (예: seed 형식 체크)
    alert('Seed와 Account가 저장되었습니다.');
    // Context에 저장은 setSeed, setAccount로 이미 반영됨
  };

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>XRPL Demo</h1>
      <div style={{ margin: '20px' }}>
        <label>
          Seed:
          <input
            value={seed}
            onChange={(e) => setSeed(e.target.value)}
            placeholder="Seed 입력"
            style={{ marginLeft: '10px', padding: '5px' }}
          />
        </label>
      </div>
      <div style={{ margin: '20px' }}>
        <label>
          Account:
          <input
            value={account}
            onChange={(e) => setAccount(e.target.value)}
            placeholder="Account 입력"
            style={{ marginLeft: '10px', padding: '5px' }}
          />
        </label>
      </div>
      <div style={{ margin: '20px' }}>
        <button onClick={handleCheck} style={{ padding: '5px 10px' }}>
          Check & Save
        </button>
      </div>
      <div style={{ display: 'flex', justifyContent: 'center', gap: '20px' }}>
        <button onClick={() => navigate('/mint-nft')} style={{ padding: '10px 20px' }}>
          Mint NFT
        </button>
        <button onClick={() => navigate('/transfer')} style={{ padding: '10px 20px' }}>
          Transfer XRP & NFT
        </button>
      </div>
    </div>
  );
};

export default MainPage;