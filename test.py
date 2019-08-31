from dateutil import parser
a = "2018-08-21T13:13:32"
b = "2019-08-21T13:13:32"
c = "2019-02-21T13:13:32"





ew = [parser.parse(a).strftime("%Y-%m-%d %H:%M:%S"),parser.parse(b).strftime("%Y-%m-%d %H:%M:%S"),parser.parse(c).strftime("%Y-%m-%d %H:%M:%S")]

print(sorted(ew, reverse=True))

