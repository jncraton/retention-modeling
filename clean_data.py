import csv
import numpy as np

def convert_gpa_to_grade(hs_gpa):
    if hs_gpa > 3.7: return 8
    elif hs_gpa > 3.3: return 7
    elif hs_gpa > 3.0: return 6
    elif hs_gpa > 2.7: return 5
    elif hs_gpa > 2.3: return 4
    elif hs_gpa > 2.0: return 3
    elif hs_gpa > 1.7: return 2
    else: return 1

zip_pci_map = {}

for row in csv.DictReader(open('zip-pci.tsv', 'r'), dialect='excel-tab'):
  zip_pci_map[row['zip']] = row['pci']

pci = int(np.mean([int(r['pci']) for r in csv.DictReader(open('zip-pci.tsv', 'r'), dialect='excel-tab')]))

with open('data/data.csv','r') as fin:
  reader = csv.DictReader(fin)
  data = list(reader)

  print("Converting keys to lowercase...")
  for row in data:
      for k in row.keys():
        row[k.lower()] = row.pop(k)

  print("Removed rows without IDs")
  data = [r for r in data if r['people_code_id']]

  print("Calculating means for imputation...")
  years = set([r['entry_year'] for r in data])
  years = sorted(list(years))

  valid_gpa_data = [s for s in data if s['hs_gpa'] and float(s['hs_gpa']) > 0 and float(s['hs_gpa']) < 5]
  valid_sat_data = [s for s in data if s['sat_verbal'] and float(s['sat_verbal']) > 0]

  hs_gpa_mean = "%.2f" % (sum(float(r['hs_gpa']) for r in valid_gpa_data) / len(valid_gpa_data))
  sat_verb_mean = int(round(sum(float(r['sat_verbal']) for r in valid_sat_data) / len(valid_sat_data)))
  sat_math_mean = int(round(sum(float(r['sat_math']) for r in valid_sat_data) / len(valid_sat_data)))

  hs_gpa_means = {}
  for year in years:
    this_year = [s for s in valid_gpa_data if s['entry_year'] == str(year)]
    if len(this_year) > 0:
      hs_gpa_means[year] = "%.2f" % (sum(float(r['hs_gpa']) for r in this_year) / len(this_year))
    else:
      hs_gpa_means[year] = hs_gpa_mean
    print(year, len(this_year), hs_gpa_means[year])

  sat_verb_means = {}
  sat_math_means = {}
  for year in years:
    this_year = [s for s in valid_sat_data if s['entry_year'] == str(year)]
    if len(this_year) > 0:
      sat_verb_means[year] = int(round(sum(float(r['sat_verbal']) for r in this_year) / len(this_year)))
      sat_math_means[year] = int(round(sum(float(r['sat_math']) for r in this_year) / len(this_year)))
    else:
      sat_verb_means[year] = sat_verb_mean
      sat_math_means[year] = sat_math_mean
    print("%s SAT means: %d %d (n=%d)" % (year, sat_verb_means[year], sat_math_means[year], len(this_year)))
      
  print('Loading people...')
  people = {p['PEOPLE_CODE_ID']: p for p in csv.DictReader(open('data/people.csv'))}

  print('Loading addresses...')
  address = {p['PEOPLE_ORG_CODE_ID']: p for p in csv.DictReader(open('data/address.csv')) if p['ADDRESS_TYPE'] == 'PERM'}

  with open('data/clean_data.tsv','w') as fout:
    fieldnames = list(map(str.lower,reader.fieldnames))+['name','hs_grade','white','black','mexican_american','native_american','asian','hispanic', 'graduated_in_6', 'us_zip', 'country', 'zip_pci', 'international'] 
    fieldnames.remove('race')
    fieldnames.remove('sat_writing')
    fieldnames.remove('act_comp')
    fieldnames.remove('enrolled_in_entry_term')
    fieldnames.remove('lastupdated')
  
    writer = csv.DictWriter(fout,fieldnames=fieldnames,dialect='excel-tab',extrasaction='ignore')

    writer.writeheader()
    for row in data:
      if row['entry_year'] <= '2016' and row['entry_year'] >= '1991':
        row['name'] = "%s %s" % (people[row['people_code_id']]['FIRST_NAME'], people[row['people_code_id']]['LAST_NAME'],)
        try:
          row['country'] = address[row['people_code_id']]['COUNTRY']
          if row['country'] == 'US' or row['country'] == '':
            row['us_zip'] = address[row['people_code_id']]['ZIP_CODE']
          else:
            row['us_zip'] = ''
        except KeyError:
          row['us_zip'] = ''
          row['country'] = ''
        try:
          row['zip_pci'] = zip_pci_map[row['us_zip']]
        except KeyError:
          row['zip_pci'] = pci # Mean imputation
        row['hs_gpa'] = float(row['hs_gpa']) or hs_gpa_means[row['entry_year']] # Mean imputation
        row['hs_grade'] = convert_gpa_to_grade(float(row['hs_gpa']))
              
        row['sat_verbal'] = float(row['sat_verbal']) or sat_verb_mean # Mean imputation
        row['sat_math'] = float(row['sat_math']) or sat_math_mean # Mean imputation
        row['gender'] = 2 if row['gender'] == 'Female' else 1
        row['white'] = 2 if row['race'].startswith('White') else 1
        row['black'] = 2 if row['race'] == 'African American' else 1
        row['mexican_american'] = 2 if row['race'] == 'Mexican American' else 1
        row['native_american'] = 2 if row['race'] == 'American Indian/Alaskan Native' else 1
        row['asian'] = 2 if row['race'] == 'Asian' else 1
        row['hispanic'] = 2 if row['race'] == 'Hispanic' else 1
        row['international'] = 2 if row['country'] != '' and row['country'] != 'US' else 1
  
        row['graduated_in_6'] = int((row['undergrad_grad_date'] or False) and row['undergrad_grad_date'] < "%d/08" % (int(row['entry_year']) + 6))
        row['retained'] = int(bool(row['retained']))
  
        writer.writerow(row)