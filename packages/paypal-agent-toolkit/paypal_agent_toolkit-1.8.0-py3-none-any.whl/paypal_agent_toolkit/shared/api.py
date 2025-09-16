

from typing import Optional
from pydantic import BaseModel
from .configuration import Context
from .paypal_client import PayPalClient
from .tools import tools

class PayPalAPI(BaseModel):
    
    _context: Context
    _paypal_client: PayPalClient
    
    def __init__(self, client_id: str, secret: str, context: Optional[Context]):
        super().__init__()

        self._context = context if context is not None else Context()
        self._paypal_client = PayPalClient(client_id=client_id, secret=secret, context=context)
        
    
    def run(self, method: str, params: dict) -> str:
        if method == "get_merchant_insights" and self._context.sandbox:
            raise ValueError("get_merchant_insights is not supported in sandbox mode")
        
        for tool in tools:
            if tool.get("method") == method:
                execute_fn = tool.get("execute")
                if execute_fn:
                    return execute_fn(self._paypal_client, params)
        raise ValueError(f"method: {method} not found in tools list")

