import csv

def convert_gpa_to_grade(hs_gpa):
    if hs_gpa > 3.7: return 8
    elif hs_gpa > 3.3: return 7
    elif hs_gpa > 3.0: return 6
    elif hs_gpa > 2.7: return 5
    elif hs_gpa > 2.3: return 4
    elif hs_gpa > 2.0: return 3
    elif hs_gpa > 1.7: return 2
    else: return 1

with open('data.csv','r') as fin:
  reader = csv.DictReader(fin)
  data = list(reader)

  print("Converting keys to lowercase...")
  for row in data:
      for k in row.keys():
        row[k.lower()] = row.pop(k)

  print("Calculating means for imputation...")
  valid_gpa_data = [s for s in data if s['hs_gpa'] and float(s['hs_gpa']) > 0 and float(s['hs_gpa']) < 5]
  valid_sat_data = [s for s in data if s['sat_verbal'] and float(s['sat_verbal']) > 0]
  
  hs_gpa_mean = "%.2f" % (sum(float(r['hs_gpa']) for r in valid_gpa_data) / len(valid_gpa_data))
  sat_verb_mean = int(round(sum(float(r['sat_verbal']) for r in valid_sat_data) / len(valid_sat_data)))
  sat_math_mean = int(round(sum(float(r['sat_math']) for r in valid_sat_data) / len(valid_sat_data)))

  with open('clean_data.tsv','w') as fout:
    fieldnames = list(map(str.lower,reader.fieldnames))+['hs_grade','white','african_american','mexican_american','native_american','graduated_in_6'] 
    fieldnames.remove('race')
    fieldnames.remove('sat_writing')
    fieldnames.remove('act_comp')
    fieldnames.remove('enrolled_in_entry_term')
    fieldnames.remove('lastupdated')
  
    writer = csv.DictWriter(fout,fieldnames=fieldnames,dialect='excel-tab',extrasaction='ignore')

    writer.writeheader()
    for row in data:
      #row['name'] = "%s %s" % (people[row['people_code_id']]['FIRST_NAME'], people[row['people_code_id']]['LAST_NAME'],)
      row['hs_gpa'] = float(row['hs_gpa']) or hs_gpa_mean # Mean imputation
      row['hs_grade'] = convert_gpa_to_grade(float(row['hs_gpa']))
            
      row['sat_verbal'] = float(row['sat_verbal']) or sat_verb_mean # Mean imputation
      row['sat_math'] = float(row['sat_math']) or sat_math_mean # Mean imputation
      row['gender'] = 2 if row['gender'] == 'Female' else 1
      row['white'] = 2 if row['race'].startswith('White') else 1
      row['african_american'] = 2 if row['race'] == 'African American' else 1
      row['mexican_american'] = 2 if row['race'] == 'Mexican American' else 1
      row['native_american'] = 2 if row['race'] == 'American Indian/Alaskan Native' else 1

      row['graduated_in_6'] = int((row['undergrad_grad_date'] or False) and row['undergrad_grad_date'] < "%d/08" % (int(row['entry_year']) + 6))
      row['retained'] = int(bool(row['retained']))

      writer.writerow(row)