import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def box_plot(pdf, cols, figsize = (15,5), with_outliers = False):
  
  """  
  Creates one box plot per column in cols.
  
  Input
  ______
  pdf : pandas dataframe
  cols : list of numeric columns
  
  Returns
  ______
  One box plot per column in cols
  """
  
  for col in cols:
    
    fig, ax = plt.subplots(figsize = figsize)
    if with_outliers == False:
      sns.boxplot(y = col, data=pdf, showfliers = False, color = '#00857a', ax = ax)
    else:
      sns.boxplot(y = col, data=pdf, showfliers = True, color = '#00857a', ax = ax)
  pass

def box_plot_time(pdf, cols, snapshotcol, period = 'yearly', figsize = (15,5), with_outliers = False):
  
  """
  
  Creates one box plot per column in cols over a specified period.
  
  Input
  _____
  pdf : pandas dataframe
  cols : list of numeric columns
  snapshotcol : name of snapshot column
  period : 'yearly', 'quarterly', 'monthly' or None
  figsize : define size of plot  

  Returns :
  ------
  One box plot per column in cols
  """
  
  for col in cols:
    
    pdf_tmp = pdf[[col, snapshotcol]]
    
    if period == 'yearly':
      x_label = 'year'
      pdf_tmp[x_label] = pdf_tmp[snapshotcol].dt.year
      
    elif period == 'quarterly':
      x_label = 'quarter'
      pdf_tmp[x_label] = pdf_tmp[snapshotcol]
      pdf_tmp = pdf_tmp[pdf_tmp[x_label].dt.month.isin([3,6,9,12])]
      pdf_tmp[x_label] = pdf_tmp[x_label].dt.strftime('%Y-%m')
    
    elif period == 'monthly':
      x_label = 'month'
      pdf_tmp[x_label] = pdf_tmp[snapshotcol]
      pdf_tmp[x_label] = pdf_tmp[x_label].dt.strftime('%Y-%m')
      
    else:
      x_label = snapshotcol
      
    fig, ax = plt.subplots(figsize = figsize)
    if with_outliers == False:
      sns.boxplot(x=x_label, y = col, data=pdf_tmp.sort_values(x_label), showfliers = False, color = '#00857a', ax = ax)
    else:
      sns.boxplot(x=x_label, y = col, data=pdf_tmp.sort_values(x_label), showfliers = True, color = '#00857a', ax = ax)
    ax.tick_params(axis='x', rotation=45)
  pass

def hist_plot(pdf, cols, percentiles = None):
  """
  Plots one historgram per column in cols
  
  Input
  _____
  pdf : Pandas dataframe
  cols : List of column names
  Percentiles : None or [a, b] where a and b are between 0 and 1
 
  Returns
  ------
  One histogram per column in cols
  """
  
  pdf_tmp = pdf.copy()
  
  for col in cols:
    
    if not percentiles:
      pdf_tmp[[col]].hist()
      
    else:
      pdf_tmp_1 = pdf_tmp[(pdf_tmp[col]>pdf_tmp[col].quantile(percentiles[0])) & (pdf_tmp[col]<pdf_tmp[col].quantile(percentiles[1]))]
      pdf_tmp_1[[col]].hist()
      
  pass


def agg_method_time(pdf, cols, snapshotcol, agg_method = 'mean'):  
  """
  Plots specified aggregation method over time for each column in cols
      
  Input
  ------
  pdf: pandas dataframe
  cols: List of column names
  snapshotcol : Name of snapshot column
  agg_method : 'mean', 'median', 'min', 'max', 'sum'

  Returns
  ------
  One plot for each column in cols  
  """
  
  for col in cols:
    fig, ax = plt.subplots()
    pdf_tmp = pdf[[snapshotcol, col]].groupby(snapshotcol)[[col]].agg(agg_method)
    sns.lineplot(x = pdf_tmp.index, y = col, data = pdf_tmp, label = agg_method, ax =ax)
    ax.tick_params(axis='x', rotation=45)                
  pass


def descriptive_statistics(pdf, percentiles = [0.0, 0.001, 0.01, 0.05, 0.95, 0.99, 0.999, 1.0], dp = 3):
  
  """
  Returns descriptive statistics for all columns in cols. 
      
  Input
  ------
  pdf: pandas dataframe
  percentiles = [a, b, c] percentile values
  dp : number of decimal places

  Returns
  ------
  One pandas table containing results for all columns in cols
  """
  
  return pdf.quantile(percentiles).transpose().round(dp).reset_index().rename(columns={'index': 'riskdriver'})


def pct_obs_exceeding_percentile(pdf, cols, method = 'all', percentiles = [[0.01, 0.99], [0.05, 0.95], [0.2, 0.8]], dp = 2):
  """
  returns the percentage of observations that exceeds the defined percentiles for each column in cols.  
      
  Input
  ______
  pdf: pandas dataframe
  cols: List of column names
  method : 'all' (exceeds lower or upper bound), 'lowerbound', 'upperbound'
  percentiles = [[a,b], [c,d], [e,f]] percentile values
  dp : number of decimal places

  Returns
  ______
  One pandas table containing results for all columns in cols
  """
  
  pdf_tmp = pdf.copy()[cols]
  
  df = pd.DataFrame(index = cols)
  
  total = len(pdf_tmp)
  
  for perc in percentiles:
    
    percentage = []
    
    for col in cols:
      
      if method == 'all':
        percentage.append(
          round(100*len(pdf_tmp[(pdf_tmp[col]<pdf_tmp[col].quantile(perc[0])) | (pdf_tmp[col]>pdf_tmp[col].quantile(perc[1]))])/total, dp))
        label = str(perc)
        
      elif method == 'lowerbound':
        percentage.append(round(100*len(pdf_tmp[pdf_tmp[col]<pdf_tmp[col].quantile(perc[0])])/total, dp))
        label = str(perc[0])
        
      elif method == 'upperbound':
        percentage.append(round(100*len(pdf_tmp[pdf_tmp[col]>pdf_tmp[col].quantile(perc[1])])/total, dp))
        label = str(perc[1])
        
      else:
        raise ValueError("Unrecognised method given. Choose from 'all', 'lowerbound' or 'upperbound'.")
      
    df[label] = percentage
    
  return df


def pct_obs_exceeding_factor(pdf, cols, method = 'all', factors = [1e5, 1e10], dp = 2):
  
  """
  Returns the percentage of observations that exceeds the median multiplied by a scalar. 
      
  Input
  ______
  pdf: pandas dataframe
  cols: List of column names
  method : 'all', 'greater', 'less'
  factor : [a,b,c]
  dp : number of decimal places

  Returns
  ______
  One pandas table containing results for all columns in cols
  """
  
  pdf_tmp = pdf.copy()[cols]
  
  df = pd.DataFrame(index = cols)
  
  total = len(pdf_tmp)
  
  for factor in factors:
    
    percentage = []
    
    for col in cols:
      
      if method == 'greater':
        percentage.append(round(100*len(pdf_tmp[pdf_tmp[col]>pdf_tmp[col].median()*factor])/total, dp))
        
      elif method == 'less':
        percentage.append(round(100*len(pdf_tmp[pdf_tmp[col]<pdf_tmp[col].median()/factor])/total, dp))
      
      elif method == 'all':
        percentage.append(
          round(100*len(pdf_tmp[(pdf_tmp[col]<pdf_tmp[col].median()/factor) | (pdf_tmp[col]>pdf_tmp[col].median()*factor)])/total, dp))
    
      else:
        raise ValueError("Unrecognised method given. Choose from 'all', 'less' or 'greater'.") 
      
    df[str(factor)] = percentage
    
  return df


def testing_differences_over_time(pdf, key, cols, snapshot, return_method = 'significant'):
  
  """
  Tests for each column whether one snapshot's difference deviates from all other snapshot's differences
      
  Parameters
  ----------
  pdf: pandas dataframe
  cols: List of column names
  snapshot : Name of snapshot column
  return_method : 'all' or 'signifcant'

  Returns
  ----------
  Pandas with indicators which snapshot and column's deviates from the rest of the snapshot
  
  """
  
  pd.set_option('display.max_rows', 500)
  
  from scipy.stats import ttest_ind
  
  pdf_tmp = pdf.copy()
  
  results = {}
  
  pdf_tmp = pdf_tmp.sort_values(by=[key, snapshot])
  
  snapshot_list = pdf[snapshot].unique()
  
  for c in cols:
    
    # Shift the column (partitioned by key)
    pdf_tmp[c + "_shifted"] = pdf_tmp.groupby(key)[c].shift(1)
    
    # Determine difference
    pdf_tmp[c + "_difference"] = pdf_tmp[c] - pdf_tmp[c + "_shifted"]
    
    # Test for each snapshot whether it deviates from the other snapshots
    for s in snapshot_list:
      
      a = pdf_tmp[pdf_tmp[snapshot] == s][c + "_difference"].dropna()
      b = pdf_tmp[pdf_tmp[snapshot] != s][c + "_difference"].dropna()
    
      test_result = ttest_ind(a, b, equal_var=False)
      
      results[(c, s)] = test_result
      
      all_results = pd.DataFrame.from_dict(results).transpose().rename(columns={0:"t-statistics", 1:"p-value"})
      significant_results = all_results[all_results["p-value"] < 0.05]
  
  if return_method == 'all':
    return all_results.sort_index()
  elif return_method == 'significant':
    return significant_results.sort_index()
  else:
    return ValueError("Unexpected return_method provided. Choose from 'all' or 'signifcant'")
  
  
def inflow_outflow(pdf,reference_date,key):
  '''
  Computes the amount of outflowing and inflowing keys per reference, amount of outflowing keys that show up again somewhere in the future per reference date and the amount of times that a client flows in and out
  
  Parameters
  ----------
  pdf: pandas dataframe
  reference_date: column in the pdf that contains the reference dates
  key: the key that you want to compute the ouflow and inflow for
  
  Returns
  ----------
  3 plots:
  1. Shows the keys and the amount of the times that they flow out and in
  2. Shows per reference date how many keys flow out that show up again in the future
  3. Shows the outflow and inflow per reference date
  '''
  
  pdf_tmp = pdf.copy().sort_values([key, reference_date])
  pdf_tmp['lag'] = pdf_tmp.groupby(key)[reference_date].shift(1)
  pdf_tmp['lead'] = pdf_tmp.groupby(key)[reference_date].shift(-1)
  pdf_tmp['diff_lag'] = (pdf_tmp[reference_date] - pdf_tmp['lag']).dt.days
  pdf_tmp['diff_lead'] = (pdf_tmp['lead'] - pdf_tmp[reference_date]).dt.days
  
  pdf_tmp1 = pd.DataFrame(pdf_tmp[pdf_tmp['diff_lag']>31].groupby(key)[key].count().sort_values(ascending = False)).rename(columns = {key:'count'})
  pdf_tmp2 = pd.DataFrame(pdf_tmp[pdf_tmp['diff_lead']>31].groupby(reference_date)[reference_date].count()).rename(columns = {reference_date : 'count'})
  
  dates = np.sort(pdf[reference_date].unique(), axis=0)
  inflow_outflow = []
  
  for i in range(0,len(dates)-1):
    inflow = pdf[pdf[reference_date]==dates[i+1]][key].isin(pdf[pdf[reference_date]==dates[i]][key]).tolist().count(False)
    outflow = pdf[pdf[reference_date]==dates[i]][key].isin(pdf[pdf[reference_date]==dates[i+1]][key]).tolist().count(False)
    inflow_outflow.append((dates[i+1], inflow, outflow))
    
  pdf_inflow_outflow = pd.DataFrame(inflow_outflow, columns=['reference_date', 'inflow', 'outflow'])
  
  pdfs = [pdf_tmp1, pdf_tmp2, pdf_inflow_outflow]
  
  f, axs = plt.subplots(3,1, sharey=False, sharex=False, figsize=(30,40))
  f.suptitle('Inflow outflow analysis', fontweight = 'bold', fontsize=20)
  axs[0].bar(pdf_tmp1.index.astype(str), pdf_tmp1['count'], label='Amount of times that the key flows in and out')
  axs[0].set_xlabel(reference_date)
  axs[0].set_ylabel('count')
  axs[0].set_xticklabels(pdf_tmp1.index.astype(str),rotation = 90)
  axs[1].plot(pdf_tmp2.index, pdf_tmp2['count'], label='Amount of keys flowing out that show up again in the future per reference date')
  axs[1].set_xlabel(reference_date)
  axs[1].set_ylabel('count')
  axs[2].plot(pdf_inflow_outflow['reference_date'], pdf_inflow_outflow['inflow'], label='Inflow')
  axs[2].plot(pdf_inflow_outflow['reference_date'], pdf_inflow_outflow['outflow'], label='Outflow')
  #axs[2].set_xticklabels(axs[2].get_xticklabels(),rotation = 90)
  axs[2].set_xlabel(reference_date)
  axs[2].set_ylabel('count')
  plt.legend()
  plt.show()
  
  pass

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pyspark.sql.functions as F
from pyspark.sql.window import Window
from matplotlib import colors as colors2


def completeness_report_pandas(pdf, cols, snapshot_col):
    """
    Generates a completeness report for the specified columns per snapshot.

    The report shows the percentage of non-null values for each column in the input DataFrame,
    grouped by the snapshot column. The resulting table is styled with a background gradient
    to visually represent completeness.

    Parameters:
    pdf (pandas.DataFrame): The input DataFrame containing the data.
    cols (list of str): The list of columns to check for completeness.
    snapshot_col (str): The name of the column representing snapshots (must be of datetime type).

    Returns:
    pandas.io.formats.style.Styler: A styled DataFrame showing the completeness of each column per snapshot.
    """

    pdf_dq = pdf.copy()

    pdf_dq[snapshot_col] = pdf_dq[snapshot_col].dt.strftime("%Y-%m")
    pdf_dq_table = (
        pdf_dq.groupby(snapshot_col)[cols].apply(lambda x: x.notnull().mean()).T
    )

    output_table = (
        pdf_dq_table.style.background_gradient(
            subset=pdf_dq_table.columns, cmap="RdYlGn", vmin=0, vmax=1
        )
        .format(dict.fromkeys(pdf_dq_table.keys(), "{:.1%}"))
        .set_table_attributes('style="border-collapse:collapse"')
        .set_properties(**{"text-align": "right", "font-size": "9pt"})
        .set_table_styles(
            [
                {"selector": "th", "props": [("font-size", "9pt")]},
                {"selector": "tbody tr th", "props": [("text-align", "right")]},
                {"selector": "thead tr th", "props": [("text-align", "right")]},
                {"selector": "th", "props": [("text-align", "center")]},
            ]
        )
    )

    return output_table


def create_proportion_of_missing_table(pdf: pd.DataFrame, cols: list[str]):
    """
    Returns one pandas table with the proportion of missings for each column in cols.

    parameters
    ----------
    pdf : pandas.DataFrame
        DataFrame containing the columns for which the proportion of missing is checked
    cols : list[str]
        List containing the name of the columns for which the proportion of missing is measured

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the columns 'missing_proportion', 'unique_values', 'discrimination_possible' 
    """
    return pd.DataFrame({
        "missing_proportion": [len(pdf[pdf[col].isna()]) / len(pdf) for col in cols], 
        "unique_values": [pdf[col].nunique() for col in cols], 
        "discrimination_possible": [pdf[col].nunique() > 1 for col in cols], 
    }, index=cols)
  
def completeness_report(spark_session,
                        sdf,
                        cols,
                        snapshotcol = "_ReferenceDateEOM",
                        snapshot_interval = "monthly"):
  
  """
  This function produces a table with the data completeness over time for each column in cols.
  The table is styled to provide easily interpretable output.

  Input
  _____
  sdf : spark dataframe
  cols : list of columns names
  snapshotcol : name of date column
  snapshot_interval : "daily", "monthly" or "yearly"

  Returns
  _____
  pandas table
  """
  ############################################################################
  #Step 1 : Compute the percentage of missing values per snapshot per variable 
  ############################################################################
  if snapshot_interval == 'daily':

    min_, max_ = sdf.agg(F.min(snapshotcol), F.max(snapshotcol)).first()

    # construct dataframe of all dates
    dates = spark_session.sql(f"select sequence(to_date('{min_}'), to_date('{max_}'), interval '1' day) as {snapshotcol}") \
                    .withColumn(snapshotcol, F.explode(snapshotcol)) 

    joined = dates.join(sdf, [snapshotcol], how='left')

    joined = joined.withColumn(snapshotcol, F.date_format(snapshotcol, "yyyy-MM-dd"))

  elif snapshot_interval == 'monthly':

    min_, max_ = sdf.agg(F.min(snapshotcol), F.max(snapshotcol)).first()

    # construct dataframe of all dates
    dates = (
      spark_session.sql(f"select sequence(to_date('{min_}'), to_date('{max_}'), interval '1' month) as {snapshotcol}")
      .withColumn(snapshotcol, F.explode(snapshotcol)) 
      .withColumn(snapshotcol, F.last_day(snapshotcol))
    )

    joined = dates.join(sdf, [snapshotcol], how='left')

    joined = joined.withColumn(snapshotcol, F.date_format(snapshotcol, "yyyy-MM"))

  elif snapshot_interval == 'yearly':
    joined = sdf.withColumn(snapshotcol, F.date_format(snapshotcol, "yyyy"))
    
  else:
    raise Expception("Invalid snapshot_interval provided")
  
  cnt = (
    joined
    .withColumn('__cntall__', F.lit(1))
    .groupBy(snapshotcol)
    .agg(*(F.count(F.col(c)).alias(c) for c in cols + ['__cntall__']))
  )

  pct = cnt.select(snapshotcol, *[((F.col(c))/(F.col('__cntall__'))).name(c) for c in cols])

  # ###########################################################################
  # #Step 2 : Convert to Pandas  
  # ###########################################################################
  df = (
    pct
    .toPandas()
    .set_index(snapshotcol)
    .sort_index()
    .T
  )

  # ############################################################################
  # #Step 3 : Apply styling
  # ############################################################################
  df = (df
        .style
        .background_gradient(subset=df.columns, cmap="RdYlGn", vmin=0, vmax=1)
        .format(dict.fromkeys(df.keys(), '{:.1%}'))
        .set_table_attributes('style="border-collapse:collapse"')
        .set_properties(**{'text-align': 'right', 'font-size': '9pt'})
        .set_table_styles([{'selector': 'th', 'props': [('font-size', '9pt')]},
                          {'selector': 'tbody tr th', 'props': [('text-align', 'right')]},
                          {'selector': 'thead tr th', 'props': [('text-align', 'right')]},
                          {'selector': 'th', 'props': [('text-align', 'center')]}])
  )
  
  return df

def missing_percentage(pdf, cols, threshold = 75, dp = 2):
  
  """
  Returns one pandas table with % of missings for each column in cols.
  
  Input
  ______
  pdf : pandas dataframe
  cols : list of column names
  threshold : acceptable % of missings
  dp: number of decimal places
  
  Returns
  ______
  One table containing results for all columns in cols
  """
  
  df = pd.DataFrame(index = cols)
  
  total = len(pdf)
  
  percentage = []
  
  outcome = []
  
  for col in cols:
    
    pct = 100*len(pdf[pdf[col].isna()])/total
    
    percentage.append(round(pct, dp))
    
    if pct < threshold:
      outcome.append('Usable')
    else:
      outcome.append('Not Usable')
  
  df['% Missing'] = percentage
  
  df['Result'] = outcome
  
  return df.sort_values('% Missing', ascending = False)

def na_heatmap(pdf, cols, snapshotcol):
  """
  Returns one heatmap plot of the missing values for all columns in cols.
  
  Input
  ______
  pdf : Pandas dataframe
  cols : list of column names
  
  Returns
  ______
  Single heatmap plot
  """
  
  plt.figure(figsize=(10,6))
  pdf = pdf.set_index(snapshotcol).sort_index()
  pdf.index = pdf.index.date

  sns.heatmap(pdf[cols].isna().transpose(),
            cmap="YlGnBu",
            cbar_kws={'label': 'Missing Data'})
  pass


def change_in_na_over_time(pdf, cols, snapshotcol, factor = 10):
  
  """
  Returns snapshots dates per column in cols where there is a substantial change in number of missing values (determined by factor)
  
  Input
  ______
  pdf : pandas dataframe
  cols : list of column names
  snapshotcol : name of snapshot column
  factor : magnitude of change in number of values
  
  Returns
  ______
  pdf
  """ 
  
  df = pd.DataFrame()
  
  for col in cols:
    
    tmp = pdf.groupby(snapshotcol).apply(lambda c : c.isna().sum())[[col]]
    
    tmp[col + '_diff'] = abs(tmp[col] - tmp[col].shift(1))
    
    try:
      
      df = pd.concat([df, 
                      pd.DataFrame(tmp[tmp[col+ '_diff']>(tmp[col + '_diff'].median()+1)*factor][[col + '_diff']]\
                                   .unstack())\
                                   .rename(columns = {0:'Change in nr of missings'})])
      
    except:
      
      pass
  
  return df



def rel_change_in_na_over_time(pdf, cols, snapshotcol, threshold = 0.05, min_nas = 10):
  """
  Returns one pandas table containing snapshots per column in cols where 
  there is a substantial relative change in mumber of missing values (determined by threshold)
  
  Input
  ______
  pdf : pandas dataframe
  cols : list of column names
  snapshotcol : name of snapshot column
  threshold : cut off value for relative change
  min_nas : minimum number of NAs that need to exist in order to calculate relative change. 
  
  Returns
  ______
  pdf table
  """ 
  
  df = pd.DataFrame()
  
  for col in cols:
    
    tmp = pdf.groupby(snapshotcol).apply(lambda c : c.isna().sum())[[col]]
    
    tmp = tmp[tmp[col]>min_nas]
    
    tmp[col + '_rel'] = abs(tmp[col] - tmp[col].shift(1))/(tmp[col].shift(1))
    
    try:
      
      df = pd.concat([df, 
                      pd.DataFrame(tmp[tmp[col+ '_rel']>threshold][[col + '_rel']]\
                                       .unstack()).rename(columns = {0:'Relative change in nr of missings'})])
      
    except:
      
      pass
  
  return df


def na_per_year_table(pdf, cols, snapshotcol, dp = 2):
  """
  Computes the number of missing values per year for columns in cols. 
  
  Input
  ----------
  pdf: pandas dataframe
  snapshotcol: str, column with snapshot dates in pdf
  cols: list of str, columns for which na is computed in pdf
  dp : number of decimal places
  
  Returns
  ----------
  missing_cols: one pandas dataframe, missing values per year and in total
  """
  
  # Check NA values in total
  
  total = len(pdf)
  
  df = pdf.groupby(pdf[snapshotcol].dt.year).apply(lambda c : c.isnull().sum())[cols]
  
  for col in cols:
    df[col] = round(100*df[col]/pdf.groupby(pdf[snapshotcol].dt.year)[snapshotcol].count(), dp)
  
  df.index.name = None
  df = df.transpose()
  
  df['Total'] = round(100*pdf.isna().sum()[cols]/total,dp)
  
  return df

def na_per_snapshot_table(pdf, cols, snapshotcol, dp = 2):
  """
  Computes the number of missing values per snapshot for columns in cols. 
  
  Input
  ----------
  pdf: pandas dataframe
  snapshotcol: str, column with snapshot dates in pdf
  cols: list of str, columns for which na is computed in pdf
  dp : number of decimal places
  
  Returns
  ----------
  missing_cols: one pandas dataframe, missing values per year and in total
  """
  
  # Check NA values in total
  
  total = len(pdf)
  
  df = pdf.groupby(pdf[snapshotcol]).apply(lambda c : c.isnull().sum())[cols]
  
  for col in cols:
    df[col] = round(100*df[col]/pdf.groupby(pdf[snapshotcol])[snapshotcol].count(), dp)
  
  df.index.name = None
  df = df.transpose()
  
  df['Total'] = round(100*pdf.isna().sum()[cols]/total,dp)
  
  return df


def statisticalProfile(sdf, snapshotDate, snapshotdate_interval, dateFormat = 'yyyy-MM'):
  """
  Computes the percentage of missing values per snapshot per variable .. Vivienne check! ..
  Written by Vivienne, changed by Kevin Aritonang
  Runs in ~? min
      
  Parameters
  ----------
  sdf: spark dataframe
  snapshotDate: Vivienne
  snapshotdate_interval: str, in ('daily', 'monthly', 'quaterly', 'yearly')
  dateFormat: str, Vivienne!

  Returns
  ----------
  spark dataframe visualizing the result in colors per snapshot per variable
  
  """
  
  allowed_types = ['DoubleType', 'FloatType', 'LongType', 'IntegerType', 'DecimalType']
  
  cols = [c for c in sdf.columns if c.lower() != snapshotDate.lower()]
  cols.append('__cntall__')
  if snapshotdate_interval == 'daily':
    minDate = sdf.agg({snapshotDate: 'min'}).first()[0]
    maxDate = sdf.agg({snapshotDate: 'max'}).first()[0]
    dates = sqlContext.sql("select distinct explode(sequence(to_date('" + minDate + "'), to_date('" + maxDate + "'), interval " + str(interval) + " month)) as snapshotDate")
    joined = F.broadcast(dates).join(sdf.withColumn('____joined____', F.lit(1)), [snapshotDate], how='inner')
  else:
    joined = sdf.withColumn('____joined____', F.lit(1))

  cnt = joined.drop('____joined____').withColumn(snapshotDate, F.date_format(snapshotDate, dateFormat)).withColumn('__cntall__', F.lit(1)).groupBy(snapshotDate).agg(*(F.count(F.col(c)).alias(c) for c in cols))
  pct = cnt.select(*[((F.col(field.name))/(F.col('__cntall__'))).name(field.name) if str(field.dataType) in allowed_types else F.col(field.name) for field in cnt.schema.fields])
  
  if pct.select('__cntall__').rdd.flatMap(lambda x:x).collect()[0] <= 1:
    return pct
  else:
    allowed_types = ['DoubleType()', 'FloatType()', 'LongType()', 'IntegerType()', 'DecimalType()']
    pct = cnt.select(*[((F.col(field.name))/(F.col('__cntall__'))).name(field.name) if str(field.dataType) in allowed_types else F.col(field.name) for field in cnt.schema.fields])
    return pct

def formatReport(sdf, snapshotDate):
  """
  .. Vivienne check! ..
  Runs in ~? min
      
  Parameters
  ----------
  sdf: spark dataframe
  snapshotDate: Vivienne

  Returns
  ----------
  spark dataframe ....
  
  """
  res = sdf.drop('__cntall__').toPandas().set_index(snapshotDate).sort_index().T

  fmt = dict.fromkeys(res.keys(), '{:.1%}')

  res = res.style.apply(bg, axis=None).applymap(lambda x: 'color: %s' % fg(x)).format(fmt).set_table_attributes('style="border-collapse:collapse"').set_properties(**{'text-align': 'right', 'font-size': '9pt'}).set_table_styles([{'selector': 'th', 'props': [('font-size', '9pt')]}, {'selector': 'tbody tr th', 'props': [('text-align', 'right')]}, {'selector': 'thead tr th', 'props': [('text-align', 'right')]}, {'selector': 'th', 'props': [('text-align', 'center')]}])
    
  return res

def bg(s, m=0, M=1, cmap='RdYlGn', low=0, high=0.2):
  """
  Written by Vivienne, changed by Kevin Aritonang
  """
  
  m = m if m is not None else s.min().min()
  M = M if M is not None else s.max().max()

  rng = M - m
  norm = colors2.Normalize(m - (rng * low),
                          M + (rng * high))
  
  normed = s.apply(lambda x: norm(x.values))
  
  try:
    cm = plt.cm.get_cmap(cmap).copy()
  except:
    cm = plt.cm.get_cmap(cmap) 
  
  cm.set_over(rgb2hex(187, 190, 195))
  c = normed.applymap(lambda x: colors2.rgb2hex(cm(x)))
  
  return c.applymap(lambda x: 'background-color: %s' % x)

def fg(x):
  """
  Sets color scheme, Vivienne?
  """
  color = 'white' if x < 0.25 else 'black'
  color = color if x<=1 else rgb2hex(187, 190, 195)
  return color

def rgb2hex(r,g,b):
  """
  Sets color scheme, Vivienne?
  """
  return "#{:02x}{:02x}{:02x}".format(r,g,b)

import pandas as pd

def higher_equal_lower(pdf,pair,drop_na=False):
  """
  Computes the sign of the difference between pairs of variables
  
  Input
  -----
  pdf: pandas dataframe
  pair: list of lists of strings, variables that need to be compared (example input comparing A=B and B=C: [['A','B'], ['B','C']]
  drop_na: boolean, whether NaNs should be dropped
  
  Returns
  -------
  pdf: pandas dataframe, with absolute and relative count of lower, higher and equal or na
  """
  strings = []
  higher = []
  zero = []
  lower = []
  equal = []
  nan = []
   
  # Compare variables  
  for i in range(len(pair)):
      strings.append(pair[i][0] + ' - ' + pair[i][1])
      large = pdf[pair[i][0]]
      small = pdf[pair[i][1]]
      higher.append((large > small).astype(int).sum())
      lower.append((large < small).astype(int).sum())
      equal.append((large == small).astype(int).sum())
  
  # Compute relative amounts
  if drop_na:
    n = [max(higher[i]+lower[i]+equal[i],1) for i in range(len(strings))]
    r_higher = [higher[i]/n[i] for i in range(len(strings))]
    r_lower = [lower[i]/n[i] for i in range(len(strings))]
    r_equal = [equal[i]/n[i] for i in range(len(strings))]
    d = {'Higher': higher, 'Lower': lower, 'Equal': equal,
         'Higher fraction': r_higher, 'Lower fraction': r_lower, 'Equal fraction': r_equal}
  else:
    n = len(pdf)
    nan = [n-higher[i]-lower[i]-equal[i] for i in range(len(strings))]
    r_higher = [x/n for x in higher]
    r_lower = [x/n for x in lower]
    r_equal = [x/n for x in equal]
    r_nan = [x/n for x in nan]
    d = {'Higher': higher, 'Lower': lower, 'Equal': equal,
         'NaN': nan, 'Higher fraction': r_higher, 'Lower fraction': r_lower, 'Equal fraction': r_equal, 'NaN fraction': r_nan, }
  
  return pd.DataFrame(data = d, index=strings)

from functions.data_quality.dq_representativeness import *
from functions.data_engineering.convert_data import *
from pyspark.sql import functions as F
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from functions.plotting import joypy
import statistics

def psi(pdf1, pdf2, col, buckets = 10, buckettype = 'bins', dp = 2):  
  """
  Calculate the PSI for a single numeric variable
        Input
        _____
           pdf1: pandas data frame
           pdf2: pandas data frame, same size as pdf1
           col: name of numeric column
           buckets: number of percentile ranges to bucket the values into
           buckettype : bucketing type, 'bins' or 'quantiles'
           dp: number of decimal places
        Returns
        _____
           psi_value: integer PSI value
  """
    
  import warnings

  pdf1_array = pdf1[[col]].dropna().to_numpy()
  pdf2_array = pdf2[[col]].dropna().to_numpy()

  def scale_range (input, min, max):
      input += -(np.min(input))
      input /= np.max(input) / (max - min)
      input += min
      return input

  breakpoints = np.arange(0, buckets + 1) / (buckets) * 100

  if buckettype == 'bins':
      breakpoints = scale_range(breakpoints, np.min(pdf1_array), np.max(pdf1_array))
  elif buckettype == 'quantiles':
      breakpoints = np.stack([np.percentile(pdf1_array, b) for b in breakpoints])

  pdf1_percents = np.histogram(pdf1_array, breakpoints)[0] / len(pdf1_array)
  pdf2_percents = np.histogram(pdf2_array, breakpoints)[0] / len(pdf2_array)

  def sub_psi(e_perc, a_perc):
      '''Calculate the pdf2 PSI value from comparing the values.
         Update the pdf2 value to a very small number if equal to zero
      '''
      if a_perc == 0:
          warnings.warn(f"{col}")
          a_perc = 0.0001
      if e_perc == 0:
          warnings.warn(f"{col}")
          e_perc = 0.0001

      value = (e_perc - a_perc) * np.log(e_perc / a_perc)
      return(value)

  psi_value = np.sum(sub_psi(pdf1_percents[i], pdf2_percents[i]) for i in range(0, len(pdf1_percents)))

  return(round(psi_value*100,dp))
      
            
      
def calculate_psi(pdf1, pdf2, cols, buckets = 10, buckettype = 'bins', label = 'PSI', dp = 2):
  
  """
  Calculate the PSI for all columns in cols (numeric only)
        Input
        _____
           pdf1: pandas data frame
           pdf2: pandas data frame, same size as pdf1
           cols: list of numeric column names
           buckets: number of percentile ranges to bucket the values into
           buckettype : bucketing type, 'bins' or 'quantiles'
           labels: Name of the PSI column
           dp: number of decimal places
        Returns
        _____
           psi_value: Pandas table with PSI value for each column in cols
  """ 
  
  df = pd.DataFrame(index = cols)
  
  psi_list = []
  
  for col in cols:
    if (len(pdf1[col].dropna())==0) | (len(pdf2[col].dropna())==0):
        psi_list.append('NA')
    else:
      psi_list.append(psi(pdf1, pdf2, col, buckets = buckets, buckettype = buckettype, dp = dp))
    
  df[label] = psi_list
  
  return df



def psi_comparison_wrapper(pdf1, cols, snapshotcol, method = 'year_on_year', buckets = 10, buckettype = 'bins', dp = 2):
  
  """
  Computes PSI for each column in cols over years defined by a chosen method. (numeric only)
        Input
        _____
           pdf1: pandas data frame
           cols: list of numeric column names
           snapshotcol : name of snapshot column
           method : 'year_on_year' for a year on year PSI comparison. 'end_year' to compute PSI of every year compared with end year.
           buckets: number of percentile ranges to bucket the values into
           buckettype : bucketing type, 'bins' or 'quantiles'
           dp: number of decimal places
        Returns
        _____
           psi_value: One Pandas table with PSI value for each column and year (defined by method) in cols
  """   
  
  years = list(np.sort(pdf1[snapshotcol].dt.year.unique()))
  
  if method == 'year_on_year':
    
    results = {}
    
    for i, year in enumerate(years):
      
      if i < len(years)-1:
        
        results[f'{i}'] = calculate_psi(pdf1[pdf1[snapshotcol].dt.year == year],
                                        pdf1[pdf1[snapshotcol].dt.year == years[i+1]],
                                        cols,
                                        label = f'{str(year)} vs {str(years[i+1])}',
                                        buckets = buckets, buckettype = buckettype, dp = dp)       
      else:
        pass
  
  elif method == 'end_year':
    
    results = {}
    
    end_year = max(years)
    
    for i, year in enumerate(years):
      
      if year != end_year:
        
        results[f'{i}'] = calculate_psi(pdf1[pdf1[snapshotcol].dt.year == year],
                                        pdf1[pdf1[snapshotcol].dt.year == end_year],
                                        cols,
                                        label = f'{str(year)} vs {str(end_year)}',
                                        buckets = buckets, buckettype = buckettype, dp = dp)        
      else:
        pass

  return pd.concat(results.values(), axis = 1)


def psi_cat(pdf1, pdf2, col, dp = 2, return_psi_per_cat = False):
  
  """
  Calculate the PSI for a single categorical variable
        Input
        _____
           pdf1: pandas data frame
           pdf2: pandas data frame, same size as pdf1
           col: name of categorical column
           dp: number of decimal places
        Returns
        _____
           psi_value: calculated PSI value
  """
    
  import warnings

  pdf1_array = pdf1[[col]].dropna().to_numpy()
  pdf2_array = pdf2[[col]].dropna().to_numpy()

  pdf1_unique = np.unique(pdf1_array,return_counts=True)  
  pdf1_categories = list(pdf1_unique[0])
  pdf1_values = list(pdf1_unique[1])
  
  pdf2_unique = np.unique(pdf2_array,return_counts=True)  
  pdf2_categories = list(pdf2_unique[0])
  pdf2_values = list(pdf2_unique[1])
  
  missing_1 = list(set(pdf1_categories).difference(pdf2_categories)) 
  missing_2 = list(set(pdf2_categories).difference(pdf1_categories)) 
  
  #Account for cases where a category is in pdf1 but not in pdf2 or vice verca (leading to different size arrays)
  for val in missing_1:
    idx = pdf1_categories.index(val)
    pdf2_values.insert(idx, 0)
    pdf2_categories.insert(idx, val)
      
  for val in missing_2:
    idx = pdf2_categories.index(val)
    pdf1_values.insert(idx, 0)
    pdf1_categories.insert(idx, val)

  pdf1_percents = np.array(pdf1_values)/len(pdf1_array)
  pdf2_percents = np.array(pdf2_values)/len(pdf2_array)
    
  def sub_psi(e_perc, a_perc):
      '''Calculate the pdf2 PSI value from comparing the values.
         Update the pdf2 value to a very small number if equal to zero
      '''
      
      if a_perc == 0:
          warnings.warn(f"{col}")
          a_perc = 0.0001
      if e_perc == 0:
          warnings.warn(f"{col}")
          e_perc = 0.0001

      value = (e_perc - a_perc) * np.log(e_perc / a_perc)
      return(value)
    
  psi_value_per_cat = [sub_psi(pdf1_percents[i], pdf2_percents[i]) for i in range(0, len(pdf1_percents))]

  if return_psi_per_cat == True:
    return pdf1_categories, [round(x*100, dp) for x in psi_value_per_cat]
  else:
    return round(np.sum(psi_value_per_cat)*100,dp)
      
def calculate_psi_cat(pdf1, pdf2, cols, label = 'PSI', dp = 2):
  
  """
  Calculate the PSI for all columns in cols (categorical only)
        Input
        _____
           pdf1: pandas data frame
           pdf2: pandas data frame, same size as pdf1
           cols: list of categorical column names
           labels: Name of the PSI column
           dp: number of decimal places
        Returns
        _____
           psi_value: One pandas table with PSI value for each column in cols
  """ 
  
  df = pd.DataFrame(index = cols)

  psi_list = []

  for col in cols:
    if (len(pdf1[col].dropna())==0) | (len(pdf2[col].dropna())==0):
      psi_list.append('NA')
    else:
      psi_list.append(psi_cat(pdf1, pdf2, col, dp = dp))

  df[label] = psi_list

  return df
  
  
def psi_cat_comparison_wrapper(pdf1, cols, snapshotcol, method = 'year_on_year', dp = 2):
  """
  Computes PSI for each column in cols over years defined by a chosen method. (categorical only)
        Input
        _____
           pdf1: pandas data frame
           cols: list of categorical column names
           snapshotcol : name of snapshot column
           method : 'year_on_year' for a year on year PSI comparison. 'end_year' to compute PSI of every year compared with end year.
           dp: number of decimal places
        Returns
        _____
           psi_value: One pandas table with PSI value for each column and year (defined by method) in cols
  """ 
  
  years = list(np.sort(pdf1[snapshotcol].dt.year.unique()))
  
  if method == 'year_on_year':
    
    results = {}
    
    for i, year in enumerate(years):
      
      if i < len(years)-1:
        
        results[f'{i}'] = calculate_psi_cat(pdf1[pdf1[snapshotcol].dt.year == year],
                                            pdf1[pdf1[snapshotcol].dt.year == years[i+1]],
                                            cols,
                                            label = f'{str(year)} vs {str(years[i+1])}', dp = dp)        
      else:
        pass
  
  elif method == 'end_year':
    
    results = {}
    
    end_year = max(years)
    
    for i, year in enumerate(years):
      
      if year != end_year:
        
        results[f'{i}'] = calculate_psi_cat(pdf1[pdf1[snapshotcol].dt.year == year],
                                            pdf1[pdf1[snapshotcol].dt.year == end_year],
                                            cols,
                                            label = f'{str(year)} vs {str(end_year)}', dp = dp)        
      else:
        pass

  return pd.concat(results.values(), axis = 1)
    
      
    
def plot_yearly_distribution(pdf, cols, snapshotcol, percentiles=[0.05, 0.95], figsize = (20,5)):
  """
  Plots a comparison of the distributions over each year for each column in cols.
      
  Input
  -----
  pdf: pandas dataframe
  cols: list of columns 
  snapshotcol : name of snapshot column
  percentiles: list, optional, list containing percentiles to be removed: [p1, p2]
  figsize: tuple defining size of figure

  Returns
  -----
  One figure for each numerical variable in pdf
  
  """ 
  years = list(np.sort(pdf[snapshotcol].dt.year.unique()))
  
  for col in cols:
    
    results = {}
    
    medians = []
    
    for year in years:
    
      pdf_tmp = pdf[pdf[snapshotcol].dt.year==year][[col]].dropna()
      
      medians.append(pdf_tmp[col].quantile(0.5))
      
      pdf_tmp = pdf_tmp[(pdf_tmp[col]>pdf_tmp[col].quantile(percentiles[0])) & (pdf_tmp[col]<pdf_tmp[col].quantile(percentiles[1]))][col]
      
      results[year] = pdf_tmp
      
    data = [np.array(df) for df in results.values()]
  
    try:
      fig, axes = joypy.joyplot(data,  labels = [str(year) for year in years],
                              title = col, figsize = figsize, fill = True, linewidth = 1)
      
      for i in range(len(medians)): 
        ymin = 0
        median = medians[i]
        yval = axes[i].lines[1].get_ydata().max()
        axes[i].plot([median,median], [ymin, yval], color="red", linewidth = 2, zorder=200)
    except:
      pass
 
        
  pass


def plot_yearly_share_per_cat(pdf, cols, snapshotcol, rotation = 0):
  """
  Plots the percentage share in each group per year for every column in cols. 
  
  Inputs
  ______
  pdf : pandas dataframe
  cols : list of columns
  snapshotcol : name of snapshot column
  
  Returns
  ______
  One plot per column in cols
  """
  
  for col in cols:
    
    if pdf[col].nunique() > 20:
      print(col, 'was skipped due to having more than 20 categories.')
      
    else:
      pdf_not_na = pdf[~pdf[col].isna()].copy()

      years = list(str(x) for x in np.sort(pdf_not_na[snapshotcol].dt.year.unique()))

      pdf_tmp = 100*pdf_not_na.groupby([pdf_not_na[snapshotcol].dt.year, col])[[col]].count()/pdf_not_na.groupby([pdf_not_na[snapshotcol].dt.year])[[col]].count()

      pdf_tmp = pdf_tmp.unstack()

      pdf_tmp.columns = pdf_tmp.columns.droplevel()

      fig, ax = plt.subplots()    
      pdf_tmp.plot(kind = 'bar', stacked = True, ax = ax)
      ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
      ax.set_title(col)
      ax.set_xticklabels(years, rotation = rotation)
      ax.set_ylabel('% Share in each group')
      ax.set_xlabel('Year')

      width = ax.patches[0].get_width()
      stacks = len(ax.patches)//len(years)

      for i in range(stacks):
        for j in range(0, len(years) - 1):
          h0 = np.sum([ax.patches[j + len(years) * k].get_height() for k in range(0, i + 1)])
          h1 = np.sum([ax.patches[j + 1 + len(years) * k].get_height() for k in range(0, i + 1)])
          ax.plot([j + width / 2, j + 1 - width / 2], [h0, h1], color='C7', ls='--', zorder=1, linewidth = 1)
        
  pass



def plot_pct_in_bucket_psi_cat(pdf1, pdf2, cols, snapshotcol, label1 = None, label2 = None):
  """
  Plots the percentage count within each bucket and includes line
  showing the contribution to the PSI per category. 
  
  Compares pdf1 and pdf2 for columns in cols. 
  
  Input
  _____
  pdf1: pandas dataframe
  pdf2: pandas dataframe
  cols: list of str, categorical columns in pdf
  snapshotcol: str, snapshot column in pdf
  label_ref: str, label for pdf1
  label_com: str, label for pdf2

  Returns
  -------
  figure with PSI bucket for each column in cols
  
  """  
  # Create label if this does not exist
  if label1 is None:
    label1 = 'pdf1'
  if label2 is None:
    label2 = 'pdf2'
  
  for c in cols:
    
    if pdf1[c].nunique() > 20:
      print(c, 'was skipped due to having more than 20 categories.')
    
    else:
      # Compute PSI
      psi = psi_cat(pdf1, pdf2, c, dp = 2, return_psi_per_cat = False)
      categories, psi_per_cat = psi_cat(pdf1, pdf2, c, dp = 4, return_psi_per_cat = True)
      labels = categories
      x = np.arange(len(labels))
      pct1 = 100*pdf1.groupby(c)[[c]].count()/len(pdf1)
      pct2 = 100*pdf2.groupby(c)[[c]].count()/len(pdf2)
      tmp = pct1.join(pct2, lsuffix = '_1', rsuffix = '_2', how = 'outer')
      tmp = tmp.fillna(0)

      width = 0.35  # the width of the bars

      fig, ax1 = plt.subplots()
      rects1 = ax1.bar(x - width/2, tmp[c + '_1'], width, label = label1)
      rects2 = ax1.bar(x + width/2, tmp[c + '_2'], width, label = label2)
      ax2 = ax1.twinx()
      rects3 = ax2.plot(x, psi_per_cat, color="#f3c000", label = "PSI contribution")

      lines, labelss = ax1.get_legend_handles_labels()
      lines2, labels2 = ax2.get_legend_handles_labels()
      ax2.legend(lines + lines2, labelss + labels2, bbox_to_anchor=(1.15, 1.02), loc="upper left")
      ax1.set_ylabel('% count')
      ax1.set_xlabel(c)
      ax1.set_xticks(x)
      ax1.set_xticklabels(labels)
      ax2.set_ylabel("% PSI contribution")
      ax1.set_title(f'PSI = {psi}')

  pass


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def count_obs_per_moment(pdf):
  """
  Plots an area plot of the number of observations per moment in each date column
      
  Input
  -----
  pdf: pandas dataframe
  
  Returns
  -----
  One figure for each datetime variable in pdf
  """

  df_date = pdf.select_dtypes(include=['datetime'])

  for col in df_date.columns:
    
    if len(df_date.groupby(col)[col].count())>1:

      df_group = df_date.groupby(col)[col].count().sort_index()

      fig, ax = plt.subplots()      
      ax.fill_between(df_group.index.to_numpy(), df_group.to_numpy())      
      ax.set_xlabel('Year')
      ax.set_ylabel('count')
      ax.set_title(col)
  
  pass

def snapshotdate_difference(pdf, snapshotcol, delta = 'days', rounding=True):
  """
  Computes the difference between dates in the dataframe compared to the snapshot date.
  
  Input
  _____
  pdf: pandas dataframe
  snapshotcol: str, column with snapshot dates in pdf
  delta: str in ['days','months','years'], output time measure
  rounding:, bool, whether the values are rounded

  Returns
  ------
  pdf: pandas dataframe, containing the difference in dates compared to the snapshot date for all date columns
  """  
  
  # Select date columns
  df_date = pdf.select_dtypes(include=['datetime'])
  diff_cols = [] 
  
  # Select frequency
  if delta == 'days':
    d = 1
  elif delta == 'months':
    d = 30.4368499
  elif delta == 'years':
    d= 365.242199
  
  # Compute difference in days between snapshot date and other dates
  for col in df_date.columns:
    if col != snapshotcol and len(df_date.groupby(col)[col].count()) > 1:                          
      col_name = f"{snapshotcol} - {col}"
      diff_cols.append(col_name)
      pdf[col_name] = ((pdf[snapshotcol] - pdf[col]).dt.days / d)                       
  if rounding:
    pdf[diff_cols].round()
    
  return pdf[diff_cols]


def outdated_information(pdf, date_col_1, date_col_2):
  
  """
  Returns table with information on the timeliness between date_col_1 and date_col_2
  
  Input
  _____
  pdf : Pandas dataframe
  date_col_1 : name of date column
  date_col_2 : name of date column
  
  Returns
  _____
  pandas table with timeliness information
  """
  
  if date_col_1 not in pdf.columns or date_col_2 not in pdf.columns:
    pass
  
  else:
    pdf_tmp = pdf.copy()

    pdf_tmp['days'] = (pdf_tmp[date_col_1] - pdf_tmp[date_col_2]).dt.days

    conditions = [
      pdf_tmp['days']<0,
      (pdf_tmp['days']>=0) & (pdf_tmp['days']<=366),
      (pdf_tmp['days']>366) & (pdf_tmp['days']<=731),
      (pdf_tmp['days']>731) & (pdf_tmp['days']<=1096),
       pdf_tmp['days']>1096
    ]

    labels = [
      'Less than 0 years old',
      'Between 0 and 1 years old',
      'Between 1 and 2 years old',
      'Between 2 and 3 years old',
      'More than 3 years old'
    ]

    pdf_tmp['Outdated'] = np.select(conditions, labels, default = 'NA')

    df = pdf_tmp.groupby('Outdated')['Outdated'].agg([lambda c : c.count(), lambda c : round(100*c.count()/len(pdf_tmp),2)])

    return df.reindex(labels + ['NA']).rename(columns = {'<lambda_0>':'Observations', '<lambda_1>':'% Observations'})


def plot_outdated_over_time(pdf, date_col_1, date_col_2, x_axis_col, threshold_days = 731):
  """
  Returns plot with information overtime on the timeliness between date_col_1 and date_col_2
  
  Input
  _____
  pdf : Pandas dataframe
  date_col_1 : name of date column
  date_col_2 : name of date column
  x_axis_col: Name of x_axis_col. Choose between date_col_1 and date_col_2
  threshold_days : Threshold for number of days to be considered valid/outdated
  
  Returns
  _____
  single plot
  """
  
  if date_col_1 not in pdf.columns or date_col_2 not in pdf.columns:
    pass
  
  else:
    pdf_tmp = pdf.copy()

    pdf_tmp['days'] = (pdf_tmp[date_col_1] - pdf_tmp[date_col_2]).dt.days

    conditions = [
      pdf_tmp['days']>threshold_days,
      (pdf_tmp['days']>=0) & (pdf_tmp['days']<=threshold_days),
      pdf_tmp['days']<0
    ]

    labels = [
      'Outdated',
      'Valid',
      'Other'
    ]

    pdf_tmp['Timeliness'] = np.select(conditions, labels, default = 'NA')

    df = pd.crosstab(index = pdf_tmp[x_axis_col], columns = pdf_tmp['Timeliness'], normalize = 0)*100

    df.plot()
    plt.ylabel('% Observations')
    plt.xlabel(x_axis_col)
    plt.legend()
    plt.ylim(0,100)

    pass
  
  
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools

def find_duplicate_rows(pdf, cols, return_pdf = False):  
  """
  Finds duplicate rows on the combination of variables specified in 'cols'
      
  Input
  _____
  pdf: pandas dataframe    
  cols: list, list of variables to take into account for duplicates
  return_pdf : Set true to return pdf containing each duplicate row. 

  Returns
  _____
  pandas dataframe containing duplicate rows
  
  """
  
  selected_data = pdf[cols]
  
  pdf_tmp = selected_data[selected_data.astype(str).duplicated()==1]
  
  print(f'With columns {str(cols)}, there are {len(pdf_tmp)} duplicate rows.')
  
  if return_pdf == True:
    return pdf_tmp
  else:
    pass

  
  
def count_data(pdf, cols, distinct = False):
  
  """
  Counts rows of data, with option of counting unique rows. 
  
  Input
  _____
  pdf: pandas dataframe    
  cols: list, list of variables to take into account for counting or None
  distinct: If True, returns distinct count

  Returns
  _____
  printed information
  
  """
  
  if not cols:    
    pdf_tmp = pdf.copy()    
  else:    
    pdf_tmp = pdf.copy(cols)    
  if not distinct:    
    print(f'Count = {len(pdf_tmp)}')    
  else:    
      print(f'Distinct Count = {len(pdf_tmp.astype(str).drop_duplicates())} with input cols {str(cols)}')
    
  pass



def one_to_one_corespondence(pdf, cols, detail=False):
  """
  Prints variables with one-to-one correspondence.
  
  Input
  _____
  pdf: pandas dataframe
  cols: columns to check for one-to-one correspondence
  detail: show detailed information regarding one-to-one correspondence
  
  Returns
  ______
  Printed information
  """
  
  # Create pairs of all cols
  pairs = list(itertools.combinations(cols, 2))
  oto_pairs = []

  for pair in pairs:
    if pair[0] in pdf.columns and pair[1] in pdf.columns:
      # Map elements to each other
      pdf_pair0 = pdf.astype(str).groupby([pair[0]])[pair[1]].nunique()
      pdf_pair1 = pdf.astype(str).groupby([pair[1]])[pair[0]].nunique()

      # Check for one-to-one correspondance
      if pdf_pair0.max() == 1 and pdf_pair1.max() == 1:
        oto_pairs.append(1)
      else:
        oto_pairs.append(0)

      # Print detailed information
      if detail:
        print(f"There are {pdf_pair0.loc[pdf_pair0>1].count()} {pair[0]}s that match to more than one {pair[1]}. \n")
        print(f"There are {pdf_pair1.loc[pdf_pair1>1].count()} {pair[1]}s that match to more than one {pair[0]}. \n")

  # Print pairs with one-to-one correspondance
  for i in range(len(oto_pairs)):
    if oto_pairs[i]:
      print(f"The variables {pairs[i]} have one-to-one correspondance.")
  
  
  pass

from pyspark.sql import functions as F
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def large_value_counts(pdf, cols, pct=0.01, max_n="None", drop_na=True, div_distinct=False):
  """
  Summarises the largest value counts in a dataframe by column.
  Runs in ~3 min
      
  Parameters
  ----------
  pdf: pandas dataframe
  cols: list of str, columns to look for value counts
  pct: double, minimum percentage of value counts to occur in the list
  max_n: integer, maximum number of values per column
  drop_na: boolean, whether to include NaN in the value counts
  div_distinct: boolean, whether to divide the percentage of value counts by the number of distinct values
  
  Returns
  ----------
  pdf: pandas dataframe, containing normalised value counts per value in each column
  
  """
  series_list = []
  series_keys = []
  
  for col in cols:
    
    # Scaling factor for distinct
    if div_distinct:
      dist = pdf[col].nunique(dropna=drop_na)
      dist = max(dist, 1)
    else:
      dist = 1
    
    # Get n highest values
    if max_n == "None":
      pdf_tmp = pdf[col].value_counts(dropna=drop_na).to_frame(name='Count')
    else:
      pdf_tmp = pdf[col].value_counts(dropna=drop_na).head(max_n).to_frame(name='Count')
      
    # Normalise
    if drop_na:
      pdf_tmp['Count fraction'] = pdf_tmp['Count']/(pdf[col].count())
    else:  
      pdf_tmp['Count fraction'] = pdf_tmp['Count']/len(pdf[col])
    
    # Get values exceeding percentage
    pdf_tmp = pdf_tmp.loc[pdf_tmp['Count fraction'] > (pct/dist)]

    # Store values
    if len(pdf_tmp) > 0:
      series_list.append(pdf_tmp)
      series_keys.append(col)
    
  # Concatenate dataframes
  if len(series_list) > 0:
    pdf = pd.concat(series_list, keys=series_keys)
  else:
    pdf = pd.DataFrame({"Empty": []})
  return pdf

def dummy_count(pdf, cols, dummy_values, return_all = False, include_nas = True):
  """
  Computes the number and percentage of dummy value occurences
  
  Parameters
  ----------
  pdf: pandas dataframe
  cols: list of str, columns for which outliers needs to be found in kdf
  dummy_values : list of dummy values
  return_all: If False, returns only results for dummy values where count is greater than 0
  include_nas: If False, the percentage is calculated using total non null values for that column, rather than the length of pdf. 
  
  Returns
  ----------
  pdf: pandas dataframe
  """
  cols_index = np.repeat(cols,len(dummy_values))
  
  dummy_values_index = dummy_values*len(cols)
  df = pd.DataFrame(index = [cols_index, dummy_values_index])
  
  count = []
  pct = []
   
  for col in cols:
    if include_nas == False:
      total = len(pdf[~pdf[col].isna()])     
    else:
      total = len(pdf)
      
    for d in dummy_values:
      if total == 0:
        count.append(len(pdf[pdf[col]==d]))
        pct.append('N/A (no non-null values)')
      else:
        count.append(len(pdf[pdf[col]==d]))
        pct.append(round(100*len(pdf[pdf[col]==d])/total,2))
  
  df['Count'] = count
  df['%'] = pct
  
  df = df.rename_axis(('Column Names','Dummy Values'))
  
  if return_all == False:
    return df[df['Count']!=0]
  else:
    return df

  
def check_bounds(pdf, dct, include_nas = True):
  """
  Computes the number of exceedances of lower and upper bounds.
  
  Parameters
  ----------
  pdf: pandas dataframe
  dct: dictionary with the column names as keys and a list of upper and lower bounds as values. eg. dct = {'column1' : [0,100]}
  include_nas: If False, the percentage is calculated using total non null values for that column, rather than the length of pdf. 
  
  Returns
  ----------
  pdf: pandas dataframe, with exceedances of lower and upper bounds in absolute and relative terms
  """
  
  columns_to_check = set(dct.keys()).intersection(pdf.columns)

  df = pd.DataFrame(index = columns_to_check)
  df['Lower Bound (LB)'] = [dct[x][0] for x in columns_to_check]
  df['Upper Bound (UB)'] = [dct[x][1] for x in columns_to_check]

  lb = []
  ub = []
  lb_pct = []
  ub_pct = []

  for col in columns_to_check:

    if include_nas == False:
      total = len(pdf[~pdf[col].isna()])
    else:
      total = len(pdf)

    lb.append(len(pdf[pdf[col]<dct[col][0]]))
    ub.append(len(pdf[pdf[col]>dct[col][1]]))
    lb_pct.append(round(100*len(pdf[pdf[col]<dct[col][0]])/total,2))
    ub_pct.append(round(100*len(pdf[pdf[col]>dct[col][1]])/total,2))

  df['Under LB'] = lb
  df['Over UB'] = ub
  df['Under LB %'] = lb_pct
  df['Over UB %'] = ub_pct

  return df[['Lower Bound (LB)', 'Under LB', 'Under LB %', 'Upper Bound (UB)', 'Over UB', 'Over UB %']]
