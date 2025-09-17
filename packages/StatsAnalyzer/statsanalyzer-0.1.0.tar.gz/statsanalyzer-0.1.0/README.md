# StatsAnalyzer

مكتبة Python لتحليل البيانات الرقمية وإجراء إحصائيات متقدمة.

## تثبيت

py -m pip install StatsAnalyzer

python
نسخ الكود

## استخدام

from statsanalyzer import mean, median, variance, std_dev, min_max, summary

data = [10, 20, 30, 40, 50]

print("Mean:", mean(data))
print("Median:", median(data))
print("Variance:", variance(data))
print("Standard Deviation:", std_dev(data))
print("Min/Max:", min_max(data))
print("Summary:", summary(data))