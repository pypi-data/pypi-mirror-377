import pytest
import httpx
from deflect import Deflect, DeflectError, DeflectOptions, AsyncDeflect

class MockTransport(httpx.BaseTransport):
    def __init__(self, responses):
        self._responses = responses
        self.calls = 0

    def handle_request(self, request):  # type: ignore
        idx = min(self.calls, len(self._responses) - 1)
        self.calls += 1
        fn = self._responses[idx]
        return fn(request)


def json_response(data, status=200):
    return httpx.Response(status, json=data)


def test_success():
    transport = MockTransport([
        lambda req: json_response({"success": True, "verdict": {"can_pass": True}})
    ])
    client = Deflect(DeflectOptions(api_key="k", action_id="a", client=httpx.Client(transport=transport)))
    data = client.get_verdict("tok")
    assert data["success"] is True
    assert data["verdict"]["can_pass"] is True
    assert transport.calls == 1


def test_retry_network():
    class NetErrTransport(MockTransport):
        def handle_request(self, request):  # type: ignore
            current_call = self.calls
            self.calls += 1  # Increment call counter like base class does
            if current_call == 0:  # First call
                raise httpx.NetworkError("boom")
            return json_response({"success": True, "verdict": {"can_pass": False}})

    transport = NetErrTransport([
        lambda req: json_response({"success": True, "verdict": {"can_pass": False}})
    ])
    client = Deflect(DeflectOptions(api_key="k", action_id="a", client=httpx.Client(transport=transport)))
    data = client.get_verdict("tok")
    assert data["verdict"]["can_pass"] is False
    assert transport.calls == 2


def test_retry_5xx():
    transport = MockTransport([
        lambda req: httpx.Response(502, json={"error": True}),
        lambda req: json_response({"success": True, "verdict": {"can_pass": True}})
    ])
    client = Deflect(DeflectOptions(api_key="k", action_id="a", client=httpx.Client(transport=transport)))
    data = client.get_verdict("tok")
    assert data["verdict"]["can_pass"] is True
    assert transport.calls == 2


def test_no_retry_400():
    transport = MockTransport([
        lambda req: httpx.Response(400, json={"error": "bad"})
    ])
    client = Deflect(DeflectOptions(api_key="k", action_id="a", client=httpx.Client(transport=transport)))
    with pytest.raises(DeflectError):
        client.get_verdict("tok")
    assert transport.calls == 1


@pytest.mark.asyncio
async def test_async_success():
    class AsyncMockTransport(httpx.AsyncBaseTransport):
        def __init__(self, responses):
            self._responses = responses
            self.calls = 0
        async def handle_async_request(self, request):  # type: ignore
            idx = min(self.calls, len(self._responses) - 1)
            self.calls += 1
            fn = self._responses[idx]
            return fn(request)

    transport = AsyncMockTransport([
        lambda req: json_response({"success": True, "verdict": {"can_pass": True}})
    ])
    async_client = httpx.AsyncClient(transport=transport)
    client = AsyncDeflect(DeflectOptions(api_key="k", action_id="a", async_client=async_client))
    data = await client.get_verdict("tok")
    assert data["verdict"]["can_pass"] is True
    assert transport.calls == 1
