// import axios from 'axios';
//
// const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
//
// export const getAccount = (seed) => {
//   console.log('Sending seed:', seed);
//   console.log('Request URL:', `${API_URL}/account`);
//   return axios.post(`${API_URL}/account`, { seed: seed })
//     .catch(error => {
//       console.error('Axios 오류:', error.response || error);
//       throw error;
//     });
// };
//
// export const getAccountInfo = (accountId) => axios.post(`${API_URL}/account/info`, { accountId });
// export const sendXrp = (seed, amount, destination) => axios.post(`${API_URL}/send-xrp`, { seed, amount, destination });
// export const createTrustLine = (seed, issuer, currency, amount) => axios.post(`${API_URL}/trustline`, { seed, issuer, currency, amount });
// export const sendCurrency = (seed, destination, currency, amount) => axios.post(`${API_URL}/send-currency`, { seed, destination, currency, amount });
// export const getBalance = (sbSeed, opSeed) => axios.post(`${API_URL}/balance`, { sbSeed, opSeed });
// export const configureAccount = (seed, defaultSetting) => axios.post(`${API_URL}/configure`, { seed, defaultSetting });
// export const mintNft = (seed, uri, flags, transferFee, taxon) => axios.post(`${API_URL}/mint-nft`, { seed, uri, flags, transferFee, taxon });
// export const getNfts = (account) => axios.post(`${API_URL}/nfts`, { account });
// export const transferNft = (seed, nftokenId, destination) => {
//     return axios.post(`${API_URL}/transfer-nft`, {
//         seed,
//         nftokenId,
//         destination
//     });
// };
// export const createSellOffer = (seed, amount, nftokenId, expiration, destination) => axios.post(`${API_URL}/sell-offer`, { seed, amount, nftokenId, expiration, destination });
// export const acceptSellOffer = (seed, offerIndex) => axios.post(`${API_URL}/accept-sell`, { seed, offerIndex });
// export const createBuyOffer = (seed, amount, nftId, owner, expiration, destination) => axios.post(`${API_URL}/buy-offer`, { seed, amount, nftId, owner, expiration, destination });
// export const acceptBuyOffer = (seed, offerIndex) => axios.post(`${API_URL}/accept-buy`, { seed, offerIndex });
// export const getOffers = (nftId) => axios.post(`${API_URL}/offers`, { nftId });
// export const cancelOffer = (seed, nftokenOfferIds) => axios.post(`${API_URL}/cancel-offer`, { seed, nftokenOfferIds });
import axios from 'axios';

const API_URL = 'http://localhost:5000/api'; // 백엔드 URL 맞춰서 수정

export const getAccount = (params) => axios.post(`${API_URL}/get-account`, params);
export const getAccountInfo = (params) => axios.post(`${API_URL}/get-account-info`, params);
export const sendXrp = (params) => axios.post(`${API_URL}/send-xrp`, params);
export const mintNft = (params) => axios.post(`${API_URL}/mint-nft`, params);
export const transferNft = (params) => axios.post(`${API_URL}/transfer-nft`, params);
export const acceptNftOffer = (params) => axios.post(`${API_URL}/accept-nft-offer`, params);