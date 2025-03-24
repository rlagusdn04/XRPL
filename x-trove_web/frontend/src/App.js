import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AccountProvider } from './AccountContext';
import MainPage from './MainPage';
import MintNFTPage from './MintNFTPage';
import TransferPage from './TransferPage';

const App = () => {
  return (
    <AccountProvider>
      <Router>
        <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/mint-nft" element={<MintNFTPage />} />
          <Route path="/transfer" element={<TransferPage />} />
        </Routes>
      </Router>
    </AccountProvider>
  );
};

export default App;