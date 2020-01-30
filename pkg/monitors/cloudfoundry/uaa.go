package cloudfoundry

import "github.com/cloudfoundry-incubator/uaago"

func getUAAToken(uaaURL, username, password string, skipVerification bool) (string, error) {
	uaaClient, err := uaago.NewClient(uaaURL)
	if err != nil {
		return "", err
	}

	token, err := uaaClient.GetAuthToken(username, password, skipVerification)
	// TODO: handle refresh??
	return token, err
}
