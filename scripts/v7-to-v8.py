#! /usr/bin/env python3

import json
import bech32
from typing import Any
import os

def convert_bech32_address(address: str) -> str:
    """Convert a bech32 address by changing 'exo' prefix to 'im'."""
    # this is the address of the module exomint, which has changed name to immint
    # so the address can not be simply converted; instead we replace it.
    if address == "exo1jek092vl820up8x4jz9v2g6wg7qw2qvy3wry2m":
        return "im15lxnnrpy39we7z49e0dm7c0ludl6ajz46hhyfd"
    # avs address for old chain id to new chain id: bech32
    elif address == "exo14gyfhggr7ajle6jysz9a84q8x53j2nzhugud8k":
        return "im1akm6vpm6k3wlwtjhhsh2py0erq6zjusw3r6tzg"
    try:
        # Decode the bech32 address
        prefix, data = bech32.bech32_decode(address)

        if prefix is None or data is None:
            return address

        # Replace 'exo' with 'im' in the prefix
        if 'exo' in prefix:
            new_prefix = prefix.replace('exo', 'im')
            # Convert the data back to bytes and encode with new prefix
            return bech32.bech32_encode(new_prefix, data)

        return address
    except Exception:
        # If any error occurs during conversion, return original address
        return address

def process_nested_dict(data: Any) -> Any:
    """Recursively process nested dictionary and convert bech32 addresses."""
    if isinstance(data, dict):
        return {
            k.replace(
                "exocore_chain_index", "imua_chain_index"
            ).replace(
                "exomint", "immint"
            ).replace(
                "exoslash", "imslash"
            ).replace(
                "task_addr", "task_address"
            ).replace(
                "avs_owner_address", "avs_owner_addresses"
            ).replace(
                "reward_addr", "reward_address"
            ):
            process_nested_dict(v) for k, v in data.items() if k != "slash_fraction_miss"
        }
    elif isinstance(data, list):
        return [process_nested_dict(item) for item in data]
    elif isinstance(data, str):
        # avs address for old chain id to new chain id: lowercase + checksum
        if "0xaa089ba103f765fcea44808bd3d4073523254c57" in data:
            data = data.replace("0xaa089ba103f765fcea44808bd3d4073523254c57", "0xedb7a6077ab45df72e57bc2ea091f9183429720e")
        if "0xAa089Ba103f765fCeA44808BD3d4073523254C57" in data:
            data = data.replace("0xAa089Ba103f765fCeA44808BD3d4073523254C57", "0xedb7a6077Ab45dF72e57BC2Ea091f9183429720e")
        if '/' in data:  # Handle path-like strings
            parts = data.split('/')
            converted_parts = [
                convert_bech32_address(part) if part.startswith('exo') else part
                for part in parts
            ]
            return '/'.join(converted_parts)
        elif data.startswith('exo'):
            if data == 'exomint':
                return 'immint'
            elif data == 'exo':
                return 'IMUA'
            elif 'exocoretestnet_233' in data:
                return data.replace('exocoretestnet_233', 'imuachaintestnet_233')
            else:
                return convert_bech32_address(data)
        return data
    else:
        return data

def upgrade_genesis(data: Any, blank_path: str) -> Any:
    with open(blank_path, 'r') as f:
        blank_data = json.load(f)

    # chain params
    blank_data['initial_height'] = data['initial_height']
    blank_data['consensus_params'] = data['consensus_params']
    blank_data['chain_id'] = "imuachaintestnet_233-8"

    # x/assets
    blank_data['app_state']['assets']['params']['gateways'] = [ data['app_state']['assets']['params']['exocore_lz_app_address'] ]
    # TODO: copy these but check that generate.mjs does not overwrite these if they exist
    # Ideally, generate.mjs should merge the Bootstrap data with the data below after this step.
    blank_data['app_state']['assets']['client_chains'] = data['app_state']['assets']['client_chains']
    blank_data['app_state']['assets']['tokens'] = data['app_state']['assets']['tokens']
    blank_data['app_state']['assets']['deposits'] = data['app_state']['assets']['deposits']
    blank_data['app_state']['assets']['operator_assets'] = data['app_state']['assets']['operator_assets']

    # x/auth -> accounts
    blank_data['app_state']['auth']['accounts'] = data['app_state']['auth']['accounts']

    # x/authz -> authorization
    blank_data['app_state']['authz']['authorization'] = data['app_state']['authz']['authorization']

    # leave x/avs unchanged, since x/dogfood will create the first avs and there are no others in use

    # x/bank -> balances, supply
    blank_data['app_state']['bank']['balances'] = data['app_state']['bank']['balances']
    blank_data['app_state']['bank']['supply'] = data['app_state']['bank']['supply']

    # x/capability -> leave unchanged
    # x/crisis -> leave unchanged

    # x/delegation -> copy
    blank_data['app_state']['delegation'] = data['app_state']['delegation']

    # x/dogfood to be filled by generate.mjs in addition to the data below
    blank_data['app_state']['dogfood'] = data['app_state']['dogfood']

    # x/epochs -> do not copy

    # x/feegrant simple copy
    blank_data['app_state']['feegrant'] = data['app_state']['feegrant']

    # x/evm -> accounts
    blank_data['app_state']['evm']['accounts'] = data['app_state']['evm']['accounts']

    # x/slashing -> missed_blocks, signing_infos
    blank_data['app_state']['slashing']['missed_blocks'] = data['app_state']['slashing']['missed_blocks']
    blank_data['app_state']['slashing']['signing_infos'] = data['app_state']['slashing']['signing_infos']

    # x/feemarket -> params
    blank_data['app_state']['feemarket']['params'] = data['app_state']['feemarket']['params']

    # x/dogfood -> params
    blank_data['app_state']['dogfood']['params'] = data['app_state']['dogfood']['params']

    # x/erc20 -> params
    blank_data['app_state']['erc20']['params'] = data['app_state']['erc20']['params']

    # x/feedistribution -> copy
    blank_data['app_state']['feedistribution']['params'] = data['app_state']['feedistribution']['params']

    # x/operator -> copy
    blank_data['app_state']['operator'] = data['app_state']['operator']
    for operator in blank_data['app_state']['operator']['operators']:
        if operator.get('operator_info', None) is None:
            raise Exception(f"operator {operator['operator_address']} has no operator_info")
        earnings_addr = operator['operator_info'].get('earnings_addr', None)
        approve_addr = operator['operator_info'].get('approve_addr', None)
        addr = operator.get('operator_address', None)
        # addr is primary, others will be removed in the next update
        if earnings_addr != addr and earnings_addr is not None and len(earnings_addr) > 0:
            raise Exception(f"operator {operator['operator_address']} has earnings_addr {earnings_addr} != operator_address {addr}")
        if approve_addr != addr and approve_addr is not None and len(approve_addr) > 0:
            raise Exception(f"operator {operator['operator_address']} has approve_addr {approve_addr} != operator_address {addr}")
        operator['operator_info']['earnings_addr'] = operator['operator_address']
        operator['operator_info']['approve_addr'] = operator['operator_address']
    # drop slash states
    blank_data['app_state']['operator']['slash_states'] = []

    # x/oracle -> copy
    blank_data['app_state']['oracle']['params'] = data['app_state']['oracle']['params']
    # but drop key slash_fraction_miss from params
    _ = blank_data['app_state']['oracle']['params']['slashing'].pop('slash_fraction_miss', None)
    blank_data['app_state']['oracle']['params']['slashing']['min_reported_per_window'] = "0.05"
    blank_data['app_state']['oracle']['params']['slashing']['reported_rounds_window'] = "10000"
    blank_data['app_state']['oracle']['params']['slashing']['slash_fraction_malicious'] = "0.05"

    for i, feeder in enumerate(blank_data['app_state']['oracle']['params']['token_feeders']):
        if i == 0:
            continue
        feeder['start_base_block'] = str( int( data['initial_height'] ) + 20 )

    # x/slashing -> missed_blocks, signing_infos to be dropped but others retained
    blank_data['app_state']['slashing'] = data['app_state']['slashing']
    blank_data['app_state']['slashing']['missed_blocks'] = []
    blank_data['app_state']['slashing']['signing_infos'] = []
    # new params so that validators are not slashed that often
    blank_data['app_state']['slashing']['params']['signed_blocks_window'] = "10000"
    blank_data['app_state']['slashing']['params']['min_signed_per_window'] = "0.05"
    blank_data['app_state']['slashing']['params']['slash_fraction_downtime'] = "0.00"
    blank_data['app_state']['slashing']['params']['slash_fraction_double_sign'] = "0.05"

    # x/ibc bug
    blank_data['app_state']['ibc']['client_genesis']['clients'] = []
    blank_data['app_state']['ibc']['connection_genesis']['connections'] = []

    return blank_data



def main():
    # Exported file path
    input_path = "/home/user/Downloads/Telegram Desktop/export_testnetV7_11543600.json"

    # Create output path with 'im' suffix
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    output_path = os.path.join(directory, f"{name}_im{ext}")

    # Read input JSON
    with open(input_path, 'r') as f:
        data = json.load(f)

    # Process the data
    processed_data = process_nested_dict(data)

    if 'imslash' not in processed_data['app_state']:
        processed_data['app_state']['imslash'] = {}
        processed_data['app_state']['imslash']['params'] = {}

    # Upgrade the file
    blank_path = "/home/user/.imuad/config/genesis.json"
    processed_data = upgrade_genesis(processed_data, blank_path)

    # Write output JSON
    output_path = os.path.join(directory, f"{name}_upgraded{ext}")
    with open(output_path, 'w') as f:
        json.dump(processed_data, f, indent=2)

    del processed_data
    # del data

    print(f"Step 2: Upgraded file saved as: {output_path}")

if __name__ == "__main__":
    main()