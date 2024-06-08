#!/bin/bash

# For setting a given boss on a given map to a given value, use jq:
# jq --arg map customs '.Bosses.gluhar[$map] = 42'
#
# or this adds 10 to any existing chance in the file:
# jq '.Bosses.gluhar |= map_values(if . == 0 then . else . + 10 end) | .Bosses.goons |= map_values(if . == 0 then . else . + 10 end)'

PROG=$(basename $0)
MOVE_CMD="/usr/bin/mv"
COPY_CMD="/usr/bin/cp"
COPY_OPTS="-v --remove-destination"
LINK_OPTS="-vsf"

HIGHER_CHANCE_DEFAULT=75
DECENT_CHANCE_DEFAULT=50

BACKUP_DIR="/mnt/c/SPT/Backups/SWAG/bossConfig"
SWAG_DIR="/mnt/c/SPT/SPTARKOV/user/mods/SWAG"
SWAG_CONFIG_DIR="${SWAG_DIR}/config"
BOSS_CONFIG_FILE="bossConfig.json"
SWAG_BOSS_CONFIG="${SWAG_CONFIG_DIR}/${BOSS_CONFIG_FILE}"
SWAG_BOSS_ORIG="${BACKUP_DIR}/${BOSS_CONFIG_FILE}.orig"

VALID_BOSSES=(
  "gluhar"
  "goons"
  "kaban"
  "killa"
  "kolontay"
  "reshala"
  "sanitar"
  "shturman"
  "tagilla"
  "zryachiy"
)

VALID_MAPS=(
  "customs"
  "factory"
  "factory_night"
  "groundzero"
  "interchange"
  "laboratory"
  "lighthouse"
  "reserve"
  "shoreline"
  "streets"
  "woods"
  "all"
)

show_usage() {
  local valid_maps_list=$(IFS=, ; echo "${VALID_MAPS[*]}" | sed 's/,/, /g')
  echo "Usage: $PROG {all_bosses map|set_boss_chance boss map chance|set_current_chance chance|show_chance boss_or_map|original}"
  echo "Valid maps: $valid_maps_list"
  echo ""
  echo "Examples: $PROG all_bosses customs (100% all bosses on given map)"
  echo "          $PROG set_boss_chance gluhar customs 50"
  echo "          $PROG set_boss_chance gluhar all 100 (gluhar will spawn on all maps)"
  echo "          $PROG set_current_chance 75 (change any existing percentage to 75)"
  echo "          $PROG show_chance gluhar"
  echo "          $PROG show_chance customs"
  echo "          $PROG original (restore original file)"
  exit 1
}

is_valid_map() {
  local map=$1
  for valid_map in "${VALID_MAPS[@]}"; do
    if [ "$map" == "$valid_map" ]; then
      return 0
    fi
  done
  return 1
}

list_bosses() {
  jq '.Bosses | keys' $SWAG_BOSS_CONFIG
}

# Verify that at least one positional argument was given
if [ "$#" -lt 1 ]; then
  show_usage
fi

mkdir -p $BACKUP_DIR
if [ ! -e $SWAG_BOSS_ORIG ]; then
  echo "There is no original of $SWAG_BOSS_CONFIG in $BACKUP_DIR"
  echo "Run 'cp $SWAG_BOSS_CONFIG $SWAG_BOSS_ORIG' NOW!"
  echo "This will ensure whatever this script does will not destroy the original config file."
  echo "(you could always restore from the SWAG+Donuts archive file though)"
  echo "If you have already created an original file, just modify SWAG_BOSS_ORIG in the script"
  echo "to point to it."
  exit 1
fi

choice=$1

validate_json() {
  local json_file=$1

  jq empty "$json_file" 2>/dev/null
  if [ $? -ne 0 ]; then
    echo "Invalid JSON format in $json_file"
    exit 1
  fi
}

backup_config() {
  mkdir -p $BACKUP_DIR
  backup_file="${BACKUP_DIR}/${BOSS_CONFIG_FILE}.$(date +%Y%m%d_%H%M%S)"
  $COPY_CMD $SWAG_BOSS_CONFIG $backup_file

  if [ $? -eq 0 ]; then
    echo "Backup created: $backup_file"
  else
    echo "Failed to create backup."
    exit 1
  fi

  # Keep only the 10 most recent backups
  # TODO: make this configurable?
  ls -1t "$BACKUP_DIR" | tail -n +11 | xargs -I {} rm -f "$BACKUP_DIR/{}"
}

set_all_bosses_map() {
  local map=$1

  if is_valid_map $map; then
    tmpfile="tmp.$$.json"
    jq --arg map $map '
    .Bosses |= with_entries(
    if .value | type == "object" then
      if has($map) then
        .value[$map] = 100
      else
        .
      end
    else
      .
    end
    )' $SWAG_BOSS_CONFIG > $tmpfile
    if [ $? -ne 0 ]; then
      echo "Error modifying $SWAG_BOSS_CONFIG config with jq"
      echo "Not removing tmpfile: $tmpfile"
      exit 1
    fi
  else
    echo "Invalid map: $map. Valid maps: ${VALID_MAPS[*]}"
    exit 1
  fi

  validate_json $tmpfile
  $MOVE_CMD $tmpfile $SWAG_BOSS_CONFIG
  if [ $? -eq 0 ]; then
    echo "Set $boss spawn chance on $map to $chance"
  else
    echo "Faile to set spawn chance for $boss on $map"
  fi
}

set_boss_chance() {
  local boss=$1
  local map=$2
  local chance=$3

  tmpfile="tmp.$$.json"
  if [ "$map" == "all" ]; then
    jq --arg boss $boss --argjson chance $chance '
    .Bosses[$boss] |= with_entries(
    if .value | type == "number" then
      .value = $chance
    else
      .
    end
    )' $SWAG_BOSS_CONFIG > $tmpfile
    if [ $? -ne 0 ]; then
      echo "Error modifying $SWAG_BOSS_CONFIG config with jq"
      echo "Not removing tmpfile: $tmpfile"
      exit 1
    fi
  else
    if is_valid_map $map; then
      jq --arg boss $boss --arg map $map --argjson chance $chance '
      if .Bosses[$boss] | has($map) then
        .Bosses[$boss][$map] = $chance
      else
        .
      end' $SWAG_BOSS_CONFIG > $tmpfile
      if [ $? -ne 0 ]; then
        echo "Error modifying $SWAG_BOSS_CONFIG config with jq"
        echo "Not removing tmpfile: $tmpfile"
        exit 1
      fi
    else
      echo "Invalid map: $map. Valid maps: ${VALID_MAPS[*]}"
      exit 1
    fi
  fi

  validate_json $tmpfile
  $MOVE_CMD $tmpfile $SWAG_BOSS_CONFIG
  if [ $? -eq 0 ]; then
    echo "Set $boss spawn chance on $map to $chance"
  else
    echo "Faile to set spawn chance for $boss on $map"
  fi
}

# Set any existing (non-zero) chances in the file to the number provided
set_current_chance() {
  local new_chance=$1

  tmpfile="tmp.$$.json"
  jq --argjson new_chance $new_chance '
  .Bosses |= with_entries(
      if .value | type == "object" then
          .value |= with_entries(
              if .value != 0 then
                  .value = $new_chance
              else
                  .
              end
          )
      else
          .
      end
  )' $SWAG_BOSS_CONFIG > $tmpfile
  if [ $? -ne 0 ]; then
    echo "Error modifying $SWAG_BOSS_CONFIG config with jq"
    echo "Not removing tmpfile: $tmpfile"
    exit 1
  fi

  validate_json $tmpfile
  $MOVE_CMD $tmpfile $SWAG_BOSS_CONFIG
  if [ $? -eq 0 ]; then
    echo "Set existing non-zero spawn chance to $new_chance"
  else
    echo "Failed to set existing non-zero spawn chance"
  fi
}

show_chance() {
  local boss_or_map=$1

  echo -n "$boss_or_map: "
  if [[ " ${VALID_BOSSES[*]} " == *" $boss_or_map "* ]]; then
    jq --arg boss "$boss_or_map" '.Bosses[$boss]' $SWAG_BOSS_CONFIG
  elif [[ " ${VALID_MAPS[*]} " == *" $boss_or_map "* ]]; then
    jq --arg map "$boss_or_map" '
    .Bosses | to_entries | map(select(.value | type == "object") | {(.key): .value[$map]}) | add' $SWAG_BOSS_CONFIG
  else
    echo "Invalid boss or map: $boss_or_map"
    echo "Valid bosses are: ${VALID_BOSSES[*]}"
    echo "Available maps are: ${VALID_MAPS[*]}"
    exit 1
  fi
}

# Validate the current bossConfig.json file before continuing...it could be
# corrupt already
validate_json $SWAG_BOSS_CONFIG

# Backup the current config file before doing anything. Note: this has nothing
# to do with the original, default config. That is a different thing and should
# be stored somewhere before ever running this script. And never changed. All
# this does is back up the current config, which could be all bosses on
# shoreline or whatever.
if [ "$1" != "show_chance" ]; then
  backup_config
fi

case $choice in
  original|default)
    $COPY_CMD $COPY_OPTS $SWAG_BOSS_ORIG $SWAG_BOSS_CONFIG
    if [ $? -ne 0 ]; then
      echo "Failed to copy $SWAG_BOSS_ORIG to $SWAG_BOSS_CONFIG"
    fi
    ;;
  all_bosses)
    if [ "$#" -ne 2 ]; then
      echo "Error: all_bosses requires a map argument"
      show_usage
    fi

    map=$2
    echo "Setting $map to 100% for all bosses"
    set_all_bosses_map $map
    ;;
  decent_chance)
    new_chance=${2:-$DECENT_CHANCE_DEFAULT}
    set_current_chance $new_chance
    ;;
  set_boss_chance)
    if [ "$#" -ne 4 ]; then
      echo "Error: set_boss_chance requires 3 arguments: boss map chance"
      show_usage
    fi

    boss=$2
    map=$3
    chance=$4
    set_boss_chance $boss $map $chance
    ;;
  set_current_chance)
    # Check if one argument is provided
    if [ "$#" -ne 2 ]; then
      echo "Error: set_current_chance requires one argument (new chance value)"
      show_usage
    fi

    new_chance=$2
    set_current_chance $new_chance
    ;;
  show_chance)
    if [ "$#" -ne 2 ]; then
      echo "Error: show_chance requires one argument (boss or map)"
      show_usage
    fi

    boss_or_map=$2
    show_chance $boss_or_map
    ;;
  *)
    echo "Invalid option: $choice"
    show_usage
    ;;
esac
