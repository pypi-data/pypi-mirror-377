# Aerodrome Swap MCP Server

This is a Model Context Protocol (MCP) server that provides integration with the Aerodrome Swap API. It allows users to interact with Aerodrome's decentralized exchange functionality through the MCP framework.

## Features

- Interact with Aerodrome Swap API
- Support for token swaps
- Pool information retrieval
- Price information retrieval
- Quote generation

## Prerequisites

- Python 3.8+
- Conda environment activated

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd aerodrome-swap-mcp

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Start the MCP server
npx aerodrome-swap-mcp
```

Or alternatively, you can install and run it locally:

```bash
# Install the package
pip install -e .

# Start the MCP server
aerodrome-swap-mcp
```

## API Reference

This MCP server provides the following tools for interacting with the Aerodrome Swap API:

### Token Operations

- **get_tokens** - Get all tokens with optional filtering
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".
  - `limit` (int, optional): Max tokens to return (1-1000, default: 100). Defaults to 100.
  - `offset` (int, optional): Skip tokens for pagination (default: 0). Defaults to 0.
  - `listed_only` (bool, optional): Only return listed tokens. Defaults to False.

- **get_token_by_address** - Get detailed information about a specific token.
  - `address` (str): The token address.
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".

- **get_tokens_batch** - Get information for multiple tokens in a single request. Useful for efficiently fetching data for token lists.
  - `addresses` (List[str]): The list of token addresses to retrieve information for.
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".

- **search_tokens** - Search for tokens by symbol or address. This is useful for token selection in UI components.
  - `query` (str): Search term (symbol or address).
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".
  - `limit` (int, optional): Max results (1-50, default: 10)

### Price Operations

- **get_prices** - Get current token prices. This endpoint is optimized for high-frequency price queries with intelligent caching.
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".
  - `limit` (int, optional): limit (int, optional): Max pools to return (1-1000, default: 100). Only worked when "symbols" is empty. Defaults to 50.
  - `offset` (int, optional): Skip pools for pagination (default: 0). Only worked when "symbols" is empty. Defaults to 0.
  - `symbols` (Optional[List[str]], optional): The token symbols to filter prices by. When "symbols" is set, "limit" and "offset" are ignored. Exp, "AERO,USDC". Defaults to None.

- **get_price_by_address** - Get price for a specific token.
  - `address` (str): The token address.
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".

### Pool Operations

- **get_pools** - Get a list of Aerodrome pools
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".
  - `limit` (int, optional): Max pools to return (1-1000, default: 100). Defaults to 100.
  - `offset` (int, optional): Skip pools for pagination (default: 0). Defaults to 0.
  - `token` (Optional[str], optional): The token address to filter pools by. Defaults to None.

- **get_pools_detailed** - Get detailed pool information with TVL, APR, volume, fees, and voting rewards
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".
  - `limit` (int, optional): Max pools to return (1-1000, default: 100). Defaults to 100.
  - `offset` (int, optional): Skip pools for pagination (default: 0). Defaults to 0.
  - `sort_by` (str, optional): The field to sort by, must be one of: tvl, apr, volume, fees. Defaults to "tvl".
  - `symbol` (Optional[str], optional): The pool symbol. Defaults to None.
  - `min_tvl` (Optional[int], optional): The minimum TVL to filter pools by. Defaults to None.

- **get_pool_by_address** - Get detailed information about a specific pool by address.
  - `address` (str): The address of the pool.
  - `token0` (Optional[str], optional): The token0 address to filter pools by. Defaults to None.
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".

- **search_pools** - Search for pools by token pair and other criteria. At least one token address is required.
  - `token0` (Optional[str], optional): The token0 address to filter pools by. Defaults to None.
  - `token1` (Optional[str], optional): The token1 address to filter pools by. Defaults to None.
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".

### Swap Operations

- **get_quote** - Get quotes for Aerodrome
  - `from_token` (str): Token to swap from (contract address)
  - `to_token` (str): Token to swap to (contract address)
  - `amount` (int): Amount to swap (in token units, not wei)
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".

- **build_swap** - Simulates transaction (customer needs to approve on their end)
  - `from_token` (str): Token to swap from (contract address)
  - `to_token` (str): Token to swap to (contract address)
  - `amount` (str): Amount to swap (in token units, not wei)
  - `wallet_address` (str): Wallet address to execute swap.
  - `target` (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".
  - `slippage` (float, optional): Slippage tolerance (0.001-0.5, default: 0.005)

- **get_transaction** - Get transaction after swap.
  - `tx_hash` (str): Transaction hash.
  - `target` (str, optional): The target blockchain. Defaults to "aero".

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
