


# Print each line separately to make it easier to read in pytest output
def print_lines(msg):
    for l in msg.splitlines():
        print(l)


def print_datapoints(datapoints):
    for dp in datapoints:
        dims = []
        for d in dp.dimensions:
            dims.append("%s: %s" % (d.key, d.value))
        print("%s = %s {%s}" % (dp.metric, str(dp.value).strip(), ", ".join(dims)))
