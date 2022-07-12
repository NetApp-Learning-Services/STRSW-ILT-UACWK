#!/bin/bash

#   Copyright 2021 NetApp, Inc
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

usage() {
  echo -e "\n"
  echo "Usage: $0 [ -a ASTRA_ACCOUNT_ID ] [ -t AUTHORIZATION_TOKEN ] [ -f ASTRA_FQDN ]" 1>&2
  echo "All options [-a, -t and -f] are required arguments"
  echo -e "\n"
}

exit_abnormal() {
  usage
  exit 1
}

while getopts ":a:t:f:h" options; do
  case "${options}" in
    a)
      ACCOUNT_ID=${OPTARG}
      ;;
    t)
      TOKEN=${OPTARG}
      ;;
    f)
      FQDN=${OPTARG}
      ;;
    h)
      exit_abnormal
      ;;
    :)
      echo "Error: -${OPTARG} requires an argument."
      exit_abnormal
      ;;
    *)
      exit_abnormal
      ;;
  esac
done

if [ -z "${ACCOUNT_ID}" ] || [ -z "${TOKEN}" ] || [ -z "${FQDN}" ]; then
  usage
  exit 1
fi

cat << EOF > config.yaml
headers:
  Authorization: Bearer ${TOKEN}
uid: ${ACCOUNT_ID}
astra_project: ${FQDN}
verifySSL: false
EOF

exit 0

