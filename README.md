# Imuachain Release Testnet

## Testnet Details

- **Chain-ID**: `imuachaintestnet_233-8`
- **Launch date**: 2025-02-27
- **Current Exocore Version:** [`v1.1.0`](https://github.com/imua-xyz/imuachain/releases/tag/v1.1.0) 
- **Current Price Feeder Version:** [`v0.2.4`](https://github.com/imua-xyz/price-feeder/releases/tag/v0.2.4)
- **Genesis File:** [in this repository](genesis/imuachaintestnet_233-8.json), verify with `shasum -a 256 genesis.json`
- **Genesis sha256sum**: `961c19865b1d2d582fc71e565a06ac014f983a753560752961115220bdc5a6c2`

### Endpoints

Endpoints are exposed as subdomains for the sentry and snapshot nodes (described below) as follows:

* `https://api-cosmos-rest.exocore-restaking.com`
* `https://api-eth.exocore-restaking.com`

Seed nodes:

1. `seed1t.exocore-restaking.com`
2. `seed2t.exocore-restaking.com`

### Seeds

You can add these in your seeds list.

```
5dfa2ddc4ce3535ef98470ffe108e6e12edd1955@seed2t.exocore-restaking.com:26656
4cc9c970fe52be4568942693ecfc2ee2cdb63d44@seed1t.exocore-restaking.com:26656
```

### Block Explorers

  - https://exoscan.org/

### Bash Script

Run the script provided in this repo to join the provider chain:
* `join-release-testnet.sh` will create a `imuad` service.
* Script must be run either as root or from a sudoer account.
* Script will attempt to download the amd64 binary from the Exocore [releases](https://github.com/ExocoreNetwork/exocore/releases) page. You can modify the `CHAIN_BINARY_URL` to match your target architecture if needed.

#### State Sync Option

* By default, the script will sync from genesis block, to turn on state sync to catch up quickly to the current height, set `STATE_SYNC` to `true`.
