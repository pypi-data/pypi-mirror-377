"""
Aerodrome Swap MCP Server
"""

import logging
from typing import Optional, List, Dict, Any
import requests
from pydantic import BaseModel, Field

from fastmcp import FastMCP
import os

mcp = FastMCP("aerodrome-swap-mcp")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the Aerodrome Swap API base URL
AERODROME_API_BASE_URL = os.getenv("AERODROME_API_BASE_URL")

if not AERODROME_API_BASE_URL:
    raise ValueError("AERODROME_API_BASE_URL environment variable is not set")


class Token(BaseModel):
    """Model for token information"""

    address: str = Field(..., description="The token contract address")
    symbol: str = Field(..., description="The token symbol")
    name: Optional[str] = Field(default=None, description="The token name")
    decimals: int = Field(..., description="The number of decimals for the token")
    listed: Optional[bool] = Field(
        default=None, description="Whether the token is listed on Aerodrome"
    )


class Price(BaseModel):
    """Model for price information"""

    token: Token = Field(..., description="The token information")
    price: float = Field(..., description="The current price of the token in USD")
    price_display: float = Field(
        ..., description="The display price of the token in USD"
    )

    @staticmethod
    def from_dict(token_name, data: Dict[str, Any]) -> "Price":
        """Create a Price instance from a dictionary"""
        return Price(
            token=Token(**data.get("token", {}), name=token_name),
            price=data.get("price", 0.0),
            price_display=data.get("price_display", 0.0),
        )


class Pool(BaseModel):
    """Model for pool information"""

    lp: str = Field(..., description="The liquidity provider contract address")
    type: int = Field(..., description="The type of the pool")
    token0_address: str = Field(..., description="The first token in the pool")
    token1_address: str = Field(..., description="The second token in the pool")
    is_stable: bool = Field(..., description="Whether the pool is stable")
    is_cl: bool = Field(..., description="Whether the pool is concentrated liquidity")
    symbol: str = Field(..., description="The pool symbol")
    type_label: str = Field(..., description="The type label of the pool")


class PoolTypeInfo(BaseModel):
    """Model for pool type information"""

    type: int = Field(..., description="The type of the pool")
    is_stable: bool = Field(..., description="Whether the pool is stable")
    is_cl: bool = Field(..., description="Whether the pool is concentrated liquidity")
    label: str = Field(..., description="The type label of the pool")
    decimals: int = Field(..., description="The number of decimals for the pool")


class PoolLiquidityReserves(BaseModel):
    """Model for pool liquidity reserves"""

    token0_amount: float = Field(
        ..., description="The reserve amount of the first token"
    )
    token1_amount: float = Field(
        ..., description="The reserve amount of the second token"
    )


class PoolLiquidity(BaseModel):
    """Model for pool liquidity information"""

    tvl: float = Field(..., description="Total Value Locked in the pool")
    total_supply: float = Field(..., description="Total supply of the pool tokens")
    reserves: PoolLiquidityReserves = Field(
        ..., description="Reserves of the tokens in the pool"
    )


class PoolTradingVolumeBreakdown(BaseModel):
    """Model for pool trading volume breakdown"""

    token0_volume: float = Field(..., description="Trading volume of the first token")
    token1_volume: float = Field(..., description="Trading volume of the second token")


class PoolTradingFeesBreakdown(BaseModel):
    """Model for pool trading fees breakdown"""

    token0_fees: float = Field(..., description="Trading fees of the first token")
    token1_fees: float = Field(..., description="Trading fees of the second token")


class PoolTrading(BaseModel):
    """Model for pool trading information"""

    volume_24h: float = Field(..., description="Trading volume in the last 24 hours")
    fees_24h: float = Field(..., description="Fees generated in the last 24 hours")
    apr: float = Field(..., description="Annual Percentage Rate for the pool")
    pool_fee_bps: int = Field(..., description="Pool fee in basis points")
    pool_fee_percentage: float = Field(..., description="Pool fee as a percentage")
    volume_breakdown: PoolTradingVolumeBreakdown = Field(
        ..., description="Breakdown of trading volume by token"
    )
    fees_breakdown: PoolTradingFeesBreakdown = Field(
        ..., description="Breakdown of fees by token"
    )


class PoolGauge(BaseModel):
    """Model for pool gauge information"""

    total_supply: float = Field(..., description="Total supply of the gauge")
    emissions_per_second: float = Field(
        ..., description="Emissions per second for the gauge"
    )
    weekly_emissions: float = Field(..., description="Weekly emissions for the gauge")


class PoolContracts(BaseModel):
    """Model for pool contract addresses"""

    nfpm: str = Field(..., description="The NFPM contract address")
    alm: str = Field(..., description="The ALM contract address")


class PoolDetailed(BaseModel):
    """Model for detailed pool information"""

    symbol: str = Field(..., description="The pool symbol")
    factory: str = Field(..., description="The factory contract address")
    type_info: PoolTypeInfo = Field(..., description="The type information of the pool")
    tokens: List[Token] = Field(..., description="The tokens in the pool")
    liquidity: PoolLiquidity = Field(
        ..., description="The liquidity information of the pool"
    )
    trading: PoolTrading = Field(..., description="The trading information of the pool")
    gauge: PoolGauge = Field(..., description="The gauge information of the pool")
    contracts: PoolContracts = Field(
        ..., description="The contract addresses of the pool"
    )
    voting: Optional[Dict[str, Any]] = Field(
        None, description="The voting information of the pool"
    )

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PoolDetailed":
        """Create a PoolDetailed instance from a dictionary"""
        return PoolDetailed(
            symbol=data.get("symbol", ""),
            factory=data.get("factory", ""),
            type_info=PoolTypeInfo(**data.get("type_info", {})),
            tokens=[Token(**v, name=k) for k, v in data.get("tokens", {}).items()],
            liquidity=PoolLiquidity(**data.get("liquidity", {})),
            trading=PoolTrading(**data.get("trading", {})),
            gauge=PoolGauge(**data.get("gauge", {})),
            contracts=PoolContracts(**data.get("contracts", {})),
            voting=data.get("voting"),
        )


class QuoteInput(BaseModel):
    """Model for quote input information"""

    token: Token = Field(..., description="The input token information")
    amount: str = Field(..., description="The input amount")
    amount_wei: str = Field(..., description="The input amount in wei")
    price_usd: float = Field(..., description="The price of the input token in USD")
    value_usd: float = Field(..., description="The USD value of the input amount")


class QuoteOutput(BaseModel):
    """Model for quote output information"""

    token: Token = Field(..., description="The output token information")
    amount: float = Field(..., description="The output amount")
    amount_wei: str = Field(..., description="The output amount in wei")
    min_amount: float = Field(..., description="The minimum output amount")
    min_amount_wei: str = Field(..., description="The minimum output amount in wei")
    price_usd: float = Field(..., description="The price of the output token in USD")
    value_usd: float = Field(..., description="The USD value of the output amount")


class QuoteRoutePathItem(BaseModel):
    """Model for quote route path item"""

    pool_address: str = Field(..., description="The pool address")
    is_stable: bool = Field(..., description="Whether the pool is stable")
    is_cl: bool = Field(..., description="Whether the pool is concentrated liquidity")
    hop_number: int = Field(..., description="The hop number in the route")


class QuoteRoute(BaseModel):
    """Model for quote route information"""

    path: List[QuoteRoutePathItem] = Field(..., description="The route path")
    hops: int = Field(..., description="The number of hops in the route")
    type: str = Field(..., description="The type of the route")


class Quote(BaseModel):
    """Model for quote information"""

    input: QuoteInput = Field(..., description="The input information for the quote")
    output: QuoteOutput = Field(..., description="The output information for the quote")
    route: QuoteRoute = Field(..., description="The route information for the quote")
    execution_price: float = Field(..., description="The execution price for the quote")
    slippage: float = Field(..., description="The slippage for the quote")

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Quote":
        """Create a Quote instance from a dictionary"""
        return Quote(
            input=QuoteInput(**data.get("input", {})),
            output=QuoteOutput(**data.get("output", {})),
            route=QuoteRoute(
                path=[
                    QuoteRoutePathItem(**item)
                    for item in data.get("route", {}).get("path", [])
                ],
                hops=data.get("route", {}).get("hops", 0),
                type=data.get("route", {}).get("type", ""),
            ),
            execution_price=data.get("execution_price", 0.0),
            slippage=data.get("slippage", 0.0),
        )


class SwapTransactionDetailDebug(BaseModel):
    """Model for transaction debug information"""

    swapper_address: str = Field(..., description="The swapper contract address")
    is_native_input: bool = Field(..., description="Whether the input token is native")
    is_direct_swap: bool = Field(..., description="Whether the swap is direct")
    gas_price_gwei: float = Field(..., description="The gas price in gwei")
    commands: str = Field(..., description="The commands executed in the transaction")
    inputs_count: int = Field(
        ..., description="The number of inputs in the transaction"
    )
    function_selector: str = Field(
        ..., description="The function selector of the transaction"
    )


class SwapTransactionDetail(BaseModel):
    """Model for transaction information"""

    to: str = Field(..., description="The recipient address of the transaction")
    data: str = Field(..., description="The data payload of the transaction")
    value: str = Field(..., description="The value of the transaction in wei")
    gas: str = Field(..., description="The gas limit for the transaction")
    gasPrice: str = Field(..., description="The gas price for the transaction in wei")
    nonce: str = Field(..., description="The nonce of the transaction")
    chainId: str = Field(..., description="The chain ID of the transaction")
    from_address: str = Field(
        ..., alias="from", description="The sender address of the transaction"
    )
    debug: Optional[SwapTransactionDetailDebug] = Field(
        None, alias="_debug", description="Debug information for the transaction"
    )

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SwapTransactionDetail":
        """Create a SwapTransactionDetail instance from a dictionary"""
        debug = None
        if "_debug" in data:
            debug_data = data.get("_debug")
            del data["_debug"]
            debug = SwapTransactionDetailDebug(**debug_data) if debug_data else None
        return SwapTransactionDetail(**data, _debug=debug)


class SwapTransaction(BaseModel):
    """Model for swap transaction information"""

    type: str = Field(
        ..., description="The type of the transaction, e.g., approval, swap"
    )
    description: str = Field(..., description="A description of the transaction")
    transaction: SwapTransactionDetail = Field(
        ..., description="The transaction details"
    )

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SwapTransaction":
        """Create a Transaction instance from a dictionary"""
        return SwapTransaction(
            type=data.get("type", ""),
            description=data.get("description", ""),
            transaction=SwapTransactionDetail.from_dict(data.get("transaction", {})),
        )


class SwapSummary(BaseModel):
    """Model for swap summary information"""

    from_amount: str = Field(
        ..., alias="from", description="The input amount and token symbol"
    )
    to_amount: str = Field(
        ..., alias="to", description="The output amount and token symbol"
    )
    minimum_received: str = Field(..., description="The minimum amount to be received")
    slippage: str = Field(..., description="The slippage percentage")
    route_hops: int = Field(..., description="The number of hops in the route")


class Swap(BaseModel):
    """Model for swap information"""

    success: bool = Field(..., description="Whether the quote request was successful")
    wallet_address: str = Field(..., description="The wallet address for the swap")
    chain_id: int = Field(..., description="The chain ID for the swap")
    quote: Quote = Field(..., description="The quote information for the swap")
    transactions: List[SwapTransaction] = Field(
        ..., description="The list of transactions for the swap"
    )
    summary: SwapSummary = Field(..., description="A summary of the swap")

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Swap":
        """Create a Swap instance from a dictionary"""
        return Swap(
            success=data.get("success", False),
            wallet_address=data.get("wallet_address", ""),
            chain_id=data.get("chain_id", 0),
            quote=Quote.from_dict(data.get("quote", {})),
            transactions=[
                SwapTransaction.from_dict(tx) for tx in data.get("transactions", [])
            ],
            summary=SwapSummary(**data.get("summary", {})),
        )


class Transaction(BaseModel):
    """Model for transaction information"""

    found: bool = Field(..., description="Whether the transaction was found")
    status: str = Field(..., description="The status of the transaction")
    transaction_hash: str = Field(..., description="The hash of the transaction")
    block_number: int = Field(..., description="The block number of the transaction")
    confirmations: int = Field(
        ..., description="The number of confirmations for the transaction"
    )
    gas_used: int = Field(..., description="The gas used by the transaction")
    effective_gas_price: int = Field(
        ..., description="The effective gas price of the transaction in wei"
    )
    from_address: str = Field(
        ..., alias="from", description="The sender address of the transaction"
    )
    to: str = Field(..., description="The recipient address of the transaction")
    logs: int = Field(
        ..., description="The number of logs generated by the transaction"
    )
    explorer_url: str = Field(
        ..., description="The URL to view the transaction on a blockchain explorer"
    )


def _make_request(
    method: str,
    endpoint: str,
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Make a request to the Aerodrome API"""
    try:
        url = f"{AERODROME_API_BASE_URL}/{endpoint}"
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to {endpoint}: {e}")
        raise


@mcp.tool
def get_tokens(
    target: str = "aero", limit: int = 100, offset: int = 0, listed_only: bool = False
) -> List[Token]:
    """Get all tokens with optional filtering"""
    try:
        data = _make_request(
            "GET",
            "tokens",
            {
                "target": target,
                "limit": limit,
                "offset": offset,
                "listed_only": str(listed_only).lower(),
            },
        )
        tokens = [Token(**token_data) for token_data in data.get("tokens", [])]
        return tokens
    except Exception as e:
        logger.error(f"Error in get_tokens: {e}")
        raise


@mcp.tool
def get_token_by_address(address: str, target: str = "aero") -> Token:
    """Get detailed information about a specific token.

    Args:
        address (str): The token address.
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero". Defaults to "aero".

    Returns:
        Token: The token information.
    """
    try:
        data = _make_request("GET", f"tokens/{address}", {"target": target})
        return Token(**data.get("token", {}))
    except Exception as e:
        logger.error(f"Error in get_token_by_address: {e}")
        raise


@mcp.tool
def get_tokens_batch(addresses: List[str], target: str = "aero") -> List[Token]:
    """Get information for multiple tokens in a single request. Useful for efficiently fetching data for token lists.

    Args:
        addresses (List[str]): The list of token addresses to retrieve information for.
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero". Defaults to "aero".

    Returns:
        List[Token]: A list of token information.
    """
    try:
        params = {"target": target}
        if addresses:
            params["addresses"] = addresses
        data = _make_request("GET", "tokens/batch", params)
        tokens = [Token(**token_data) for token_data in data.get("tokens", [])]
        return tokens
    except Exception as e:
        logger.error(f"Error in get_tokens_batch: {e}")
        raise


@mcp.tool
def search_tokens(query: str, target: str = "aero", limit: int = 10) -> List[Token]:
    """Search for tokens by symbol or address. This is useful for token selection in UI components.

    Args:
        query (str): Search term (symbol or address).
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero". Defaults to "aero".
        limit (int, optional): Max results (1-50, default: 10)

    Returns:
        List[Token]: _description_
    """
    try:
        data = _make_request(
            "GET", "tokens/search", {"target": target, "query": query, "limit": limit}
        )
        tokens = [Token(**token_data) for token_data in data.get("tokens", [])]
        return tokens
    except Exception as e:
        logger.error(f"Error in search_tokens: {e}")
        raise


@mcp.tool
def get_prices(
    target: str = "aero",
    limit: int = 50,
    offset: int = 0,
    symbols: Optional[List[str]] = None,
) -> List[Price]:
    """Get current token prices. This endpoint is optimized for high-frequency price queries with intelligent caching.
    Using query string parameters, you can get by symbols (ex symbols=AERO,USDC) or get by addresses (ex addresses=0x123,0x456)

    Args:
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero". Defaults to "aero".
        limit (int, optional): limit (int, optional): Max pools to return (1-1000, default: 100). Only worked when "symbols" is empty. Defaults to 50.
        offset (int, optional): Skip pools for pagination (default: 0). Only worked when "symbols" is empty. Defaults to 0.
        symbols (Optional[List[str]], optional): The token symbols to filter prices by. When "symbols" is set, "limit" and "offset" are ignored. Exp, "AERO,USDC". Defaults to None.

    Returns:
        List[Price]: _description_
    """
    try:
        params = {"target": target, "limit": limit, "offset": offset}
        if symbols:
            params["symbols"] = ",".join(symbols)
        data = _make_request("GET", "prices", params)
        prices = [
            Price.from_dict(token_name, price_data)
            for token_name, price_data in data.get("prices", {}).items()
        ]
        return prices
    except Exception as e:
        logger.error(f"Error in get_token_prices: {e}")
        raise


@mcp.tool
def get_price_by_address(address: str, target: str = "aero") -> Price:
    """Get price for a specific token.

    Args:
        address (str): _description_
        target (str, optional): _description_. Defaults to "aero".

    Returns:
        Price: _description_
    """
    try:
        data = _make_request("GET", f"prices/{address}", {"target": target})
        return Price(**data)
    except Exception as e:
        logger.error(f"Error in get_token_price_by_address: {e}")
        raise


@mcp.tool
def get_pools(
    target: str = "aero", limit: int = 100, offset: int = 0, token: Optional[str] = None
) -> List[Pool]:
    """Get a list of Aerodrome pools

    Args:
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".
        limit (int, optional): Max pools to return (1-1000, default: 100). Defaults to 100.
        offset (int, optional): Skip pools for pagination (default: 0). Defaults to 0.
        token (Optional[str], optional): The token address to filter pools by. Defaults to None.

    Returns:
        List[Pool]: A list of Aerodrome pools
    """

    try:
        params = {"target": target, "limit": limit, "offset": offset}
        if token:
            params["token"] = token
        data = _make_request("GET", "pools", params)
        pools = [Pool(**pool_data) for pool_data in data]
        return pools
    except Exception as e:
        logger.error(f"Error in get_pools: {e}")
        raise


@mcp.tool
def get_pools_detailed(
    target: str = "aero",
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "tvl",
    symbol: Optional[str] = None,
    min_tvl: Optional[int] = None,
) -> List[PoolDetailed]:
    """Get detailed pool information with TVL, APR, volume, fees, and voting rewards

    Args:
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".
        limit (int, optional): Max pools to return (1-1000, default: 100). Defaults to 100.
        offset (int, optional): Skip pools for pagination (default: 0). Defaults to 0.
        sort_by (str, optional): The field to sort by, must be one of: tvl, apr, volume, fees. Defaults to "tvl".
        symbol (Optional[str], optional): The pool symbol. Defaults to None.
        min_tvl (Optional[int], optional): The minimum TVL to filter pools by. Defaults to None.

    Returns:
        List[PoolDetailed]: A list of detailed pool information.
    """
    try:
        params = {
            "target": target,
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
        }
        if symbol:
            params["symbol"] = symbol
        if min_tvl:
            params["min_tvl"] = str(min_tvl)
        data = _make_request("GET", "pools/detailed", params)
        pools = [PoolDetailed.from_dict(pool_data) for pool_data in data]
        return pools
    except Exception as e:
        logger.error(f"Error in get_pools_detailed: {e}")
        raise


@mcp.tool
def get_pool_by_address(
    address: str, token0: Optional[str] = None, target: str = "aero"
) -> Pool:
    """Get detailed information about a specific pool by address.

    Args:
        address (str): The address of the pool.
        token0 (Optional[str], optional): The token0 address to filter pools by. Defaults to None.
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".

    Returns:
        Pool: The pool information.
    """
    try:
        params = {"target": target}
        if token0:
            params["token0"] = token0
        data = _make_request("GET", f"pools/{address}", params)
        return Pool(**data.get("pool", {}))
    except Exception as e:
        logger.error(f"Error in get_pool_by_address: {e}")
        raise


@mcp.tool
def search_pools(
    token0: Optional[str] = None, token1: Optional[str] = None, target: str = "aero"
) -> List[Pool]:
    """Search for pools by token pair and other criteria. At least one token address is required.

    Args:
        token0 (Optional[str], optional): The token0 address to filter pools by. Defaults to None.
        token1 (Optional[str], optional): The token1 address to filter pools by. Defaults to None.
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".

    Returns:
        List[Pool]: List of pools matching the criteria.
    """
    try:
        if not token0 and not token1:
            raise ValueError("At least one token address is required")

        params = {"target": target}
        if token0:
            params["token0"] = token0
        if token1:
            params["token1"] = token1
        data = _make_request("GET", "pools/search", params)
        pools = [Pool(**pool_data) for pool_data in data.get("pools", [])]
        return pools
    except Exception as e:
        logger.error(f"Error in search_pools: {e}")
        raise


@mcp.tool
def get_quote(
    from_token: str, to_token: str, amount: int, target: str = "aero"
) -> Quote:
    """Get quotes for Aerodrome

    Args:
        from_token (str): Token to swap from (contract address)
        to_token (str): Token to swap to (contract address)
        amount (int): Amount to swap (in token units, not wei)
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".

    Returns:
        Quote: The quote information.
    """
    try:
        data = _make_request(
            "GET",
            "quote",
            {
                "target": target,
                "from_token": from_token,
                "to_token": to_token,
                "amount": amount,
            },
        )
        quote = Quote.from_dict(data)
        return quote
    except Exception as e:
        logger.error(f"Error in get_quote: {e}")
        raise


@mcp.tool
def build_swap(
    from_token: str,
    to_token: str,
    wallet_address: str,
    amount: str,
    target: str = "aero",
    slippage: float = 0.005,
) -> Swap:
    """Simulates transaction (customer needs to approve on their end)

    Args:
        from_token (str): Token to swap from (contract address)
        to_token (str): Token to swap to (contract address)
        amount (str): Amount to swap (in token units, not wei)
        wallet_address (str): Wallet address to execute swap.
        target (str, optional): The target blockchain, "base", "aero", "optimistic-ethereum", "velo". Defaults to "aero".
        slippage (float, optional): Slippage tolerance (0.001-0.5, default: 0.005)

    Returns:
        Swap: The swap information including transactions to be executed.
    """
    try:
        data = _make_request(
            "POST",
            "swap/build",
            {"target": target},
            {
                "from_token": from_token,
                "to_token": to_token,
                "amount": amount,
                "wallet_address": wallet_address,
                "slippage": slippage,
            },
        )
        return Swap.from_dict(data)
    except Exception as e:
        logger.error(f"Error in build_swap: {e}")
        raise


@mcp.tool
def get_transaction(tx_hash: str, target: str = "aero") -> Transaction:
    """Get transaction after swap.

    Args:
        tx_hash (str): Transaction hash.
        target (str, optional): The target blockchain. Defaults to "aero".

    Returns:
        Transaction: The transaction details.
    """
    try:
        data = _make_request("GET", f"transaction/{tx_hash}", {"target": target})
        return Transaction(**data)
    except Exception as e:
        logger.error(f"Error in get_transaction: {e}")
        raise


if __name__ == "__main__":
    mcp.run(transport="stdio")
