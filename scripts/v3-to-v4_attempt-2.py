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
    blank_data['app_state']['assets']['params']['exocore_lz_app_address'] = '0xbDA4e8C4f1404A1ab48cCC878971d467c1410dEF'
    # blank_data['app_state']['epochs']['epochs'] = exported_data['app_state']['epochs']['epochs']
    # blank_data['app_state']['dogfood']['params'] = exported_data['app_state']['dogfood']['params']

    # Handle bank balances, including only 'aexo' and removing 'aevmos' from the coins list
    blank_data['app_state']['bank']['balances'] = [
        {
            'address': balance['address'],
            'coins': [coin for coin in balance['coins'] if coin['denom'] != 'aevmos']
        }
        for balance in exported_data['app_state']['bank']['balances']
        if any(coin['denom'] == 'aexo' for coin in balance['coins'])
    ]

    blank_data['app_state']['bank']['supply'] = [
        item for item in exported_data['app_state']['bank']['supply']
        if item['denom'] != 'aevmos'
    ]

    # Increment the last number of chain_id by 1
    # chain_id_parts = exported_data['chain_id'].split('-')
    # if len(chain_id_parts) > 1:
    #     new_version_number = int(chain_id_parts[-1]) + 1
    #     chain_id_parts[-1] = str(new_version_number)
    #     new_chain_id = '-'.join(chain_id_parts)
    # else:
    #     new_chain_id = chain_id_parts[0] + '-1'
    # blank_data['chain_id'] = new_chain_id

    blank_data['validators'] = []

    # Save the updated data to the output file
    with open(output_file, 'w') as file:
        json.dump(blank_data, file, indent=2)

    print(f"Genesis upgrade completed and saved to {output_file}")

# Call the function with your file paths
upgrade_genesis('240806_exported.json', 'blank.json', '240806_upgraded.json')

