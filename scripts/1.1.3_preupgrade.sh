#!/bin/bash

set -e

log() {
  echo "[INFO] $1"
}

error_exit() {
  echo "[ERROR] $1" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || error_exit "$1 not installed. More info: <https://stedolan.github.io/jq/download/>"
}

backup_configs() {
  local dir="$1"
  local timestamp="$2"
  for file in "$dir"/config/*.toml "$dir"/config/*.json; do
    [ -f "$file" ] && cp "$file" "$file.$timestamp.old"
  done
}

replace_file() {
  local src="$1"
  local dest="$2"
  local desc="$3"
  [ -f "$src" ] && cp "$src" "$dest" && log "Successfully replaced $desc" || error_exit "$src does not exist. Aborting."
}

update_chain_id() {
  local genesis="$1"
  local client_toml="$2"
  local chain_id
  chain_id=$(jq -r '.chain_id' "$genesis")
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/^chain-id = .*/chain-id = \"$chain_id\"/" "$client_toml"
  else
    sed -i "s/^chain-id = .*/chain-id = \"$chain_id\"/" "$client_toml"
  fi
  log "Updated chain-id in client.toml to $chain_id"
}

clear_data_dir() {
  local data_dir="$1"
  [ -d "$data_dir" ] || error_exit "Directory $data_dir does not exist."
  for item in "$data_dir"/*; do
    if [ -f "$item" ]; then
      if [[ "$(basename "$item")" == "priv_validator_state.json" ]]; then
        log "Processing file: $item"
        jq 'del(.signature, .signbytes) | .height = "0" | .round = 0 | .step = 0' "$item" > "$data_dir/tmp.json" \
          && mv "$data_dir/tmp.json" "$item"
      fi
    elif [ -d "$item" ]; then
      log "Deleting directory: $item"
      rm -rf "$item"
    fi
  done
}

main() {
  log "execute the custom preupgrade script"
  require_cmd jq

  NODE_DIR="${NODE_DIR:-/$HOME/.imuad}"
  UPGRADE_GENESIS="$NODE_DIR/config/1.1.3_genesis.json"
  ORACLE_BEACON_CONFIG="$NODE_DIR/config/1.1.3_oracle_env_beaconchain.yaml"
  ORACLE_FEEDER_YAML="$NODE_DIR/config/1.1.3_oracle_feeder.yaml"
  ORACLE_BEACON_FILENAME="oracle_env_beaconchain.yaml"
  ORACLE_FEEDER_FILENAME="oracle_feeder.yaml"
  CURRENT_TIME=$(date +"%Y%m%d_%H%M%S")

  [ -d "$NODE_DIR" ] || error_exit "Source directory $NODE_DIR does not exist."

  backup_configs "$NODE_DIR" "$CURRENT_TIME"

  replace_file "$UPGRADE_GENESIS" "$NODE_DIR/config/genesis.json" "genesis.json with 1.1.3_genesis.json"
  replace_file "$ORACLE_BEACON_CONFIG" "$NODE_DIR/config/$ORACLE_BEACON_FILENAME" "$ORACLE_BEACON_FILENAME"
  replace_file "$ORACLE_FEEDER_YAML" "$NODE_DIR/config/$ORACLE_FEEDER_FILENAME" "$ORACLE_FEEDER_FILENAME"

  update_chain_id "$NODE_DIR/config/genesis.json" "$NODE_DIR/config/client.toml"

  clear_data_dir "$NODE_DIR/data"

  # todo: do some other changes to the config file for the upgrade, which is determined by the node manager.
  # todo: address the change for price feeder

  log "execute the custom preupgrade script successfully!"
}

main "$@"
