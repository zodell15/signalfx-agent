package kubernetes

import (
	"errors"
	"os"
)

const (
	nodeEnvVar = "MY_NODE_NAME"
)

// NodeName returns the name of the node based on the MY_NODE_NAME envvar
func NodeName() (string, error) {
	if n := os.Getenv(nodeEnvVar); n != "" {
		return n, nil
	}
	return "", errors.New("Cannot determine node name, please set envvar " + nodeEnvVar)
}
