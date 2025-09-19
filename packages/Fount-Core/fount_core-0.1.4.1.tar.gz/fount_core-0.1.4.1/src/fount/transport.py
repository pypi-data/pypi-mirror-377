from typing import Optional
from io import BytesIO
import json
import sys
import httpx
import logging

logger = logging.getLogger(__name__)


class HTTPTransport:
    def __init__(
        self,
        base_url: httpx.URL | str,
        timeout: float,
        api_key: str,
        client: Optional[httpx.Client] = None,
    ):
        self.client = client or httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={"X-API-Key": f"{api_key}"} if api_key else {},
        )

    def upload_dataframe(self, dataframe):
        csv_params = {"index": False, "encoding": "utf-8", "compression": None}
        buffer = BytesIO()
        try:
            dataframe.to_csv(buffer, **csv_params)
            files = {"file": ("dataframe.csv", buffer.getvalue(), "text/csv")}
            try:
                job_id = None
                sys.stdout.write("==> Preparing for upload\n")
                with self.client.stream(
                    method="POST",
                    url="upload",
                    files=files,
                ) as _stream_response:
                    _stream_response.raise_for_status()
                    for chunk in _stream_response.iter_text():
                        try:
                            data = json.loads(chunk)
                        except json.JSONDecodeError:
                            continue
                        sys.stdout.write(f"\r{data.get('status')}")
                        sys.stdout.flush()
                        if "job_id" in data:
                            job_id = data.get("job_id")
                return job_id
            except httpx.TimeoutException:
                logger.error("Request Timed out")
            except httpx.HTTPStatusError as e:
                logger.error(e.response.text)
                logger.error(
                    f"\nError response {e.response.status_code} while requesting {e.request.url!r}"
                )
            except httpx.RequestError as e:
                logger.error(
                    f"\nAn error occurred while requesting {e.request.url!r}: {e}"
                )
        finally:
            buffer.close()

    def start_job(self, job_type, payload):
        _r = self.client.post(job_type, json=payload)
        if _r.is_success:
            return _r.json()
        elif _r.is_client_error:
            return {"error": "Client error"}
        elif _r.is_server_error:
            return {"error": "Server error"}

    def get_job_status(self, _p):
        req = self.client.get("status", params={"task_id": _p})
        return req.json()

    def get_job_metrics(self, _p):
        return self.client.get("metrics", params={"task_id": _p}).json()

    def get_artifacts(self, _p):
        return self.client.get("metrics", params={"task_id": _p}).json()

    # def stream_events(self,job_type,id):
    #     ...

    def close(self):
        return None
