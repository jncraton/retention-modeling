import csv
import random
import numpy
import matplotlib
matplotlib.use('Agg') # don't use x server backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats

actual_retention = {}
with open('actual-retention.tsv', 'r') as fact:
  for row in csv.DictReader(fact, dialect='excel-tab'):
    actual_retention[row['class_year']] = row['retention_rate']
    
years = ['2016','2015','2014','2013','2012']
campus = 'all'

for year in years:
  with open('results/%s/%s_ftiac_expected_graduation.tsv' % (campus,year)) as infile:
    data = [float(r['expected_retention']) for r in csv.DictReader(infile, dialect='excel-tab')] 
  
    sims = 20000
    results = []
    
    for sim in range(sims):
      if not sim % 1000:
        print("Running simulation %d" % sim)
        
      retained = 0.
      for expected_retention in data:
        if expected_retention >= random.SystemRandom().random():
          retained += 1
    
      results.append(retained)
  
    npresults = numpy.asarray(results)
    title = "Histogram of %d simlated results (μ=%.00f, σ=%.01f, mode=%.00f)" % (sims, npresults.mean(), npresults.std(), stats.mode(npresults)[0][0])
    print(title)
  
    bins = [bin for bin in range(int(npresults.mean()) - 20, int(npresults.mean()) + 20)]
  
    plt.hist(results, bins=bins)
    plt.xlabel('Number of retained %s students' % year)
    plt.ylabel('Simulation Count')
    plt.title(title)
    plt.savefig('results/%s/%s_overall_retention_count_histogram.png' % (campus,year))
    plt.close()
  

    results = [100.0*float(r)/len(data) for r in results]
    npresults = numpy.asarray(results)
    title = "Histogram of %d simlated results (μ=%.01f%%, σ=%.01f%%, mode=%.01f%%)" % (sims, npresults.mean(), npresults.std(), stats.mode(npresults)[0][0])
    print(title)
  
    bins = [100.0*float(b) / len(data) for b in bins]
  
    plt.hist(results, bins=bins)
    plt.xlabel('%s retention percentage' % year)
    plt.ylabel('Simulation Count')
    plt.title(title)
    if year in actual_retention.keys():
      plt.axvline(100.0*float(actual_retention[year]), color='black', linestyle='dashed', linewidth=2)
      plt.text(100.0*float(actual_retention[year]), 400, "Actual Retention",rotation=90, bbox=dict(facecolor='white', alpha=0.8), ha='center', va='center')
    else:
      plt.axvline(npresults.mean(), color='black', linestyle='dashed', linewidth=2)
      plt.text(npresults.mean(), 400, "Expected Retention", rotation=90, bbox=dict(facecolor='white', alpha=0.8), ha='center',va='center')
                        
    plt.savefig('results/%s/%s_overall_retention_histogram.png' % (campus,year))
    plt.close()