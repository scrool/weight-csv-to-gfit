import csv
import datetime
import dateutil.tz
import dateutil.parser
from dateutil import zoneinfo

DAWN_TIME = datetime.datetime(1970, 1, 1, tzinfo=dateutil.tz.tzutc())
TIME_ZONE = zoneinfo.gettz('Europe/Berlin')

def nano(val):
  """Converts a number to nano (str)."""
  return '%d' % (int(val) * 1e9)

def epoch_of_time_str(dateTimeStr, tzinfo):
  log_time = dateutil.parser.parse(dateTimeStr).replace(tzinfo=tzinfo)
  return (log_time - DAWN_TIME).total_seconds()

def read_weights_csv(csv_filename):
    is_header = True
    weights = []
    unit_denominator = 1.0
    with open(csv_filename, 'rb') as csvfile:
        weights_reader = csv.reader(csvfile, delimiter=',')
        for row in weights_reader:
            if is_header:
                is_header=False
                if 'lb' in row[1]:
                    unit_denominator = 2.20462
                continue
            weights.append(dict(
                seconds_from_dawn=epoch_of_time_str(row[0], TIME_ZONE),
                weight=float(row[1])/unit_denominator
                ))
    return weights

def read_weights_csv_with_gfit_format(csv_filename):
    weights = read_weights_csv(csv_filename)
    gfit_weights = []
    for weight in weights:
        gfit_weights.append(dict(
            dataTypeName='com.google.weight',
            endTimeNanos=nano(weight["seconds_from_dawn"]),
            startTimeNanos=nano(weight["seconds_from_dawn"]),
            value=[dict(fpVal=weight["weight"])],
        ))
    return gfit_weights

if __name__=="__main__":
    gfit_weights = read_weights_csv_with_gfit_format('../weight.csv')
