#!/bin/bash
# Yandex Direct MCP CLI Wrapper
# Использование: ./yandex-direct.sh <tool_name> '[json_args]'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_NAME="$1"
ARGS="${2:-{}}"

if [ -z "$TOOL_NAME" ]; then
  echo "Использование: $0 <tool_name> '[json_args]'"
  echo ""
  echo "Примеры:"
  echo "  $0 get_campaigns '{\"field_names\":[\"Id\",\"Name\"]}'"
  echo "  $0 get_account_balance '{}"  
  echo "  $0 wordstat_top_requests '{\"phrase\":\"купить ноутбук\"}'"
  exit 1
fi

# Формируем JSON-RPC запрос
REQUEST="{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"$TOOL_NAME\",\"arguments\":$ARGS}}"

# Вызываем MCP прокси
cd "$SCRIPT_DIR"
printf '%s\n' "$REQUEST" | timeout 15 node mcp-proxy.js 2>/dev/null
