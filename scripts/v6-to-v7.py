#!/usr/bin/env python

import json

HOLESKY = 0x9d19
HOLESKY_SUFFIX = f"_{hex(HOLESKY)}"

def upgrade_genesis(exported_file, blank_file, output_file):
    # Load the content of the two genesis files
    with open(exported_file, 'r') as file:
        exported_data = json.load(file)
    with open(blank_file, 'r') as file:
        blank_data = json.load(file)

    # Do not increment initial_height by 1, since that is done during export.
    blank_data['initial_height'] = exported_data['initial_height']
    # copy over gas limit
    blank_data['consensus_params'] = exported_data['consensus_params']

    # Copy over the necessary app_state parts
    blank_data['app_state']['auth']['accounts'] = exported_data['app_state']['auth']['accounts']
    blank_data['app_state']['evm']['accounts'] = exported_data['app_state']['evm']['accounts']
    blank_data['app_state']['feemarket'] = exported_data['app_state']['feemarket']
    # We will change this later with CLI
    blank_data['app_state']['assets']['params']['exocore_lz_app_address'] = '0x0000000000000000000000000000000000000000'
    blank_data['app_state']['dogfood']['params'] = exported_data['app_state']['dogfood']['params']

    blank_data['app_state']['bank']['balances'] = exported_data['app_state']['bank']['balances']
    blank_data['app_state']['bank']['supply'] = exported_data['app_state']['bank']['supply']

    # remove Holesky
    blank_data['app_state']['assets']['client_chains'] = \
        [ elem for elem in exported_data['app_state']['assets']['client_chains']
            if int( elem['layer_zero_chain_id'] ) != HOLESKY ]

    deposits = []
    for deposit in exported_data['app_state']['assets']['deposits']:
        if deposit["staker"].endswith(HOLESKY_SUFFIX):
            continue
        subdeposits = []
        for subdeposit in deposit["deposits"]:
            if subdeposit["asset_id"].endswith(HOLESKY_SUFFIX):
                continue
            subdeposits.append(subdeposit)
        deposits.append({ "staker": deposit["staker"], "deposits": subdeposits })
    blank_data['app_state']['assets']['deposits'] = deposits

    operator_assets = []
    for operator_asset in exported_data['app_state']['assets']['operator_assets']:
        res = []
        for asset_state in operator_asset["assets_state"]:
            if asset_state["asset_id"].endswith(HOLESKY_SUFFIX):
                continue
            res.append(asset_state)
        operator_assets.append({ "operator": operator_asset["operator"], "assets_state": res })
    blank_data['app_state']['assets']['operator_assets'] = operator_assets

    blank_data['app_state']['assets']['tokens'] = \
        [ elem for elem in exported_data['app_state']['assets']['tokens']
            if int( elem['asset_basic_info']['layer_zero_chain_id'] ) != HOLESKY ]

    blank_data['app_state']['delegation']['associations'] = \
        [ elem for elem in exported_data['app_state']['delegation']['associations']
            if not elem['staker_id'].endswith(HOLESKY_SUFFIX) ]

    blank_data['app_state']['delegation']['delegation_states'] = \
        [ elem for elem in exported_data['app_state']['delegation']['delegation_states']
            if not elem['key'].split("/")[0].endswith(HOLESKY_SUFFIX) ]

    stakers_by_operator = []
    for staker_by_operator in exported_data['app_state']['delegation']['stakers_by_operator']:
        if staker_by_operator["key"].endswith(HOLESKY_SUFFIX):
            continue
        stakers = []
        for staker in staker_by_operator["stakers"]:
            if staker.endswith(HOLESKY_SUFFIX):
                continue
            stakers.append(staker)
        stakers_by_operator.append({ "key": staker_by_operator["key"], "stakers": stakers })
    blank_data['app_state']['delegation']['stakers_by_operator'] = stakers_by_operator

    blank_data['app_state']['delegation']['undelegations'] = \
        [ elem for elem in exported_data['app_state']['delegation']['undelegations']
            if not ( elem['staker_id'].endswith(HOLESKY_SUFFIX) or elem['asset_id'].endswith(HOLESKY_SUFFIX) ) ]

    blank_data['app_state']['dogfood'] = exported_data['app_state']['dogfood']
    blank_data['app_state']['dogfood']['params']['asset_ids'] = \
        [ elem for elem in exported_data['app_state']['dogfood']['params']['asset_ids']
            if not elem.endswith(HOLESKY_SUFFIX) ]

    blank_data['app_state']['operator'] = exported_data['app_state']['operator']

    oracle = exported_data['app_state']['oracle']
    oracle['index_recent_msg'] = None
    oracle['index_recent_params'] = None
    oracle['validator_update_block'] = None
    oracle['prices_list'] = []
    oracle['recent_msg_list'] = []
    oracle['recent_params_list'] = []
    oracle['staker_list_assets'] = []
    oracle['params']['slashing'] = blank_data['app_state']['oracle']['params']['slashing']

    tokens = []
    for token in oracle['params']['tokens']:
        token['asset_id'] = [ elem for elem in token['asset_id'].split(',') 
         if not elem.endswith(HOLESKY_SUFFIX) ]
        if len(token['asset_id']) > 0:
            token['asset_id'] = ",".join(token['asset_id'])
            tokens.append(token)
    oracle['params']['tokens'] = tokens

    feeders = []
    for feeder in oracle['params']['token_feeders']:
        if int( feeder['token_id'] ) > len(oracle['params']['tokens']):
            continue
        feeders.append(feeder)
    oracle['params']['token_feeders'] = feeders

    blank_data['app_state']['oracle'] = oracle

    # Increment the last number of chain_id by 1
    chain_id_parts = exported_data['chain_id'].split('-')
    if len(chain_id_parts) > 1:
        new_version_number = int(chain_id_parts[-1]) + 1
        chain_id_parts[-1] = str(new_version_number)
        new_chain_id = '-'.join(chain_id_parts)
    else:
        new_chain_id = chain_id_parts[0] + '-1'
    blank_data['chain_id'] = new_chain_id

    blank_data['validators'] = []

    # Save the updated data to the output file
    with open(output_file, 'w') as file:
        json.dump(blank_data, file, indent=2, sort_keys=True)

    print(f"Genesis upgrade completed and saved to {output_file}")

# Call the function with your file paths
upgrade_genesis('export_testnetV6_1203_og.json', 'blank.json', 'to_bootstrap_v7_1205.json')
