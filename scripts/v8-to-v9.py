#! /usr/bin/env python3

import math
import json
import argparse
from typing import Any

def upgrade_genesis(data: Any, blank_path, dogfood_addr, chain_id: str) -> Any:
    try:
        with open(blank_path, 'r') as f:
            blank_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f"Failed to load blank genesis file: {e}")
    # since these states remain unchanged, we can just copy them.
    # chain params -> copy
    blank_data['initial_height'] = data['initial_height']
    blank_data['consensus_params'] = data['consensus_params']
    blank_data['chain_id'] = chain_id

    # x/assets -> copy
    blank_data['app_state']['assets'] = data['app_state']['assets']

    # x/auth -> copy
    blank_data['app_state']['auth'] = data['app_state']['auth']

    # x/authz -> copy
    blank_data['app_state']['authz'] = data['app_state']['authz']

    # leave x/avs unchanged as default state., since x/dogfood will create the first avs 
    # and there are no others in use
    # x/bank -> copy
    blank_data['app_state']['bank'] = data['app_state']['bank']
    # x/capability -> leave unchanged as default state.
    # x/crisis -> leave unchanged as default state.

    # x/delegation -> copy
    blank_data['app_state']['delegation'] = data['app_state']['delegation']
    ## handle the updated delegation parameter structure.
    blank_data['app_state']['delegation']["params"] = {
        "instant_undelegation_penalty": 25 
    }

    # x/dogfood -> copy
    blank_data['app_state']['dogfood'] = data['app_state']['dogfood']

    # x/epochs -> do not copy, so epoch will start from 1
    # x/erc20 -> leave unchanged as default state.
    blank_data['app_state']['erc20'] = data['app_state']['erc20']
    # x/evidence -> leave unchanged as default state. clear all slash events

    # x/evm -> accounts
    # only copy accounts, as other states are the same as the default state.
    blank_data['app_state']['evm']['accounts'] = data['app_state']['evm']['accounts']

    # x/feedistribution -> use the default state, but replace the dogfood address with the correct one.
    blank_data['app_state']['feedistribution']['all_avs_reward_assets'][0]['avs'] = dogfood_addr
    
    # x/feegrant simple copy
    blank_data['app_state']['feegrant'] = data['app_state']['feegrant']
    # x/feemarket -> params
    blank_data['app_state']['feemarket']['params'] = data['app_state']['feemarket']['params']
    # x/genutil simple copy
    blank_data['app_state']['genutil'] = data['app_state']['genutil']
    # x/gov simple copy
    blank_data['app_state']['gov'] = data['app_state']['gov']
    # x/ibc bug
    blank_data['app_state']['ibc']['client_genesis']['clients'] = []
    blank_data['app_state']['ibc']['connection_genesis']['connections'] = []
    # x/immint simple copy
    blank_data['app_state']['immint'] = data['app_state']['immint']
    # x/imslash leave unchanged as default state
    # x/interchainaccounts -> leave unchanged as default state.

    # x/operator -> copy
    blank_data['app_state']['operator'] = data['app_state']['operator']
    # drop slash states
    blank_data['app_state']['operator']['slash_states'] = []
    # set an empty value for the new field.
    blank_data['app_state']['operator']['operator_asset_usd_values'] = []
    # unjail all validators
    unjailed = []
    for state in blank_data['app_state']['operator']['opt_states']:
        if state['opt_info'].get('jailed'):
            # convert the jailed operator to unjailed
            state['opt_info']['jailed'] = False
            addr = state['key'].split("/")[0]
            unjailed.append(addr)
        # set an empty value for the new field.
        state['opt_info']['jail_toggle_heights'] = []
    for operator in unjailed:
        # find the usd value
        obj = [ o for o in blank_data['app_state']['operator']['operator_usd_values'] if o['key'] == f"{dogfood_addr}/{operator}" ]
        if len(obj) == 0:
            raise Exception(f"operator {operator} not found in operator_usd_values")
        usd_value = int( math.floor( float( obj[0]['opted_usd_value']['active_usd_value'] ) ) )
        if usd_value == 0:
            continue
        # and the consensus key
        obj2 = [ o for o in blank_data['app_state']['operator']['operator_records'] if o['operator_address'] == operator ]
        if len(obj2) == 0:
            raise Exception(f"operator {operator} not found in operator_records")
        cons_key = obj2[0]['chains'][0][ 'consensus_key' ]
        # check that cons key does not exist in the validator set
        if any(v['public_key'] == cons_key for v in blank_data['app_state']['dogfood']['val_set']):
            continue
        # append to validator set
        blank_data['app_state']['dogfood']['val_set'].append({
            'power': str(usd_value),
            'public_key': cons_key,
        })
    # sort blank_data by power and then public key descending
    blank_data['app_state']['dogfood']['val_set'].sort(key=lambda x: (-int(x['power']), x['public_key']), reverse=False)
    # update the last voting power
    last_total_power = 0
    for validator in blank_data['app_state']['dogfood']['val_set']:
        last_total_power += int(validator['power'])
    blank_data['app_state']['dogfood']['last_total_power'] = str(last_total_power)

    # x/oracle -> copy
    blank_data['app_state']['oracle']['params'] = data['app_state']['oracle']['params']
    ## set a default value for the new field
    blank_data['app_state']['oracle']['params']['piece_size_byte'] = "48000"
    ## todo: there might be other necessary operations for the oracle module 
    blank_data['app_state']['oracle']['params']['rules'] = [
        {},
        {"source_ids":["0"]},
        {"source_ids":["1"]},
        {"source_ids":["0"], "nom":{"source_ids":["1"], "minimum": "1"}},
    ]
    blank_data['app_state']['oracle']['params']['epoch_identifier'] = "day"
    tokens = blank_data['app_state']['oracle']['params']['tokens']
    feeders = blank_data['app_state']['oracle']['params']['token_feeders']
    initial_height = int(data['initial_height'])
    for i, feeder in enumerate(feeders):
        if i == 0:
            continue  # skip the first feeder
        token_id = int(feeder['token_id'])
        token = tokens[token_id]
        token_name = token.get('name', '')
        if token_name.startswith('nst'):
            feeder['rule_id'] = "3"
        else:
            feeder['rule_id'] = "2"
        feeder['start_base_block'] = str(initial_height + 20)

    # x/slashing -> missed_blocks, signing_infos to be dropped but others retained
    blank_data['app_state']['slashing'] = data['app_state']['slashing']
    blank_data['app_state']['slashing']['missed_blocks'] = []
    blank_data['app_state']['slashing']['signing_infos'] = []

    # x/transfer -> leave unchanged as default state.
    # x/upgrade -> leave unchanged as default state.
    # x/vesting -> leave unchanged as default state.

    return blank_data



def main():
    parser = argparse.ArgumentParser(description="Upgrade a genesis JSON file.")
    parser.add_argument("--input", "-i", required=True, help="Path to input genesis file")
    parser.add_argument("--output", "-o", required=True, help="Path to output upgraded file")
    parser.add_argument("--blank", "-n", required=True, help="Path to blank genesis file for upgrade reference")
    parser.add_argument("--dogfood_addr", "-d", required=True, help="Dogfood address for testnet")
    parser.add_argument("--chain_id", "-c", required=True, help="Chain id")
    args = parser.parse_args()

    # Read input JSON
    try:
        with open(args.input, 'r') as f:
            genesis_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f"Failed to load input genesis file: {e}")

    # Upgrade the file
    genesis_data = upgrade_genesis(genesis_data, args.blank, args.dogfood_addr, args.chain_id)

    # Write output JSON
    try:
        with open(args.output, 'w') as f:
            json.dump(genesis_data, f, indent=2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise Exception(f"Failed to load output genesis file: {e}")

    print(f"Step 2: Upgraded file saved as: {args.output}")

if __name__ == "__main__":
    main()
