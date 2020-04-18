from upnpavcontrol.web.api import media_proxy
import pytest
import itsdangerous


def test_encode_decode():
    url = 'http://fancy.de'
    token = media_proxy.encode_url_proxy_token(url)
    decoded_url = media_proxy.decode_url_proxy_token(token)
    assert decoded_url == url
    assert token != url


def test_fake_decode():
    fake_token = 'rfegesrekborksbld.fv02314fwf'
    with pytest.raises(itsdangerous.exc.BadSignature):
        media_proxy.decode_url_proxy_token(fake_token)


def test_altered_token_decode():
    url = 'http://fancy.de'
    token = media_proxy.encode_url_proxy_token(url)
    altered_token = token[:1] + 'a' + token[2:]
    with pytest.raises(itsdangerous.exc.BadSignature):
        media_proxy.decode_url_proxy_token(altered_token)