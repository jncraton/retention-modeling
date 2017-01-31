def predict_four(student):
  """ Predicts four year retention of a student 

  >>> predict_four({
  ...   'hs_grade':7,
  ...   'sat_verbal':600,
  ...   'sat_math':600,
  ...   'gender':1,
  ...   'white':2,
  ...   'native_american':1,
  ...   'black':1,
  ...   'mexican_american':1,
  ... })
  0.6618
  """

  return (
    -.2004 +\
    .0554 * float(student['hs_grade']) +\
    .000408 * float(student['sat_verbal']) +\
    .000546 * float(student['sat_math']) +\
    .0803 * float(student['gender']) +\
    .0378 * float(student['white']) +\
    -.1403 * float(student['native_american']) +\
    -.0570 * float(student['black']) +\
    -.0566 * float(student['mexican_american'])
  )

def predict_six(student):
  return (
    -.2605 +\
    .0545 * float(student['hs_grade']) +\
    .000340 * float(student['sat_verbal']) +\
    .000590 * float(student['sat_math']) +\
    .0725 * float(student['gender']) +\
    -.1047 * float(student['native_american']) +\
    .0237 * float(student['white'])
  )

def predict_six_academic(student):
  return (
    -.2030 +\
    .0604 * float(student['hs_grade']) +\
    .000382 * float(student['sat_verbal']) +\
    .000470 * float(student['sat_math'])
  )

def predict_retention(student):
  """ Uses predict_four and assumes that about half of attrition is in the 
  first year

  This is ugly fuzzy to convert 4 year grad rates to retention rates

  2.5 is best match for last 5 years without an offset

  2.81 was chosen based on best fit for last 5 years
  2.65 was chosen based on best fit for last 10 years
  2.55 was chosen based on best fit for all time

  Offset of .05 based on historic 4 year grad rates underperforming by ~5%
  """
  return 1. - ((1. - (predict_four(student) - 0.05)) / 2.81)