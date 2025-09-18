from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List
import requests


DEFAULT_BASE_URL = "https://api.1151.to"


class UTXO:
    """Represents a single UTXO entry."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def txid(self) -> str:
        return str(self._data.get("txid", ""))

    @property
    def vout(self) -> int:
        return int(self._data.get("vout", 0))

    @property
    def address(self) -> str:
        return str(self._data.get("address", ""))

    @property
    def amount_btc(self) -> float:
        return float(self._data.get("amount_btc", 0.0))

    @property
    def confirmations(self) -> int:
        return int(self._data.get("confirmations", 0))

    @property
    def script(self) -> str:
        return str(self._data.get("script", ""))

    @property
    def raw_data(self) -> Dict[str, Any]:
        return self._data.copy()

    def __repr__(self) -> str:
        return (
            f"UTXO(txid='{self.txid}', vout={self.vout}, "
            f"amount_btc={self.amount_btc}, confirmations={self.confirmations})"
        )


class Transaction:
    """Represents a single transaction entry."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data.get("transaction", data)

    @property
    def id(self) -> str:
        return str(self._data.get("id", ""))

    @property
    def created_at(self) -> Optional[int]:
        return self._data.get("created_at")

    @property
    def associated_wallet(self) -> str:
        return str(self._data.get("associated_wallet", ""))

    @property
    def direction(self) -> str:
        return str(self._data.get("direction", ""))

    @property
    def amount(self) -> str:
        return str(self._data.get("amount", ""))

    @property
    def asset(self) -> str:
        return str(self._data.get("asset", ""))

    @property
    def destination(self) -> str:
        return str(self._data.get("destination", ""))

    @property
    def testnet(self) -> bool:
        return bool(self._data.get("testnet", False))

    @property
    def content(self) -> str:
        return str(self._data.get("content", ""))

    @property
    def success(self) -> bool:
        return bool(self._data.get("success", False))

    @property
    def raw_data(self) -> Dict[str, Any]:
        return self._data.copy()

    def __repr__(self) -> str:
        return (
            f"Transaction(id='{self.id}', asset='{self.asset}', "
            f"amount='{self.amount}', success={self.success})"
        )


class Wallet:
    """Represents a wallet object returned by the API."""

    def __init__(self, data: Dict[str, Any], client: Client) -> None:
        # The API nests wallet data inside {"wallet": {...}}
        self._data = data.get("wallet", data)
        self._client = client

    @property
    def id(self) -> str:
        return str(self._data.get("id", ""))

    @property
    def created_at(self) -> Optional[int]:
        return self._data.get("created_at")

    @property
    def wallet_name(self) -> str:
        return str(self._data.get("wallet_name", ""))

    @property
    def owned_by(self) -> str:
        return str(self._data.get("owned_by", ""))

    @property
    def address(self) -> str:
        return str(self._data.get("address", ""))

    @property
    def network(self) -> str:
        return str(self._data.get("network", ""))

    @property
    def testnet(self) -> bool:
        return bool(self._data.get("testnet", False))

    @property
    def last_used(self) -> Optional[int]:
        return self._data.get("last_used")

    @property
    def raw_data(self) -> Dict[str, Any]:
        return self._data.copy()

    def send(self, amount: float, destination: str, asset: str) -> Tuple[bool, str]:
        """Send funds from this wallet. Wrapper around Client.send_from_wallet."""
        return self._client.send_from_wallet(
            wallet_id=self.id,
            amount=amount,
            destination=destination,
            asset=asset,
        )

    def get_utxos(self) -> List[UTXO]:
        """Fetch UTXOs for this wallet. Wrapper around Client.get_utxos."""
        return self._client.get_utxos(wallet_id=self.id)

    def transactions(self) -> List[Transaction]:
        """Fetch transactions for this wallet."""
        return self._client.get_wallet_transactions(wallet_id=self.id)

    def __repr__(self) -> str:
        return (
            f"Wallet(id='{self.id}', wallet_name='{self.wallet_name}', "
            f"address='{self.address}', network='{self.network}', testnet={self.testnet})"
        )


class Client:
    """Client for interacting with api.1151.to"""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        *,
        timeout: float = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not isinstance(api_key, str) or not api_key:
            raise ValueError("api_key must be a non-empty string")
        self.api_key = api_key
        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout = timeout
        self.session = session or requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload["api_key"] = self.api_key
        resp = self.session.post(self._url(path), json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def create_wallet(self, name: str, network: str, testnet: bool) -> Wallet:
        data = self._post(
            "/wallet/create",
            {
                "wallet_name": name,
                "network": network,
                "testnet": testnet,
            },
        )
        return Wallet(data, self)

    def get_wallet(self, wallet_id: str) -> Wallet:
        try:
            data = self._post("/wallet/get", {"wallet_id": wallet_id})
            return Wallet(data, self)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                empty_data = {
                    "wallet": {
                        "id": None,
                        "created_at": None,
                        "wallet_name": None,
                        "owned_by": None,
                        "address": None,
                        "network": None,
                        "testnet": None,
                        "last_used": None,
                    }
                }
                return Wallet(empty_data, self)
        raise

    def delete_wallet(self, wallet_id: str) -> None:
        self._post("/wallet/delete", {"wallet_id": wallet_id})

    def send_from_wallet(
        self, wallet_id: str, amount: float, destination: str, asset: str
    ) -> Tuple[bool, str]:
        data = self._post(
            "/wallet/send",
            {
                "wallet_id": wallet_id,
                "amount": float(amount),
                "destination": destination,
                "asset": asset,
            },
        )
        success = data.get("result") == "ok"
        tx_id = str(data.get("tx_id", ""))
        return success, tx_id

    def get_utxos(self, wallet_id: str) -> List[UTXO]:
        """Get the list of UTXOs for a wallet."""
        data = self._post("/wallet/utxos", {"wallet_id": wallet_id})
        utxo_list = data.get("utxos", [])
        return [UTXO(utxo) for utxo in utxo_list]

    def get_transaction(self, tx_id: str) -> Transaction:
        data = self._post("/transaction/get", {"tx_id": tx_id})
        return Transaction(data)

    def get_wallet_transactions(self, wallet_id: str) -> List[Transaction]:
        data = self._post("/wallet/transactions", {"wallet_id": wallet_id})
        transactions = data.get("transactions", [])
        return [Transaction(tx) for tx in transactions]
