# Exocore Release Testnet

## Testnet Details

- **Chain-ID**: `exocoretestnet_233-5`
- **Launch date**: 2024-09-11
- **Current Exocore Version:** [`v1.0.4`](https://github.com/ExocoreNetwork/exocore/releases/tag/v1.0.4) (upgraded with genesis at height `7328987`)
- **Launch Exocore Version:** `release/v1.0.4`
- **Genesis File:** [in this repository](genesis.json.gz), verify with `shasum -a 256 genesis.json`
- **Genesis sha256sum**: `d4adc4dbf45880b10ce67594fe529bc09510cba4812aa0e2f96634d2d2d8de25`

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
* `join-release-testnet.sh` will create a `exocored` service.
* Script must be run either as root or from a sudoer account.
* Script will attempt to download the amd64 binary from the Exocore [releases](https://github.com/ExocoreNetwork/exocore/releases) page. You can modify the `CHAIN_BINARY_URL` to match your target architecture if needed.

#### State Sync Option

* By default, the script will attempt to use state sync to catch up quickly to the current height. To turn off state sync, set `STATE_SYNC` to `false`.
