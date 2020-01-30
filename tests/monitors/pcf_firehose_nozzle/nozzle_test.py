import asyncio
import json
from base64 import b64encode
from contextlib import contextmanager
from functools import partial as p

from sanic import Sanic, response
from signalfx.generated_protocol_buffers import signal_fx_protocol_buffers_pb2 as sf_pbuf
from tests.helpers.agent import Agent
from tests.helpers.assertions import has_datapoint, has_time_series
from tests.helpers.util import run_simple_sanic_app, wait_for


@contextmanager
def run_fake_uaa():
    app = Sanic()

    @app.post("/oauth/token")
    async def get_token(req):  # pylint:disable=unused-variable
        auth_value = req.headers.get("Authorization")
        expected_auth = b"Basic " + b64encode(b"myusername:mypassword")
        if expected_auth == auth_value.encode("utf-8"):
            json_data = {
                "access_token": "good-token",
                "token_type": "bearer",
                "expires_in": 1_000_000,
                "scope": "",
                "jti": "28edda5c-4e37-4a63-9ba3-b32f48530a51",
            }
            return response.json(json_data)
        return response.text("Unauthorized", status=401)

    with run_simple_sanic_app(app) as url:
        yield url


@contextmanager
def run_fake_rlp_gateway(envelopes):
    app = Sanic()

    @app.route("/v2/read", stream=True)
    async def stream_envelopes(req):  # pylint:disable=unused-variable
        auth_value = req.headers.get("Authorization")
        expected_auth = b"bearer good-token"
        if expected_auth != auth_value.encode("utf-8"):
            return response.text("Unauthorized (bad token)", status=401)

        async def streaming(resp):
            while True:
                for e in envelopes:
                    data = b"data: " + json.dumps(e).encode("utf-8") + b"\n\n"
                    print(data)
                    await resp.write(data)
                await asyncio.sleep(10)

        return response.stream(streaming)

    with run_simple_sanic_app(app) as url:
        yield url


def test_pcf_nozzle():
    firehose_envelopes = [
        {
            "batch": [
                {
                    "timestamp": "1580228407476075606",
                    "source_id": "uaa",
                    "instance_id": "",
                    "deprecated_tags": {},
                    "tags": {
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "origin": "uaa",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                    "gauge": {"metrics": {"vitals.jvm.cpu.load": {"unit": "gauge", "value": 0}}},
                }
            ]
        },
        {
            "batch": [
                {
                    "timestamp": "1580228407476126130",
                    "source_id": "uaa",
                    "instance_id": "",
                    "deprecated_tags": {},
                    "tags": {
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "origin": "uaa",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                    "gauge": {"metrics": {"vitals.jvm.thread.count": {"unit": "gauge", "value": 47}}},
                }
            ]
        },
        {
            "batch": [
                {
                    "timestamp": "1580228407476264719",
                    "source_id": "uaa",
                    "instance_id": "",
                    "deprecated_tags": {},
                    "tags": {
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "origin": "uaa",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                    "gauge": {"metrics": {"vitals.jvm.non-heap.init": {"unit": "gauge", "value": 7_667_712}}},
                }
            ]
        },
        {
            "batch": [
                {
                    "timestamp": "1580428783743352757",
                    "source_id": "doppler",
                    "instance_id": "",
                    "deprecated_tags": {},
                    "tags": {
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "direction": "egress",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "metric_version": "2.0",
                        "origin": "loggregator.doppler",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                    "counter": {"name": "dropped", "delta": "0", "total": "149000"},
                }
            ]
        },
        {
            "batch": [
                {
                    "timestamp": "1580428783743496839",
                    "source_id": "doppler",
                    "instance_id": "",
                    "deprecated_tags": {},
                    "tags": {
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "direction": "ingress",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "metric_version": "2.0",
                        "origin": "loggregator.doppler",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                    "counter": {"name": "dropped", "delta": "0", "total": "0"},
                },
                {
                    "timestamp": "1580428783744624100",
                    "source_id": "doppler",
                    "instance_id": "",
                    "deprecated_tags": {},
                    "tags": {
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "metric_version": "2.0",
                        "origin": "loggregator.doppler",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                    "counter": {"name": "egress", "delta": "0", "total": "1075978016"},
                },
                {
                    "timestamp": "1580428783744924877",
                    "source_id": "doppler",
                    "instance_id": "",
                    "deprecated_tags": {},
                    "tags": {
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "metric_version": "2.0",
                        "origin": "loggregator.doppler",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                    "counter": {"name": "egress", "delta": "7457", "total": "1075985473"},
                },
                {
                    "timestamp": "1580428783833603896",
                    "source_id": "system_metrics_agent",
                    "instance_id": "",
                    "deprecated_tags": {},
                    "tags": {
                        "deployment": "service-instance_a474d20d-9a64-4bac-993d-e0f644604083",
                        "index": "2cc60900-9c39-4ec3-80bb-2c1d22c10130",
                        "ip": "10.0.8.28",
                        "job": "mongodb-config-agent",
                        "origin": "system_metrics_agent",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                    "gauge": {"metrics": {"system_cpu_sys": {"unit": "Percent", "value": 0.315_324_026_576_374_3}}},
                },
                {
                    "timestamp": "1580428783833625031",
                    "source_id": "system_metrics_agent",
                    "instance_id": "",
                    "deprecated_tags": {},
                    "tags": {
                        "deployment": "service-instance_a474d20d-9a64-4bac-993d-e0f644604083",
                        "index": "2cc60900-9c39-4ec3-80bb-2c1d22c10130",
                        "ip": "10.0.8.28",
                        "job": "mongodb-config-agent",
                        "origin": "system_metrics_agent",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                    "gauge": {
                        "metrics": {
                            "system_disk_ephemeral_inode_percent": {"unit": "Percent", "value": 0.103_100_393_700_787_4}
                        }
                    },
                },
            ]
        },
    ]
    with run_fake_rlp_gateway(firehose_envelopes) as gateway_url, run_fake_uaa() as uaa_url:
        with Agent.run(
            f"""
        disableHostDimensions: true
        monitors:
         - type: pcf-firehose-nozzle
           uaaUrl: {uaa_url}
           rlpGatewayUrl: {gateway_url}
           uaaUser: myusername
           uaaPassword: mypassword
                """
        ) as agent:
            expected_time_series = [
                [
                    "vitals.jvm.non-heap.init",
                    {
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "origin": "uaa",
                        "product": "Small Footprint Pivotal Application Service",
                        "source_id": "uaa",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                ],
                [
                    "vitals.jvm.cpu.load",
                    {
                        "source_id": "uaa",
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "origin": "uaa",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                ],
                [
                    "vitals.jvm.thread.count",
                    {
                        "source_id": "uaa",
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "origin": "uaa",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                ],
                [
                    "dropped",
                    {
                        "source_id": "doppler",
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "direction": "egress",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "metric_version": "2.0",
                        "origin": "loggregator.doppler",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                ],
                [
                    "dropped",
                    {
                        "source_id": "doppler",
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "direction": "ingress",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "metric_version": "2.0",
                        "origin": "loggregator.doppler",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                ],
                [
                    "egress",
                    {
                        "source_id": "doppler",
                        "deployment": "cf-389cbac3d7a2c6c990c8",
                        "index": "ba5499ed-129c-48f2-877c-e270e5bd2648",
                        "ip": "10.0.4.7",
                        "job": "control",
                        "metric_version": "2.0",
                        "origin": "loggregator.doppler",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                ],
                [
                    "system_cpu_sys",
                    {
                        "source_id": "system_metrics_agent",
                        "deployment": "service-instance_a474d20d-9a64-4bac-993d-e0f644604083",
                        "index": "2cc60900-9c39-4ec3-80bb-2c1d22c10130",
                        "ip": "10.0.8.28",
                        "job": "mongodb-config-agent",
                        "origin": "system_metrics_agent",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                ],
                [
                    "system_disk_ephemeral_inode_percent",
                    {
                        "source_id": "system_metrics_agent",
                        "deployment": "service-instance_a474d20d-9a64-4bac-993d-e0f644604083",
                        "index": "2cc60900-9c39-4ec3-80bb-2c1d22c10130",
                        "ip": "10.0.8.28",
                        "job": "mongodb-config-agent",
                        "origin": "system_metrics_agent",
                        "product": "Small Footprint Pivotal Application Service",
                        "system_domain": "sys.industry.cf-app.com",
                    },
                ],
            ]

            for metric_name, dimensions in expected_time_series:
                assert wait_for(p(has_time_series, agent.fake_services, metric_name=metric_name, dimensions=dimensions))

            assert has_datapoint(agent.fake_services, metric_type=sf_pbuf.GAUGE, metric_name="vitals.jvm.cpu.load")
            assert has_datapoint(agent.fake_services, metric_type=sf_pbuf.CUMULATIVE_COUNTER, metric_name="dropped")
