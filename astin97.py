def predict_four(student):
  """ Predicts four year retention of a student 

  >>> predict_four({
  ...   'hs_grade':7,
  ...   'sat_verbal':600,
  ...   'sat_math':600,
  ...   'gender':1,
  ...   'white':2,
  ...   'native_american':1,
  ...   'african_american':1,
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
    -.0570 * float(student['african_american']) +\
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

  2.5 was chosen based on comparison of HC means for the last 5 years
  2.2 was chosen based on comparison of HC means for all time
  """
  return 1.0 - ((1.0 - predict_four(student)) / 2.5)