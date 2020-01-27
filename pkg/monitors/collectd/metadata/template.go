// +build linux

package metadata

// AUTOGENERATED BY scripts/collectd-template-to-go.  DO NOT EDIT!!

import (
	"text/template"

	"github.com/signalfx/signalfx-agent/pkg/monitors/collectd"
)

// CollectdTemplate is a template for a metadata collectd config file
var CollectdTemplate = template.Must(collectd.InjectTemplateFuncs(template.New("metadata")).Parse(`
LoadPlugin "python"
TypesDB "{{ pythonPluginRoot }}/signalfx/types.db.plugin"
<Plugin python>
  ModulePath "{{ pythonPluginRoot }}/signalfx/src"
  LogTraces true
  Interactive false

  Import "signalfx_metadata"
  <Module signalfx_metadata>
  {{with .IntervalSeconds -}}
    Interval {{.}}
  {{- end}}
    Notifications true
    URL "{{.WriteServerURL}}?monitorID={{.MonitorID}}"
    Token {{if .Token}}"{{.Token}}"{{else}}"unnecessary"{{end}}
    NotifyLevel "OKAY"
    ProcPath "{{ .ProcFSPath }}"
    EtcPath "{{ .EtcPath }}"
    HostMetadata false
    PerCoreCPUUtil {{ .PerCoreCPUUtil }}
    Datapoints false
    PersistencePath "{{ .PersistencePath }}"
    ProcessInfo {{if .OmitProcessInfo}}false{{else}}true{{end}}
    {{with .DogStatsDIP -}}
    IP "{{.}}"
    {{- end}}
    {{with .DogStatsDPort -}}
    DogStatsDPort {{.}}
    {{- end}}
    {{with .IngestEndpoint -}}
    IngestEndpoint "{{.}}"
    {{- end}}
    {{with .Verbose -}}
    Verbose {{.}}
    {{- end}}
  </Module>
</Plugin>


<Chain "PostCache"> 
  <Rule "set_metadata_monitor_id"> 
    <Match "regex"> 
      Plugin "^signalfx-metadata$" 
    </Match> 
    <Target "set"> 
      MetaData "monitorID" "{{.MonitorID}}" 
    </Target> 
  </Rule> 
</Chain>
`)).Option("missingkey=error")