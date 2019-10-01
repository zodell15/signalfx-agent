// +build !windows

package processlist

import (
	"strconv"
	"time"

	"github.com/shirou/gopsutil/process"
)

// ProcessList takes a snapshot of running processes
func ProcessList() ([]*TopProcess, error) {
	var procs []*TopProcess

	ps, err := process.Processes()
	if err != nil {
		return nil, err
	}

	for _, p := range ps {
		meminfo, err := p.MemoryInfoEx()
		if err != nil {
			continue
		}

		cpuTimes, err := p.Times()
		if err != nil {
			continue
		}

		username, _ := p.Username()
		// gopsutil confuses priority and nice
		priority, _ := p.Nice()
		nice := priority - 20
		if priority == 40 {
			nice = 0
		}
		status, _ := p.Status()
		memPercent, _ := p.MemoryPercent()
		cmdLine, _ := p.Cmdline()
		if cmdLine == "" {
			cmdLine, _ = p.Name()
		}
		createTime, _ := p.CreateTime()

		procs = append(procs, &TopProcess{
			ProcessID:           int(p.Pid),
			CreatedTime:         time.Unix(0, createTime*1000000),
			Username:            username,
			Priority:            int(priority),
			Nice:                strconv.Itoa(int(nice)),
			VirtualMemoryBytes:  meminfo.VMS,
			WorkingSetSizeBytes: meminfo.RSS,
			SharedMemBytes:      meminfo.Shared,
			Status:              status,
			MemPercent:          float64(memPercent),
			// gopsutil scales the times to seconds already
			TotalCPUTime: time.Duration((cpuTimes.User + cpuTimes.System) * float64(time.Second)),
			Command:      cmdLine,
		})
	}
	return procs, nil
}
