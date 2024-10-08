#!/usr/bin/env python

import json

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
    blank_data['app_state']['slashing']['missed_blocks'] = exported_data['app_state']['slashing']['missed_blocks']
    blank_data['app_state']['slashing']['signing_infos'] = exported_data['app_state']['slashing']['signing_infos']
    blank_data['app_state']['feemarket'] = exported_data['app_state']['feemarket']
    # We will change this later with CLI
    blank_data['app_state']['assets']['params']['exocore_lz_app_address'] = '0x0000000000000000000000000000000000000000'
    # blank_data['app_state']['epochs'] = exported_data['app_state']['epochs']
    blank_data['app_state']['dogfood']['params'] = exported_data['app_state']['dogfood']['params']

    # x/assets -> copied the gateway address, rest fed by generate.js
    # x/auth -> copied the genesis accounts
    # x/authz is empty
    # x/avs is empty
    # x/bank -> copied the balances and supply
    # x/capability is empty
    # x/crisis -> left unchanged to prevent x/crisis checks
    #             from being made (the denom `stake` doesn't exist on our chain)
    # x/delegation -> fed by generate.js
    # x/dogfood -> copied the params, rest fed by generate.js
    # x/epochs -> skipped, so counting down restarts from genesis
    # x/erc20 -> empty
    # x/evm -> copied
    # x/exomint -> empty, newer is preferred due to lower per-epoch amount
    # x/feegrant -> empty
    # x/feemarket -> not relevant so not copied
    # x/genutil -> empty
    # x/gov -> not used so not copied, has the wrong min denomination so no proposals possible
    # x/ibc -> empty
    # x/interchainaccounts -> empty
    # x/operator -> empty, will be fed by generate.js
    # x/oracle -> not copied, will be fed by generate.js
    # x/recovery -> not relevant so not copied
    # x/slashing -> not relevant so not copied
    # x/transfer -> not relevant so not copied
    # x/upgrade -> empty

    # Handle bank balances, including only 'hua' and removing 'aevmos' from the coins list
    blank_data['app_state']['bank']['balances'] = [
        {
            'address': balance['address'],
            'coins': [
                {
                    'amount': balance['coins'][0]['amount'],
                    'denom': 'hua',
                }
            ]
        }
        for balance in exported_data['app_state']['bank']['balances']
    ]

    blank_data['app_state']['bank']['supply'] = [
        {
            'amount': exported_data['app_state']['bank']['supply'][0]['amount'],
            'denom': 'hua',
        }
    ]

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
        json.dump(blank_data, file, indent=2)

    print(f"Genesis upgrade completed and saved to {output_file}")

# Call the function with your file paths
upgrade_genesis('genesis_export_v5_1008.json', 'blank.json', 'to_bootstrap_v6_1008.json')
