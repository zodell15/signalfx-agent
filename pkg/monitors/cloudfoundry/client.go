package cloudfoundry

import (
	"context"
	"crypto/tls"
	"errors"
	"log"
	"net"
	"net/http"
	"strings"
	"time"

	"code.cloudfoundry.org/go-loggregator/rpc/loggregator_v2"
	"github.com/cloudfoundry/go-loggregator"
	"github.com/signalfx/golib/v3/datapoint"
	"github.com/signalfx/signalfx-agent/pkg/core/common/dpmeta"
	"github.com/signalfx/signalfx-agent/pkg/utils"
	"github.com/sirupsen/logrus"
)

const defaultShardID = "signalfx-nozzle"

type SignalFxGatewayClient struct {
	gatewayClient *loggregator.RLPGatewayClient

	ShardID string
}

func NewSignalFxGatewayClient(gatewayAddr string, uaaToken string, skipVerify bool, logger logrus.FieldLogger) *SignalFxGatewayClient {
	transport := http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: skipVerify},
		DialContext: (&net.Dialer{
			Timeout: 10 * time.Second,
		}).DialContext,
	}
	gatewayClient := loggregator.NewRLPGatewayClient(gatewayAddr,
		loggregator.WithRLPGatewayClientLogger(utils.NewStdLogWithLogrus(logger)),
		loggregator.WithRLPGatewayHTTPClient(&tokenAttacher{
			token: uaaToken,
			client: &http.Client{
				Transport: &transport,
			},
		}))

	return &SignalFxGatewayClient{
		gatewayClient: gatewayClient,
		ShardID:       defaultShardID,
	}
}

func (c *SignalFxGatewayClient) Run(ctx context.Context, sender func(...*datapoint.Datapoint)) error {
	if strings.TrimSpace(c.ShardID) == "" {
		return errors.New("shardId cannot be empty")
	}

	streamer := c.gatewayClient.Stream(ctx, &loggregator_v2.EgressBatchRequest{
		ShardId: c.ShardID,
		Selectors: []*loggregator_v2.Selector{
			{
				Message: &loggregator_v2.Selector_Counter{
					Counter: &loggregator_v2.CounterSelector{},
				},
			},
			{
				Message: &loggregator_v2.Selector_Gauge{
					Gauge: &loggregator_v2.GaugeSelector{},
				},
			},
		},
	})

	return c.processEnvelopes(ctx, streamer, sender)
}

func (c *SignalFxGatewayClient) processEnvelopes(ctx context.Context, streamer loggregator.EnvelopeStream, sender func(...*datapoint.Datapoint)) error {
	for {
		if ctx.Err() != nil {
			return ctx.Err()
		}

		var dps []*datapoint.Datapoint
		for _, env := range streamer() {
			if env == nil {
				return errors.New("log streamer shut down")
			}

			envDPs, err := envelopeToDatapoints(env)
			if err != nil {
				log.Printf("Error converting envelope to SignalFx datapoint: %v", err)
				continue
			}

			dps = append(dps, envDPs...)
		}

		for i := range dps {
			utils.SetDatapointMeta(dps[i], dpmeta.NotHostSpecificMeta, true)
		}

		// sender should return immediately
		sender(dps...)
	}
}

// Used to set the Authorization header on requests
type tokenAttacher struct {
	token  string
	client *http.Client
}

func (a *tokenAttacher) Do(req *http.Request) (*http.Response, error) {
	req.Header.Set("Authorization", a.token)
	return a.client.Do(req)
}
