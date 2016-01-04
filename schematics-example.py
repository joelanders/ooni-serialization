import datetime
import yaml
from schematics.models import Model
from schematics.types import BaseType, BooleanType, FloatType
from schematics.types.compound import ListType, DictType, ModelType
from schematics.types.temporal import TimeStampType as HalfTimeStampType

# we want unix timestamp both ways
class TimeStampType(HalfTimeStampType):
    def to_native(self, value, context=None):
        return TimeStampType.timestamp_to_date(value)

# the StringType from schematics tries and fails to do some utf-8
# decoding, with no way to ignore, escape, or whatever we want.
class StringType(BaseType):
    pass

class HttpRequestsHeader(Model):
    backend_version = StringType()
    input_hashes = ListType(StringType)
    options = ListType(StringType)
    probe_asn = StringType()
    probe_cc = StringType()
    probe_city = StringType()
    probe_ip = StringType()
    report_id = StringType()
    software_name = StringType()
    software_version = StringType()
    start_time = TimeStampType()
    test_helpers = DictType(StringType)
    test_name = StringType()
    test_version = StringType()

# backend_version: 1.1.4
# input_hashes: [f29d079f9c0be6d7ea7fdb9570926f79e40f1a12becb7592e89ec03ee8901bf6]
# options: [-f, citizenlab-urls-global.txt]
# probe_asn: AS7922
# probe_cc: US
# probe_city: null
# probe_ip: 127.0.0.1
# report_id: 3SSsiXiSGLBthOHDe8NkNoCD3vKrrVoitLhihcFOyCzXAmicJHWkPSqMZ9OFkcJU
# software_name: ooniprobe
# software_version: 1.3.1
# start_time: 1441193001.0
# test_helpers: {}
# test_name: http_requests
# test_version: 0.2.4

# we read something like [['a', ['b']], ['c', ['d']]] into
# {'a': ['b'], 'c': ['d']}
# XXX polish this off with proper error-raising
class HttpHeadersType(BaseType):
    def to_native(self, raw):
        headers = {}
        for name, vals in raw:
            if name in headers:
                headers[name].extend(vals)
            else:
                headers[name] = vals
        return headers

# only exists nested under HttpRequestResponse
class HttpRequest(Model):
    body = StringType()
    headers = HttpHeadersType()
    method = StringType()
    tor = DictType(StringType)
    url = StringType()

# only exists nested under HttpRequestResponse
class HttpResponse(Model):
    body = StringType()
    code = StringType()
    headers = HttpHeadersType()

# only exists nested under HttpRequestsEntry
class HttpRequestResponse(Model):
    failure = StringType()
    request = ModelType(HttpRequest)
    response = ModelType(HttpResponse)

class HttpRequestsEntry(Model):
    agent = StringType()
    body_length_match = BooleanType()
    body_proportion = FloatType()
    control_failure = StringType()
    experiment_failure = StringType()
    factor = FloatType()
    headers_diff = ListType(StringType) # actually a set
    headers_match = BooleanType()
    input_url = StringType() # 'input' is a reserved word, need to tell lib about it. also, is it missing from spec?
    requests = ListType(ModelType(HttpRequestResponse))
    socksproxy = StringType()
    test_runtime = FloatType()
    test_start_time = TimeStampType()

# agent: agent
# body_length_match: null
# body_proportion: null
# control_failure: socks_host_unreachable
# experiment_failure: dns_lookup_error
# factor: 0.8
# headers_diff: null
# headers_match: null
# input: http://freehomepage.com
# requests:
# - failure: dns_lookup_error
#   request:
#     body: null
#     headers:
#     - - User-Agent
#       - ['Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2) Gecko/20100115 Firefox/3.6']
#     method: GET
#     tor: {is_tor: false}
#     url: http://freehomepage.com
# socksproxy: null
# test_runtime: 0.2677900791168213
# test_start_time: 1441193047.0

with open('samps/2015-09-02/20150902T112321Z-AS7922-http_requests-v1-probe.yaml', 'r') as f:
    yaml_gen = yaml.load_all(f.read())

header_yaml = yaml_gen.next()
header = HttpRequestsHeader(header_yaml)
#header.validate()
print header

for entry_yaml in yaml_gen:
    entry = HttpRequestsEntry(entry_yaml, deserialize_mapping={'input_url':'input'})
    #entry.validate()
    print entry

