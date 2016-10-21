import csv
import os
import shutil
import matplotlib
matplotlib.use('Agg') # don't use x server backend
import matplotlib.pyplot as plt
import seaborn as sns

import astin97

start_year = "2011"

if __name__ == '__main__':
  print('Loading people...')
  people = {p['PEOPLE_CODE_ID']: p for p in csv.DictReader(open('people.csv'))}

  print('Loading IPEDS retention...')
  actual_retention = list(csv.DictReader(open('actual-retention.tsv'),dialect='excel-tab'))
  actual_retention = [s for s in actual_retention if s['class_year'] >= start_year]

  print('Loading retention report data...')
  student_data = list(csv.DictReader(open('clean_data.tsv','r'),dialect='excel-tab'))

  def build_results(path, filter=lambda r: True):
    print('Building results for %s...' % path)
    
    if not os.path.exists(path):
      os.makedirs(path)

    data = [s for s in student_data if filter(s) and s['entry_year'] >= start_year]
    
    for row in data:
      row['name'] = "%s %s" % (people[row['people_code_id']]['FIRST_NAME'], people[row['people_code_id']]['LAST_NAME'],)
            
      row['expected_retention'] = astin97.predict_retention(row)
      row['expected_four_year'] = astin97.predict_four(row)
      row['expected_six_year'] = astin97.predict_six(row)
      row['expected_six_year_academic'] = astin97.predict_six_academic(row)
        
    with open('%s/expected_graduation_rate_by_year.tsv' % path, 'w') as f_agg:
      agg_writer = csv.DictWriter(f_agg, dialect='excel-tab', extrasaction='ignore', fieldnames=[
        'year', 'expected_four_year', 'under_50_four_year', 'expected_six_year_academic', 'expected_six_year', 'under_50_six_year', 'calculated_six_year','expected_retention','calculated_retention','calculated_retention',
      ])
      agg_writer.writeheader()

      years = sorted(set([r['entry_year'] for r in data if r['entry_year'] >= start_year]))
      
      for year in years:
        print("%s %s..." % (path, year))
        year_data = sorted([r for r in data if r['entry_year'] == str(year) and r['entry_term'] == 'FALL'], key = lambda r:r['expected_four_year'])

        agg_writer.writerow({
          'year': year,
          'expected_retention': '%.3f' % (sum(float(r['expected_retention']) for r in year_data) / len(year_data)),
          'expected_four_year': '%.3f' % (sum(float(r['expected_four_year']) for r in year_data) / len(year_data)),
          'expected_six_year': '%.3f' % (sum(float(r['expected_six_year']) for r in year_data) / len(year_data)),
          'expected_six_year_academic': '%.3f' % (sum(float(r['expected_six_year_academic']) for r in year_data) / len(year_data)),
          'calculated_six_year': '%.3f' % (sum(float(r['graduated_in_6']) for r in year_data) / len(year_data)),
          'calculated_retention': '%.3f' % (sum(float(r['retained']) for r in year_data) / len(year_data)),
          'under_50_four_year': len([r for r in year_data if r['expected_four_year'] < .50]),
          'under_50_six_year': len([r for r in year_data if r['expected_six_year'] < .50]),
        })

        plt.hist([r['expected_six_year'] for r in year_data], 20)
        plt.xlabel('Six year graduation chance')
        plt.ylabel('Count')
        plt.title('Histogram of %s expected 6 year grad rate' % year)
        plt.savefig('%s/%s_expected_six_histogram.png' % (path, year))
        plt.close()

        with open('%s/%s_ftiac_expected_graduation.tsv' % ((path), year), 'w') as f_year:
          year_writer = csv.DictWriter(f_year, dialect='excel-tab', extrasaction='ignore', fieldnames=[
            'people_code_id', 'name', 'expected_retention', 'expected_four_year', 'expected_six_year','expected_six_year_academic','college', 
          ])
          year_writer.writeheader()
          for row in year_data:
            row = row.copy()
            row['college'] = row['college']
            row['expected_retention'] = '%.2f' % row['expected_retention']
            row['expected_four_year'] = '%.2f' % row['expected_four_year']
            row['expected_six_year'] = '%.2f' % row['expected_six_year']
            row['expected_six_year_academic'] = '%.2f' % row['expected_six_year_academic']
            year_writer.writerow(row)

      shutil.copyfile('%s/%s_ftiac_expected_graduation.tsv' % (path, years[-1]), '%s/%s_ftiac_expected_graduation.tsv' % (path, 'latest'))
      shutil.copyfile('%s/%s_expected_six_histogram.png' % (path, years[-1]), '%s/%s_expected_six_histogram.png' % (path, 'latest'))

    with open('%s/expected_graduation_rate_by_year.tsv' % path, 'r') as f_agg:
        data = [r for r in csv.DictReader(f_agg, dialect='excel-tab')]

        years = [r['year'] for r in data]
        actual_only_retention = [float(r['retention_rate']) for r in actual_retention if r['retention_rate'] and float(r['retention_rate']) > 0.0]
        expected_only_retention = [float(r['expected_retention']) for r in data][:-1]

        overall_means = {
          "expected_retention": sum(expected_only_retention) / len(expected_only_retention),
          #"calculated_retention": sum([float(r['calculated_retention']) for r in data][:-1]) / 24.,
          "actual_retention": sum(actual_only_retention) / len(actual_only_retention),
        }
        
        plt.legend(frameon=True, loc='lower right', handles = [
          plt.plot(years, [r['expected_six_year'] for r in data], label='Expected Six Year')[0],
          plt.plot([r['year'] for r in data], [r['expected_six_year_academic'] for r in data], label='Expected Six Year (only GPA+SAT)')[0],
          plt.plot([r['class_year'] for r in actual_retention if r['six_year_grad_rate']], [r['six_year_grad_rate'] for r in actual_retention if r['six_year_grad_rate']], label = 'Actual Six Year')[0],
        ])
        plt.xlabel('Year')
        plt.ylabel('Expected')
        plt.title('Expected 6 year grad rate')
        plt.savefig('%s/expected_6_by_year.png' % path)
        plt.close()

        plt.legend(frameon=True, loc='lower right', handles = [
          plt.plot(years, [r['expected_four_year'] for r in data], label='Expected Four Year')[0],
          plt.plot([r['class_year'] for r in actual_retention if r['four_year_grad_rate']], [r['four_year_grad_rate'] for r in actual_retention if r['four_year_grad_rate']], label = 'Actual Four Year')[0],
        ])
        plt.xlabel('Year')
        plt.ylabel('Expected')
        plt.title('Expected 4 year grad rate')
        plt.savefig('%s/expected_4_by_year.png' % path)
        plt.close()

        def get_expected_retention(year):
          return float([r['expected_retention'] for r in data if r['year'] == year][0])

        (fig, ax) = plt.subplots()
        
        plt.legend(frameon=True, loc='lower right', handles = [
          ax.fill_between(
            [int(r['year']) for r in data if r['year'] >= start_year],
            [100*float(r['expected_retention'])-4.4 for r in data if r['year'] >= start_year],
            [100*float(r['expected_retention'])+4.4 for r in data if r['year'] >= start_year],
            color="black", alpha=.1,
            label="±2 σ from expected",
          ),
          ax.fill_between(
            [int(r['year']) for r in data if r['year'] >= start_year],
            [100*float(r['expected_retention'])-2.2 for r in data if r['year'] >= start_year],
            [100*float(r['expected_retention'])+2.2 for r in data if r['year'] >= start_year],
            color="black", alpha=.2,
            label="±1 σ from expected",
          ),
          plt.plot([r['year'] for r in data if r['year'] >= start_year], [100.0 * float(r['expected_retention']) for r in data if r['year'] >= start_year], label='Expected Retention')[0],
          plt.plot([r['class_year'] for r in actual_retention if r['class_year'] >= start_year], [100.0* float(r['retention_rate']) for r in actual_retention if r['class_year'] >= start_year], label = 'Actual Retention')[0],

          plt.plot([r['year'] for r in data], [100.0*float(overall_means['expected_retention']) for r in data], label='Expected Retention Mean')[0],
          plt.plot([r['year'] for r in data], [100.0*float(overall_means['actual_retention']) for r in data], label='Actual Retention Mean')[0],

          #plt.plot([r['year'] for r in data][:-1], [r['calculated_retention'] for r in data][:-1], label='Calculated Retention')[0],
          #plt.plot([r['year'] for r in data], [overall_means['calculated_retention'] for r in data], label='Calculated Retention Mean')[0],
          #plt.plot([r['class_year'] for r in actual_retention], [.7 + float(r['retention_rate']) - get_expected_retention(r['class_year']) for r in actual_retention], label='Deviation')[0],
        ])
        plt.xlabel('Year')
        ax = plt.gca()
        ax.get_xaxis().get_major_formatter().set_useOffset(False)
        plt.ylabel('Retention Rate')
        plt.title('Expected Retention Rate by Year')
        plt.savefig('%s/expected_retention_by_year.png' % path)
        plt.close()

        plt.legend(frameon=True, loc='lower right', handles = [
          plt.plot([r['year'] for r in data], [r['expected_six_year'] for r in data], label='Expected Six Year')[0],
          plt.plot([r['class_year'] for r in actual_retention], [r['retention_rate'] for r in actual_retention], label = 'Actual Retention')[0],
        ])
        plt.xlabel('Year')
        plt.ylabel('Expected')
        plt.title('Expected 6 year grad rate vs actual retention')
        plt.savefig('%s/expected_6_by_year_vs_retention.png' % path)
        plt.close()
        
        plt.legend(frameon=True, loc='lower right', handles = [
          plt.plot([r['year'] for r in data], [r['under_50_six_year'] for r in data], label='Six Year')[0],
          plt.plot([r['year'] for r in data], [r['under_50_four_year'] for r in data], label='Four Year')[0],
        ])
        plt.xlabel('Year')
        plt.ylabel('Students')
        plt.title('Less than 50% chance of graduating')
        plt.savefig('%s/expected_6_by_year_under_50.png' % path)
        plt.close()


  build_results('results/all')
  build_results('results/main', lambda r:r['college'] == 'College of Arts and Sciences')
  #build_results('results/main-women', lambda r:r['college'] == 'College of Arts and Sciences' and r['gender'] == '2')
  #build_results('results/main-men', lambda r:r['college'] == 'College of Arts and Sciences' and r['gender'] == '1')
  #build_results('results/buffalo', lambda r:r['college'] == 'Buffalo AA')
