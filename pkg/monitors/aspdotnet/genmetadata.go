// Code generated by monitor-code-gen. DO NOT EDIT.

package aspdotnet

import (
	"github.com/signalfx/golib/v3/datapoint"
	"github.com/signalfx/signalfx-agent/pkg/monitors"
)

const monitorType = "aspdotnet"

var groupSet = map[string]bool{}

const (
	aspNetApplicationRestarts                           = "asp_net.application_restarts"
	aspNetApplicationsRunning                           = "asp_net.applications_running"
	aspNetRequestsCurrent                               = "asp_net.requests_current"
	aspNetRequestsQueue                                 = "asp_net.requests_queue"
	aspNetRequestsRejected                              = "asp_net.requests_rejected"
	aspNetWorkerProcessRestarts                         = "asp_net.worker_process_restarts"
	aspNetWorkerProcessesRunning                        = "asp_net.worker_processes_running"
	aspNetApplicationsErrorsDuringExecution             = "asp_net_applications.errors_during_execution"
	aspNetApplicationsErrorsTotalSec                    = "asp_net_applications.errors_total_sec"
	aspNetApplicationsErrorsUnhandledDuringExecutionSec = "asp_net_applications.errors_unhandled_during_execution_sec"
	aspNetApplicationsPipelineInstanceCount             = "asp_net_applications.pipeline_instance_count"
	aspNetApplicationsRequestsFailed                    = "asp_net_applications.requests_failed"
	aspNetApplicationsRequestsSec                       = "asp_net_applications.requests_sec"
	aspNetApplicationsSessionSQLServerConnectionsTotal  = "asp_net_applications.session_sql_server_connections_total"
	aspNetApplicationsSessionsActive                    = "asp_net_applications.sessions_active"
)

var metricSet = map[string]monitors.MetricInfo{
	aspNetApplicationRestarts:                           {Type: datapoint.Gauge},
	aspNetApplicationsRunning:                           {Type: datapoint.Gauge},
	aspNetRequestsCurrent:                               {Type: datapoint.Gauge},
	aspNetRequestsQueue:                                 {Type: datapoint.Gauge},
	aspNetRequestsRejected:                              {Type: datapoint.Gauge},
	aspNetWorkerProcessRestarts:                         {Type: datapoint.Gauge},
	aspNetWorkerProcessesRunning:                        {Type: datapoint.Gauge},
	aspNetApplicationsErrorsDuringExecution:             {Type: datapoint.Gauge},
	aspNetApplicationsErrorsTotalSec:                    {Type: datapoint.Gauge},
	aspNetApplicationsErrorsUnhandledDuringExecutionSec: {Type: datapoint.Gauge},
	aspNetApplicationsPipelineInstanceCount:             {Type: datapoint.Gauge},
	aspNetApplicationsRequestsFailed:                    {Type: datapoint.Gauge},
	aspNetApplicationsRequestsSec:                       {Type: datapoint.Gauge},
	aspNetApplicationsSessionSQLServerConnectionsTotal:  {Type: datapoint.Gauge},
	aspNetApplicationsSessionsActive:                    {Type: datapoint.Gauge},
}

var defaultMetrics = map[string]bool{}

var groupMetricsMap = map[string][]string{}

var monitorMetadata = monitors.Metadata{
	MonitorType:       "aspdotnet",
	DefaultMetrics:    defaultMetrics,
	Metrics:           metricSet,
	MetricsExhaustive: false,
	Groups:            groupSet,
	GroupMetricsMap:   groupMetricsMap,
	SendAll:           true,
}
