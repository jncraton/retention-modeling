import csv
import random
import numpy
import matplotlib
matplotlib.use('Agg') # don't use x server backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats

with open('results/main/latest_ftiac_expected_graduation.tsv') as infile:
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
  plt.xlabel('Expected number of retained students')
  plt.ylabel('Simulation Count')
  plt.title(title)
  plt.savefig('results/main/lastest_overall_retention_count_histogram.png')
  plt.close()

  

  results = [100.0*float(r)/len(data) for r in results]
  npresults = numpy.asarray(results)
  title = "Histogram of %d simlated results (μ=%.01f%%, σ=%.01f%%, mode=%.01f)" % (sims, npresults.mean(), npresults.std(), stats.mode(npresults)[0][0])
  print(title)

  bins = [100.0*float(b) / len(data) for b in bins]

  plt.hist(results, bins=bins)
  plt.xlabel('Expected number of retained students')
  plt.ylabel('Simulation Count')
  plt.title(title)
  plt.savefig('results/main/lastest_overall_retention_histogram.png')
  plt.close()