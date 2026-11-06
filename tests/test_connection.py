import json,threading,urllib.request,urllib.error
import pytest
from tracescope.service import make_server

def test_web_runner_requires_token_and_explicit_origin():
    server=make_server(port=0,token='test-only-secret')
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}'
    try:
        request=urllib.request.Request(url+'/api/health',headers={'Origin':'https://ilcde.github.io'})
        with urllib.request.urlopen(request) as response:
            assert response.headers['Access-Control-Allow-Origin']=='https://ilcde.github.io'
            assert json.load(response)['ok']
        with pytest.raises(urllib.error.HTTPError) as error:urllib.request.urlopen(url+'/api/capabilities')
        assert error.value.code==401
        request=urllib.request.Request(url+'/api/capabilities',headers={'Authorization':'Bearer test-only-secret','Origin':'https://ilcde.github.io'})
        with urllib.request.urlopen(request) as response:assert json.load(response)['adapters']
        request=urllib.request.Request(url+'/api/runs',method='OPTIONS',headers={'Origin':'https://untrusted.invalid'})
        with pytest.raises(urllib.error.HTTPError) as error:urllib.request.urlopen(request)
        assert error.value.code==403
    finally:server.shutdown();server.server_close()
