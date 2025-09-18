# tls_adapter.py
from typing import Optional, Sequence, Union, Tuple
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager, ProxyManager

# If SSLManager is in the same package:
from .sslManager import SSLManager  # <-- adjust if needed


def _normalize_ciphers(ciphers: Optional[Union[str, Sequence[str]]]) -> Optional[str]:
    if ciphers is None:
        return None
    if isinstance(ciphers, str):
        # collapse whitespace, dedupe accidental commas
        parts = [p.strip() for p in ciphers.split(",") if p.strip()]
        return ",".join(parts) if parts else ""
    # it's a sequence
    return ",".join(s.strip() for s in ciphers if s and s.strip())


class TLSAdapter(HTTPAdapter):
    """
    Requests adapter that injects a preconfigured SSLContext (from SSLManager)
    into both the main pool and any HTTPS proxy pools.
    """
    def __init__(
        self,
        ssl_manager: Optional[SSLManager] = None,
        ciphers: Optional[Union[str, Sequence[str]]] = None,
        certification: Optional[int] = None,   # e.g., ssl.CERT_REQUIRED
        ssl_options: Optional[int] = None
    ) -> None:
        ciphers_str = _normalize_ciphers(ciphers)

        self.ssl_manager = ssl_manager or SSLManager(
            ciphers=ciphers_str,
            ssl_options=ssl_options,
            certification=certification,
        )
        # Expose normalized/canonical values for singleton comparisons
        self.ciphers: Optional[str] = getattr(self.ssl_manager, "ciphers", ciphers_str)
        self.certification: int = getattr(self.ssl_manager, "certification", ssl.CERT_REQUIRED)
        self.ssl_options: Optional[int] = getattr(self.ssl_manager, "ssl_options", None)
        self.ssl_context: ssl.SSLContext = self.ssl_manager.ssl_context

        super().__init__()

    # Use canonical signature for clarity across urllib3 versions
    def init_poolmanager(self, connections: int, maxsize: int, block: bool = False, **pool_kwargs) -> None:
        pool_kwargs["ssl_context"] = self.ssl_context
        super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)

    def proxy_manager_for(self, proxy: str, **proxy_kwargs) -> ProxyManager:
        # only attach context for HTTPS proxies
        if proxy and str(proxy).lower().startswith("https://"):
            proxy_kwargs["ssl_context"] = self.ssl_context
        return super().proxy_manager_for(proxy, **proxy_kwargs)


class TLSAdapterSingleton:
    _instance: Optional[TLSAdapter] = None
    _config: Optional[Tuple[Optional[str], Optional[int], Optional[int]]] = None
    
    @staticmethod
    def get_instance(
        ciphers: Optional[Union[str, Sequence[str]]] = None,
        certification: Optional[int] = None,
        ssl_options: Optional[int] = None
    ) -> TLSAdapter:
        ciphers_str = _normalize_ciphers(ciphers)
        config = (ciphers_str, certification, ssl_options)

        if TLSAdapterSingleton._instance is None or TLSAdapterSingleton._config != config:
            TLSAdapterSingleton._instance = TLSAdapter(
                ciphers=ciphers_str,
                certification=certification,
                ssl_options=ssl_options,
            )
            TLSAdapterSingleton._config = config

        return TLSAdapterSingleton._instance
