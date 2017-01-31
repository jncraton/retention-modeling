import numpy as np
from sklearn import datasets, linear_model
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
import csv

retention_reg = None

prediction_vars = [
  'hs_gpa',
  'gender',
  'sat_math',
  'sat_verbal',
  'white',
  'black',
  'mexican_american',
  'native_american',
  'asian',
  'hispanic',
  'international',
  'zip_pci',
]

def init_retention():
  global retention_reg

  data = []
  
  for row in csv.DictReader(open('data/clean_data.tsv'), dialect='excel-tab'):
    if row['entry_term'] == 'FALL':
      data.append([
        row['people_code_id'].replace('P',''),
        row['entry_year'],
        row['retained'],
        ] + [row[var] for var in prediction_vars])
  
  data = np.array(data).astype(np.float)
  
  training = data[(data[:,1] >= 2011) & (data[:,1] < 2016)]
  
  # Split the data into training/testing sets
  training_X = training[:-20, 3:]
  training_X_test = training[-20:, 3:]
  
  # Split the targets into training/testing sets
  training_y = training[:-20, 2]
  training_y_test = training[-20:, 2]
  
  retention_reg = GradientBoostingRegressor(
    n_estimators=20,
    max_depth=4,
    learning_rate=.1,
    random_state=0
  )
  
  # Train the model using the training sets
  retention_reg.fit(training_X, training_y)
  
  # The coefficients
  #print('Coefficients: \n', regr.coef_)
  # The mean squared error
  print("Mean squared error: %.2f"
        % np.mean((retention_reg.predict(training_X_test) - training_y_test) ** 2))
  # Explained variance score: 1 is perfect prediction
  print('Variance score: %.2f' % retention_reg.score(training_X_test, training_y_test))

  print('Predicted overall retention: %.2f' % np.mean(retention_reg.predict(training_X)))

def predict_retention(student):
  return retention_reg.predict(np.array([student[var] for var in prediction_vars]).reshape(1,-1))

if __name__ == '__main__':
  init_retention()
  print(predict_retention({
    'hs_gpa': 3.7,
    'gender': 2,
    'sat_math': 600,
    'sat_verbal': 600,
    'white': 2,
    'black': 1,
    'mexican_american': 1,
    'native_american': 1,
    'asian': 1,
    'hispanic': 1,
    'international': 1,
    'zip_pci': 60,
  }))