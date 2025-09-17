"""Main client class for the Finatic Server SDK."""

import asyncio
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta

from .api_client import ApiClient
from ..types import (
    DeviceInfo,
    SessionInitResponse,
    SessionResponse,
    OtpRequestResponse,
    OtpVerifyResponse,
    SessionAuthenticateResponse,
    PortalUrlResponse,
    UserToken,
    Holding,
    Order,
    Portfolio,
    BrokerInfo,
    BrokerAccount,
    BrokerOrder,
    BrokerPosition,
    BrokerBalance,
    BrokerConnection,
    BrokerDataOptions,
    OrdersFilter,
    PositionsFilter,
    AccountsFilter,
    BalancesFilter,
    OrderResponse,
    BrokerOrderParams,
    BrokerExtras,
    CryptoOrderOptions,
    OptionsOrderOptions,
    TradingContext,
    ApiPaginationInfo,
    PaginatedResult,
)
from ..utils.errors import (
    AuthenticationError,
    ValidationError,
    ApiError,
)


class FinaticServerClient:
    """Main client for interacting with the Finatic Server API.
    
    This client provides a high-level interface for authentication, portfolio management,
    and trading operations. It handles API key authentication and session management
    automatically.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.finatic.dev",
        device_info: Optional[DeviceInfo] = None,
        timeout: int = 30
    ):
        """Initialize the Finatic Server client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            device_info: Device information for requests
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url
        self.device_info = device_info
        self.timeout = timeout
        
        # Initialize API client
        self._api_client = ApiClient(base_url, device_info, timeout)
        
        # Session state
        self._session_id: Optional[str] = None
        self._company_id: Optional[str] = None
        self._user_token: Optional[UserToken] = None
        self._one_time_token: Optional[str] = None
        
        # Trading context
        self._trading_context: TradingContext = TradingContext()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._api_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        try:
            await self._api_client.__aexit__(exc_type, exc_val, exc_tb)
        except Exception as e:
            # Log cleanup errors but don't raise them
            print(f"Warning: Error during client cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup if context manager is not used."""
        try:
            if hasattr(self, '_api_client') and self._api_client:
                # Try to close the session if it's still open
                if hasattr(self._api_client, '_session') and self._api_client._session:
                    if not self._api_client._session.closed:
                        asyncio.create_task(self._api_client._session.close())
        except Exception:
            # Ignore cleanup errors in destructor
            pass
    
    async def _initialize_session(self) -> str:
        """Initialize a session by getting a one-time token.
        
        Returns:
            One-time token for session initialization
            
        Raises:
            AuthenticationError: If API key is invalid
            ApiError: For other API errors
        """
        if self._one_time_token:
            return self._one_time_token
        
        # Call the session init endpoint with API key
        response = await self._api_client._request(
            method='POST',
            path='/auth/session/init',
            additional_headers={'X-API-Key': self.api_key}
        )
        
        session_init = SessionInitResponse(**response)
        self._one_time_token = session_init.data['one_time_token']
        
        return self._one_time_token
    
    async def start_session(self, user_id: Optional[str] = None) -> SessionResponse:
        """Start a session with the one-time token.
        
        Args:
            user_id: Optional user ID for direct authentication
            
        Returns:
            Session response
            
        Raises:
            AuthenticationError: If token is invalid
            ApiError: For other API errors
        """
        # Get one-time token if not already available
        token = await self._initialize_session()
        
        # Start session
        response = await self._api_client._request(
            method='POST',
            path='/auth/session/start',
            data={'user_id': user_id} if user_id else {},
            additional_headers={'One-Time-Token': token}
        )
        
        session_response = SessionResponse(**response)
        
        # Handle both nested data structure and flat structure
        if session_response.data:
            # Nested structure (like frontend SDK expects)
            self._session_id = session_response.data.session_id
            self._company_id = session_response.data.company_id
        else:
            # Flat structure (what your API currently returns)
            self._session_id = session_response.session_id
            self._company_id = session_response.company_id
        
        # Set session context in API client (only if we have valid IDs)
        if self._session_id and self._company_id:
            self._api_client.set_session_context(
                self._session_id,
                self._company_id
            )
        
        return session_response

    async def set_user_id(self, user_id: str) -> None:
        """Set the user ID for the current session.
        
        Args:
            user_id: The user ID to set for the session
            
        Raises:
            AuthenticationError: If session is not initialized
        """
        if not self._session_id:
            raise AuthenticationError("Session not initialized. Please start a session first.")
        
        self._user_id = user_id
        # Update the API client with the new user ID if needed
        if hasattr(self._api_client, 'set_user_id'):
            await self._api_client.set_user_id(user_id)
    
    async def request_otp(self, email: str) -> OtpRequestResponse:
        """Request OTP for session authentication.
        
        Args:
            email: Email address to send OTP to
            
        Returns:
            OTP request response
            
        Raises:
            AuthenticationError: If session is not active
            ValidationError: If email is invalid
            ApiError: For other API errors
        """
        if not self._session_id:
            raise AuthenticationError("Session not initialized. Call start_session() first.")
        
        response = await self._api_client._request(
            method='POST',
            path='/auth/otp/request',
            data={'email': email}
        )
        
        return OtpRequestResponse(**response)
    
    async def verify_otp(self, otp: str) -> OtpVerifyResponse:
        """Verify OTP for session authentication.
        
        Args:
            otp: One-time password to verify
            
        Returns:
            OTP verification response with tokens
            
        Raises:
            AuthenticationError: If OTP is invalid or session is not active
            ApiError: For other API errors
        """
        if not self._session_id:
            raise AuthenticationError("Session not initialized. Call start_session() first.")
        
        response = await self._api_client._request(
            method='POST',
            path='/auth/otp/verify',
            data={'otp': otp}
        )
        
        otp_response = OtpVerifyResponse(**response)
        
        # Store tokens
        if otp_response.success and otp_response.data:
            self._user_token = UserToken(
                access_token=otp_response.data['access_token'],
                refresh_token=otp_response.data['refresh_token'],
                expires_in=otp_response.data['expires_in'],
                user_id=otp_response.data['user_id'],
                token_type=otp_response.data.get('token_type', 'Bearer'),
                scope=otp_response.data.get('scope', '')
            )
            
            # Set tokens in API client
            expires_at = (datetime.now() + timedelta(seconds=otp_response.data['expires_in'])).isoformat()
            self._api_client.set_tokens(
                otp_response.data['access_token'],
                otp_response.data['refresh_token'],
                expires_at,
                otp_response.data['user_id']
            )
        
        return otp_response
    
    async def authenticate_directly(self, user_id: str) -> SessionAuthenticateResponse:
        """Authenticate session directly with user ID.
        
        Args:
            user_id: User ID for direct authentication
            
        Returns:
            Authentication response with tokens
            
        Raises:
            AuthenticationError: If authentication fails
            ApiError: For other API errors
        """
        if not self._session_id:
            raise AuthenticationError("Session not initialized. Call start_session() first.")
        
        response = await self._api_client._request(
            method='POST',
            path='/auth/session/authenticate',
            data={'session_id': self._session_id, 'user_id': user_id}
        )
        
        auth_response = SessionAuthenticateResponse(**response)
        
        # Store tokens
        if auth_response.success and auth_response.data:
            self._user_token = UserToken(
                access_token=auth_response.data['access_token'],
                refresh_token=auth_response.data['refresh_token'],
                expires_in=3600,  # Default 1 hour
                user_id=user_id,
                token_type='Bearer',
                scope='api:access'
            )
            
            # Set tokens in API client
            expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
            self._api_client.set_tokens(
                auth_response.data['access_token'],
                auth_response.data['refresh_token'],
                expires_at,
                user_id
            )
        
        return auth_response
    
    async def get_portal_url(self, theme: Optional[Dict[str, Any]] = None, brokers: Optional[List[str]] = None, email: Optional[str] = None) -> str:
        """Get the portal URL for user authentication with optional theming and configuration.
        
        Args:
            theme: Optional theme configuration (preset or custom)
            brokers: Optional list of broker names to filter by
            email: Optional email to pre-fill in the portal
            
        Returns:
            Portal URL string with applied configuration
            
        Raises:
            AuthenticationError: If session is not initialized
        """
        if not self._session_id:
            raise AuthenticationError("Session not initialized. Call start_session() first.")
        
        try:
            response = await self._api_client.get_portal_url(self._session_id)
            portal_url = response.data['portal_url']
            
            # Use stored configuration as defaults if not provided
            final_theme = theme or getattr(self, '_portal_theme', None)
            final_brokers = brokers or getattr(self, '_portal_brokers', None)
            final_email = email or getattr(self, '_portal_email', None)
            
            # Apply theming and configuration to the URL
            portal_url = self._apply_portal_config(portal_url, final_theme, final_brokers, final_email)
            
            return portal_url
        except Exception as e:
            raise AuthenticationError(f"Failed to get portal URL: {str(e)}")
    
    def _apply_portal_config(self, base_url: str, theme: Optional[Dict[str, Any]] = None, brokers: Optional[List[str]] = None, email: Optional[str] = None) -> str:
        """Apply theming and configuration to a portal URL."""
        try:
            from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
            import base64
            import json
            
            parsed = urlparse(base_url)
            query_params = parse_qs(parsed.query)
            
            # Apply theme configuration
            if theme:
                if theme.get('preset'):
                    query_params['theme'] = [theme['preset']]
                elif theme.get('custom'):
                    # Encode custom theme as base64 JSON
                    theme_json = json.dumps(theme['custom'])
                    theme_b64 = base64.b64encode(theme_json.encode()).decode()
                    query_params['theme'] = ['custom']
                    query_params['themeObject'] = [theme_b64]
            
            # Apply broker filtering
            if brokers:
                # Convert broker names to IDs and encode
                supported_brokers = {
                    'alpaca': 'alpaca',
                    'robinhood': 'robinhood',
                    'tasty_trade': 'tasty_trade',
                    'ninja_trader': 'ninja_trader',
                    'tradovate': 'ninja_trader',  # Alias
                    'interactive_brokers': 'interactive_brokers',
                }
                
                broker_ids = []
                for broker in brokers:
                    broker_id = supported_brokers.get(broker.lower())
                    if broker_id:
                        broker_ids.append(broker_id)
                
                if broker_ids:
                    brokers_json = json.dumps(broker_ids)
                    brokers_b64 = base64.b64encode(brokers_json.encode()).decode()
                    query_params['brokers'] = [brokers_b64]
            
            # Apply email parameter
            if email:
                query_params['email'] = [email]
            
            # Rebuild URL with new query parameters
            new_query = urlencode(query_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            
            return urlunparse(new_parsed)
            
        except Exception as e:
            # If URL manipulation fails, return original URL
            print(f"Warning: Failed to apply portal configuration: {e}")
            return base_url

    async def get_session_user(self) -> Dict[str, Any]:
        """Get the user and tokens for a completed session.
        
        Returns:
            Dict containing user_id, access_token, refresh_token, and other user info
            
        Raises:
            AuthenticationError: If session is not initialized or not completed
        """
        if not self._session_id:
            raise AuthenticationError("Session not initialized. Call start_session() first.")
        
        if not self._company_id:
            raise AuthenticationError("Company ID not available. Session may not be properly initialized.")
        
        try:
            # Call the new endpoint with session ID as Bearer token and company ID header
            response = await self._api_client.get_session_user(self._session_id, self._company_id)
            
            # Store tokens internally for future API calls
            self._store_tokens(response)
            
            # Return user info using the getter methods
            return {
                "user_id": response.get_user_id(),
                "access_token": response.get_access_token(),
                "refresh_token": response.get_refresh_token(),
                "expires_in": response.get_expires_in(),
                "token_type": response.get_token_type(),
                "scope": response.get_scope(),
                "company_id": response.get_company_id()
            }
            
        except Exception as e:
            raise AuthenticationError(f"Failed to get session user: {str(e)}")

    def _store_tokens(self, user_response):
        """Store tokens internally for automatic use in API calls."""
        # Store in the API client for automatic token management
        expires_at = datetime.now() + timedelta(seconds=user_response.get_expires_in())
        self._api_client.set_tokens(
            user_response.get_access_token(),
            user_response.get_refresh_token(),
            expires_at.isoformat(),
            user_response.get_user_id()
        )
        
        # Also store in our local state
        self._user_token = UserToken(
            access_token=user_response.get_access_token(),
            refresh_token=user_response.get_refresh_token(),
            expires_in=user_response.get_expires_in(),
            user_id=user_response.get_user_id(),
            token_type=user_response.get_token_type(),
            scope=user_response.get_scope()
        )
    
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return (
            self._user_token is not None and
            self._user_token.access_token is not None and
            self._user_token.refresh_token is not None and
            self._user_token.user_id is not None
        )
    
    async def _ensure_authenticated(self):
        """Ensure the client is authenticated.
        
        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.is_authenticated():
            raise AuthenticationError("Client not authenticated. Complete authentication flow first.")
    
    # Portfolio methods
    async def get_holdings(self) -> List[Holding]:
        """Get portfolio holdings.
        
        Returns:
            List of holdings
            
        Raises:
            AuthenticationError: If not authenticated
            ApiError: For other API errors
        """
        await self._ensure_authenticated()
        access_token = await self._api_client.get_valid_access_token()
        
        response = await self._api_client._request(
            method='GET',
            path='/portfolio/holdings',
            access_token=access_token
        )
        
        return [Holding(**holding) for holding in response.get('data', [])]
    
    async def get_portfolio(self) -> Portfolio:
        """Get portfolio information.
        
        Returns:
            Portfolio information
            
        Raises:
            AuthenticationError: If not authenticated
            ApiError: For other API errors
        """
        await self._ensure_authenticated()
        access_token = await self._api_client.get_valid_access_token()
        
        response = await self._api_client._request(
            method='GET',
            path='/portfolio',
            access_token=access_token
        )
        
        return Portfolio(**response['data'])
    
    async def get_orders(self) -> List[Order]:
        """Get portfolio orders.
        
        Returns:
            List of orders
            
        Raises:
            AuthenticationError: If not authenticated
            ApiError: For other API errors
        """
        await self._ensure_authenticated()
        access_token = await self._api_client.get_valid_access_token()
        
        response = await self._api_client._request(
            method='GET',
            path='/portfolio/orders',
            access_token=access_token
        )
        
        return [Order(**order) for order in response.get('data', [])]
    
    # Trading context methods
    def set_broker(self, broker: str):
        """Set the current broker."""
        self._trading_context.broker = broker
        self._api_client.set_broker(broker)
    
    def set_account(self, account_number: str, account_id: Optional[str] = None):
        """Set the current account."""
        self._trading_context.account_number = account_number
        self._trading_context.account_id = account_id
        self._api_client.set_account(account_number, account_id)
    
    def get_trading_context(self) -> TradingContext:
        """Get the current trading context."""
        return self._trading_context
    
    def clear_trading_context(self):
        """Clear the trading context."""
        self._trading_context = TradingContext()
        self._api_client.clear_trading_context()
    
    # Utility methods
    def get_user_id(self) -> Optional[str]:
        """Get the current user ID."""
        return self._user_token.user_id if self._user_token else None
    
    def get_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self._session_id
    
    def get_company_id(self) -> Optional[str]:
        """Get the current company ID."""
        return self._company_id
    
    def is_authed(self) -> bool:
        """Return True if the client has a valid access and refresh token."""
        token_info = self._api_client.token_info
        if not token_info:
            return False
        access_token = token_info.get('access_token')
        refresh_token = token_info.get('refresh_token')
        expires_at = token_info.get('expires_at')
        if not access_token or not refresh_token:
            return False
        # Optionally, check if access token is expired
        if expires_at:
            from datetime import datetime
            try:
                expires_dt = datetime.fromisoformat(expires_at)
                if expires_dt < datetime.now():
                    return False
            except Exception:
                pass
        return True
    
    # Simple methods that automatically use stored tokens
    async def get_holdings(self) -> List[Holding]:
        """Get holdings using stored access token."""
        return await self._api_client.get_holdings_auto()
    
    async def get_orders(self) -> List[Order]:
        """Get orders using stored access token."""
        return await self._api_client.get_orders_auto()
    
    async def get_portfolio(self) -> Portfolio:
        """Get portfolio using stored access token."""
        return await self._api_client.get_portfolio_auto()
    
    async def get_broker_list(self) -> List[BrokerInfo]:
        """Get broker list using stored access token."""
        return await self._api_client.get_broker_list_auto()
    
    async def get_broker_accounts(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> PaginatedResult:
        """Get broker accounts with pagination support."""
        return await self._api_client.get_broker_accounts(page, per_page, options, filters)
    
    async def get_broker_orders(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> PaginatedResult:
        """Get broker orders with pagination support."""
        return await self._api_client.get_broker_orders(page, per_page, options, filters)
    
    async def get_broker_positions(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> PaginatedResult:
        """Get broker positions with pagination support."""
        return await self._api_client.get_broker_positions(page, per_page, options, filters)
    
    async def get_broker_balances(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[BalancesFilter] = None) -> PaginatedResult:
        """Get broker balances with pagination support."""
        return await self._api_client.get_broker_balances(page, per_page, options, filters)
    
    async def get_broker_connections(self) -> List[BrokerConnection]:
        """Get broker connections using stored access token."""
        return await self._api_client.get_broker_connections_auto()

    async def get_balances(self, options: Optional[BrokerDataOptions] = None) -> List[Dict[str, Any]]:
        """Get account balances for the authenticated user."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        return await self._api_client.get_balances(options)
    
    # Helper methods to get all data across pages
    async def get_all_broker_accounts(self, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> List[BrokerAccount]:
        """Get all broker accounts across all pages."""
        return await self._api_client.get_all_broker_accounts(options, filters)
    
    async def get_all_broker_orders(self, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> List[BrokerOrder]:
        """Get all broker orders across all pages."""
        return await self._api_client.get_all_broker_orders(options, filters)
    
    async def get_all_broker_positions(self, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> List[BrokerPosition]:
        """Get all broker positions across all pages."""
        return await self._api_client.get_all_broker_positions(options, filters)

    async def get_all_orders(self, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> List[BrokerOrder]:
        """Get all orders across all pages (convenience method)."""
        return await self._api_client.get_all_broker_orders(options, filters)

    async def get_all_positions(self, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> List[BrokerPosition]:
        """Get all positions across all pages (convenience method)."""
        return await self._api_client.get_all_broker_positions(options, filters)

    async def get_all_accounts(self, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> List[BrokerAccount]:
        """Get all accounts across all pages (convenience method)."""
        return await self._api_client.get_all_broker_accounts(options, filters)

    async def disconnect_company(self, connection_id: str) -> Dict[str, Any]:
        """Disconnect a company from a broker connection.
        
        Args:
            connection_id: The connection ID to disconnect
            
        Returns:
            Disconnect response data
            
        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        return await self._api_client.disconnect_company(connection_id)

    # Convenience filtering methods
    async def get_open_positions(self, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> List[BrokerPosition]:
        """Get only open positions."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        open_filters = {**(filters or {}), 'position_status': 'open'}
        result = await self.get_broker_positions(options=options, filters=open_filters)
        return result.data or []

    async def get_filled_orders(self, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> List[BrokerOrder]:
        """Get only filled orders."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        filled_filters = {**(filters or {}), 'status': 'filled'}
        result = await self.get_broker_orders(options=options, filters=filled_filters)
        return result.data or []

    async def get_pending_orders(self, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> List[BrokerOrder]:
        """Get only pending orders."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        pending_filters = {**(filters or {}), 'status': 'pending'}
        result = await self.get_broker_orders(options=options, filters=pending_filters)
        return result.data or []

    async def get_active_accounts(self, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> List[BrokerAccount]:
        """Get only active accounts."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        active_filters = {**(filters or {}), 'status': 'active'}
        return await self.get_broker_accounts(options=options, filters=active_filters)

    async def get_orders_by_symbol(self, symbol: str, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> List[BrokerOrder]:
        """Get orders filtered by symbol."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        symbol_filters = {**(filters or {}), 'symbol': symbol}
        result = await self.get_broker_orders(options=options, filters=symbol_filters)
        return result.data or []

    async def get_positions_by_symbol(self, symbol: str, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> List[BrokerPosition]:
        """Get positions filtered by symbol."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        symbol_filters = {**(filters or {}), 'symbol': symbol}
        result = await self.get_broker_positions(options=options, filters=symbol_filters)
        return result.data or []

    async def get_orders_by_broker(self, broker_id: str, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> List[BrokerOrder]:
        """Get orders filtered by broker."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        broker_filters = {**(filters or {}), 'broker_id': broker_id}
        result = await self.get_broker_orders(options=options, filters=broker_filters)
        return result.data or []

    async def get_positions_by_broker(self, broker_id: str, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> List[BrokerPosition]:
        """Get positions filtered by broker."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        broker_filters = {**(filters or {}), 'broker_id': broker_id}
        result = await self.get_broker_positions(options=options, filters=broker_filters)
        return result.data or []

    # Pagination helper methods
    async def get_orders_page(self, page: int, per_page: int, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> PaginatedResult:
        """Get a specific page of orders."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        return await self.get_broker_orders(page=page, per_page=per_page, options=options, filters=filters)

    async def get_positions_page(self, page: int, per_page: int, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> PaginatedResult:
        """Get a specific page of positions."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        return await self.get_broker_positions(page=page, per_page=per_page, options=options, filters=filters)

    async def get_accounts_page(self, page: int, per_page: int, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> List[BrokerAccount]:
        """Get a specific page of accounts."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        return await self.get_broker_accounts(page=page, per_page=per_page, options=options, filters=filters)

    async def get_next_orders_page(self, current_result: PaginatedResult) -> Optional[PaginatedResult]:
        """Get the next page of orders."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        if not current_result.has_next():
            return None
        
        # For now, return None as the API doesn't support cursor-based pagination
        # This would need to be implemented based on the actual API pagination structure
        return None

    async def get_next_positions_page(self, current_result: PaginatedResult) -> Optional[PaginatedResult]:
        """Get the next page of positions."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        if not current_result.has_next():
            return None
        
        # For now, return None as the API doesn't support cursor-based pagination
        # This would need to be implemented based on the actual API pagination structure
        return None

    async def get_next_accounts_page(self, current_page: int, per_page: int, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> Optional[List[BrokerAccount]]:
        """Get the next page of accounts."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please complete authentication first.")
        
        next_page = current_page + 1
        accounts = await self.get_broker_accounts(page=next_page, per_page=per_page, options=options, filters=filters)
        
        if not accounts:
            return None
        
        return accounts

    async def get_all_broker_balances(self, options: Optional[BrokerDataOptions] = None, filters: Optional[BalancesFilter] = None) -> List[BrokerBalance]:
        """Get all broker balances across all pages."""
        return await self._api_client.get_all_broker_balances(options, filters)

    # ============================================================================
    # TRADING METHODS
    # ============================================================================

    async def place_order(self, order: Dict[str, Any], extras: Optional[BrokerExtras] = None) -> OrderResponse:
        """Place a new order using the broker order API.
        
        Args:
            order: Order details with broker context
            extras: Optional broker-specific extras
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()

        
        # Convert order format to match broker API
        broker_order = BrokerOrderParams(
            broker=order.get('broker') or self._trading_context.broker or "robinhood",
            account_number=order.get('account_number') or self._trading_context.account_number or "",
            symbol=order['symbol'],
            order_qty=order['quantity'],
            action="Buy" if order['side'].lower() == 'buy' else "Sell",
            order_type=order['order_type'].title(),
            asset_type=order.get('asset_type', 'Stock'),
            time_in_force=order['time_in_force'],
            price=order.get('price'),
            stop_price=order.get('stop_price'),
            order_id=order.get('order_id'),
        )

        return await self._api_client.place_broker_order(
            broker_order, 
            extras or order.get('extras'), 
            order.get('connection_id')
        )

    async def cancel_order(
        self,
        order_id: str,
        broker: Optional[str] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Cancel a broker order.
        
        Args:
            order_id: The order ID to cancel
            broker: Optional broker override
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with cancellation details
        """
        await self._ensure_authenticated()
        return await self._api_client.cancel_broker_order(order_id, broker, {}, connection_id)

    async def modify_order(
        self,
        order_id: str,
        modifications: Dict[str, Any],
        broker: Optional[str] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Modify a broker order.
        
        Args:
            order_id: The order ID to modify
            modifications: The modifications to apply
            broker: Optional broker override
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with modification details
        """
        await self._ensure_authenticated()
        
        # Convert modifications to broker format
        broker_modifications = {}
        field_mapping = {
            'symbol': 'symbol',
            'quantity': 'order_qty',
            'price': 'price',
            'stop_price': 'stop_price',
            'time_in_force': 'time_in_force',
            'order_type': 'order_type',
            'side': 'action',
            'order_id': 'order_id',
            # Add additional mappings for common field names
            'order_qty': 'order_qty',
            'qty': 'order_qty',
            'size': 'order_qty',
        }
        
        for key, value in modifications.items():
            if key in field_mapping and value is not None:
                broker_modifications[field_mapping[key]] = value

        return await self._api_client.modify_broker_order(
            order_id, 
            broker_modifications, 
            broker, 
            {}, 
            connection_id
        )

    # ============================================================================
    # CONVENIENCE METHODS - STOCK
    # ============================================================================

    async def place_stock_market_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None
    ) -> OrderResponse:
        """Place a stock market order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            broker: Optional broker override
            account_number: Optional account number override
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()
        return await self._api_client.place_stock_market_order(
            symbol, quantity, side, broker, account_number
        )

    async def place_stock_limit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        price: float,
        time_in_force: str = "gtc",
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None
    ) -> OrderResponse:
        """Place a stock limit order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            price: Limit price
            time_in_force: 'day' or 'gtc'
            broker: Optional broker override
            account_number: Optional account number override
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()
        return await self._api_client.place_stock_limit_order(
            symbol, quantity, side, price, time_in_force, broker, account_number
        )

    async def place_stock_stop_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        stop_price: float,
        time_in_force: str = "day",
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None
    ) -> OrderResponse:
        """Place a stock stop order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            stop_price: Stop price
            time_in_force: 'day' or 'gtc'
            broker: Optional broker override
            account_number: Optional account number override
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()
        return await self._api_client.place_stock_stop_order(
            symbol, quantity, side, stop_price, time_in_force, broker, account_number
        )

    # ============================================================================
    # CONVENIENCE METHODS - CRYPTO
    # ============================================================================

    async def place_crypto_market_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        options: Optional[CryptoOrderOptions] = None,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None
    ) -> OrderResponse:
        """Place a crypto market order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            options: Optional crypto-specific options
            broker: Optional broker override
            account_number: Optional account number override
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()
        return await self._api_client.place_crypto_market_order(
            symbol, quantity, side, options, broker, account_number
        )

    async def place_crypto_limit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        price: float,
        time_in_force: str = "gtc",
        options: Optional[CryptoOrderOptions] = None,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None
    ) -> OrderResponse:
        """Place a crypto limit order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            price: Limit price
            time_in_force: 'day' or 'gtc'
            options: Optional crypto-specific options
            broker: Optional broker override
            account_number: Optional account number override
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()
        return await self._api_client.place_crypto_limit_order(
            symbol, quantity, side, price, time_in_force, options, broker, account_number
        )

    # ============================================================================
    # CONVENIENCE METHODS - OPTIONS
    # ============================================================================

    async def place_options_market_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        options: OptionsOrderOptions,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None
    ) -> OrderResponse:
        """Place an options market order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            options: Options-specific parameters
            broker: Optional broker override
            account_number: Optional account number override
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()
        return await self._api_client.place_options_market_order(
            symbol, quantity, side, options, broker, account_number
        )

    async def place_options_limit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        price: float,
        options: OptionsOrderOptions,
        time_in_force: str = "gtc",
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None
    ) -> OrderResponse:
        """Place an options limit order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            price: Limit price
            options: Options-specific parameters
            time_in_force: 'day' or 'gtc'
            broker: Optional broker override
            account_number: Optional account number override
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()
        return await self._api_client.place_options_limit_order(
            symbol, quantity, side, price, options, time_in_force, broker, account_number
        )

    # ============================================================================
    # CONVENIENCE METHODS - FUTURES
    # ============================================================================

    async def place_futures_market_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None
    ) -> OrderResponse:
        """Place a futures market order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            broker: Optional broker override
            account_number: Optional account number override
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()
        return await self._api_client.place_futures_market_order(
            symbol, quantity, side, broker, account_number
        )

    async def place_futures_limit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        price: float,
        time_in_force: str = "gtc",
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None
    ) -> OrderResponse:
        """Place a futures limit order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            price: Limit price
            time_in_force: 'day' or 'gtc'
            broker: Optional broker override
            account_number: Optional account number override
            
        Returns:
            OrderResponse with order details
        """
        await self._ensure_authenticated()
        return await self._api_client.place_futures_limit_order(
            symbol, quantity, side, price, time_in_force, broker, account_number
        )

    async def close(self):
        """Manually close the client and cleanup resources."""
        try:
            if hasattr(self, '_api_client') and self._api_client:
                await self._api_client.__aexit__(None, None, None)
        except Exception as e:
            print(f"Warning: Error during client close: {e}")
    
    # Portal configuration convenience methods
    def set_portal_theme(self, theme: Dict[str, Any]) -> None:
        """Set the default portal theme configuration.
        
        Args:
            theme: Theme configuration (preset or custom)
        """
        self._portal_theme = theme
    
    def set_portal_brokers(self, brokers: List[str]) -> None:
        """Set the default broker filter for the portal.
        
        Args:
            brokers: List of broker names to filter by
        """
        self._portal_brokers = brokers
    
    def set_portal_email(self, email: str) -> None:
        """Set the default email for the portal.
        
        Args:
            email: Email to pre-fill in the portal
        """
        self._portal_email = email
    
    def get_portal_config(self) -> Dict[str, Any]:
        """Get the current portal configuration.
        
        Returns:
            Dictionary with current portal configuration
        """
        return {
            'theme': getattr(self, '_portal_theme', None),
            'brokers': getattr(self, '_portal_brokers', None),
            'email': getattr(self, '_portal_email', None),
        }
    
    def clear_portal_config(self) -> None:
        """Clear all portal configuration settings."""
        self._portal_theme = None
        self._portal_brokers = None
        self._portal_email = None
    
    def __del__(self):
        """Destructor to ensure cleanup if context manager is not used."""
        try:
            if hasattr(self, '_api_client') and self._api_client:
                # Try to close the session if it's still open
                if hasattr(self._api_client, '_session') and self._api_client._session:
                    if not self._api_client._session.closed:
                        asyncio.create_task(self._api_client._session.close())
        except Exception:
            # Ignore cleanup errors in destructor
            pass 