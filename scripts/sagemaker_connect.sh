#!/bin/bash

# Disable the -x option if printing each command is not needed.
set -exuo pipefail

SPACE_ARN="$1"
AWS_PROFILE="${2:-}"

# TODO Fix Declan's nice trick
# aws sts get-caller-identity

# EXIT_CODE="$?"
# if [ $EXIT_CODE != 0 ]; then
#     echo "No details returned on IAM user or role whose credentials are used to call the operation."
#     aws sso login # TODO tweak for functionality in IDE e.g. Code or Cursor
# fi

# Validate ARN and extract region
if [[ "$SPACE_ARN" =~ ^arn:aws[-a-z]*:sagemaker:([a-z0-9-]+):[0-9]{12}:space\/[^\/]+\/[^\/]+$ ]]; then
    AWS_REGION="${BASH_REMATCH[1]}"
else
    echo "Error: Invalid SageMaker Studio Space ARN format."
    exit 1
fi

# Optional profile flag
PROFILE_ARG=()
if [[ -n "$AWS_PROFILE" ]]; then
    PROFILE_ARG=(--profile "$AWS_PROFILE")
fi

# Start session
START_SESSION_JSON=$(aws sagemaker start-session \
    --resource-identifier "$SPACE_ARN" \
    --region "${AWS_REGION}" \
    "${PROFILE_ARG[@]}")

# Extract fields using grep and sed
SESSION_ID=$(echo "$START_SESSION_JSON" | grep -o '"SessionId": "[^"]*"' | sed 's/.*: "//;s/"$//')
STREAM_URL=$(echo "$START_SESSION_JSON" | grep -o '"StreamUrl": "[^"]*"' | sed 's/.*: "//;s/"$//')
TOKEN=$(echo "$START_SESSION_JSON" | grep -o '"TokenValue": "[^"]*"' | sed 's/.*: "//;s/"$//')

# Validate extracted values
if [[ -z "$SESSION_ID" || -z "$STREAM_URL" || -z "$TOKEN" ]]; then
    echo "Error: Failed to extract session information from sagemaker start session response."
    exit 1
fi

# Call session-manager-plugin
session-manager-plugin \
    "{\"streamUrl\":\"$STREAM_URL\",\"tokenValue\":\"$TOKEN\",\"sessionId\":\"$SESSION_ID\"}" \
    "$AWS_REGION" "StartSession"
