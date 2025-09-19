# mintzy/client.py
import requests

class Client:
    # 📝 Define valid keys (for soft protection)
    VALID_KEYS = {"XYZ123", "ABC456", "CLIENT789"}

    def __init__(self, api_key, base_url="http://34.172.210.29/predict"):
        self.base_url = base_url
        self.api_key = api_key

    def _check_key(self):
        # Only allow if API key is in whitelist
        return self.api_key in self.VALID_KEYS

    def get_prediction(self, ticker, time_frame, parameters):
        if not self._check_key():
            return {"success": False, "error": "Unauthorized: Invalid API key"}

        if isinstance(parameters, str):
            parameters = [parameters]

        payload = {
            "action": {
                "action_type": "predict",
                "predict": {
                    "given": {"ticker": [ticker], "time_frame": time_frame},
                    "required": {"parameters": parameters}
                }
            }
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers={"X-API-Key": self.api_key},
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def batch_predict(self, tickers, time_frame, parameters=None):
        if not self._check_key():
            return [{"success": False, "error": "Unauthorized: Invalid API key", "ticker": t} for t in tickers]

        results = []
        for ticker in tickers:
            result = self.get_prediction(ticker, time_frame, parameters)
            result["ticker"] = ticker
            results.append(result)
        return results
