import React, { createContext, useState, useContext } from 'react';

const AccountContext = createContext();

export const AccountProvider = ({ children }) => {
  const [seed, setSeed] = useState('');
  const [account, setAccount] = useState('');

  return (
    <AccountContext.Provider value={{ seed, setSeed, account, setAccount }}>
      {children}
    </AccountContext.Provider>
  );
};

export const useAccount = () => useContext(AccountContext);