
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import csv

import datetime

csv_file = "co_deaths_cause_hospice_1720ytd.csv"
pop_csv_file = "region-componentsChange_data.csv"

plot_targets = [
    'All Causes',
    # 'Unintentional injuries',
    # # 'Chronic lower respiratory diseases',
    # 'Alzheimer\'s disease',
    # # 'Suicide',
    # 'Chronic liver disease and cirrhosis',
    # 'Other diseases of respiratory system',
    # # 'Influenza and pneumonia',
    # # 'Homicide/legal intervention',
    # 'Other and unspecified infectious and parasitic diseases',
    # # 'Complications of medical and surgical care',
    # # 'Anemias',
    # # 'Cholelithiasis and other disorders of gallbladder',
    # # 'Coronavirus Disease (COVID-19)',
    # # 'Other/Underlying cause of death not yet coded by CDC'
]
to_int = lambda ls: [int(x.replace(",","").replace("*","0")) for x in ls]
to_float = lambda ls: [float(x.replace(",","")) for x in ls]

def main():
    pop_df = pd.read_csv(pop_csv_file)

    pop_by_year = pd.Series(to_float(pop_df['Population'].values), index=pop_df['Year']).to_dict()

    f = open(csv_file)
    csv_reader = csv.reader(f)
    csv_data = [row for row in csv_reader]
    f.close()

    years = csv_data[2][3:-1]

    this_year = int(years[0])
    population = []
    months = csv_data[3][3:-1]
    year_month = []

    for i in range(len(years)):
        year = years[i]
        if year != '':
            this_year = int(year.replace("(Jan-YTD)",""))
        years[i] = this_year
        population.append(pop_by_year[this_year])
        year_month.append(f'{months[i]} {this_year}')

    plot_df = pd.DataFrame()

    apr_diff = []
    for i in range(5, len(csv_data)-3):
        row = csv_data[i]
        name = row[0]
        if name == "" or name not in plot_targets:
            continue
        total = to_int(csv_data[i][3:-1])
        no_hospice = to_int(csv_data[i+1][3:-1])
        hospice = to_int(csv_data[i+2][3:-1])
        df = get_df(months, years, population, total, no_hospice, hospice, name)

        data_2020 = df.loc[df['year'] == 2020]
        data_2019 = df.loc[df['year'] == 2019]
        data_apr_2019 = data_2019.loc[data_2019['month'] == 'Apr']['total'].values
        data_apr_2020 = data_2020.loc[data_2020['month'] == 'Apr']['total'].values

        adj_apr_2019 = data_2019.loc[data_2019['month'] == 'Apr']['pop_adjust'].values
        adj_apr_2020 = data_2020.loc[data_2020['month'] == 'Apr']['pop_adjust'].values

        adj_diff = adj_apr_2020 - adj_apr_2019
        adj_diff = adj_diff[0]
        apr_diff.append([name, adj_diff])
        total_percent = (data_apr_2020 - data_apr_2019) / data_apr_2019
        total_percent = total_percent[0]
        print(name, adj_diff)
        # if abs(total_percent) > 0.1:
        if True:
            plot_df = plot_df.append(df)


    titles = {
        'pop_adjust_hospice':'Population adjusted deaths under hospice care per 100,000',
        'pop_adjust_no_hospice': 'Population adjusted deaths not under hospice care per 100,000',
        'pop_adjust':'Colorado Population Adjusted Deaths per 100,000'
    }

    for var_name in ['pop_adjust_hospice', 'pop_adjust_no_hospice', 'pop_adjust']:
        with sns.plotting_context("notebook", font_scale=0.65):
            g = sns.FacetGrid(plot_df, col='name', col_wrap=1, aspect=3, sharey=False, sharex=False, margin_titles=True, palette="deep")
            g.map(sns.barplot, 'month', var_name, 'year', palette='deep')
            g.set_titles(row_template='{row_name}', col_template='{col_name}')
            g.fig.suptitle(titles[var_name], y=1.05)
            g.add_legend()
            g.savefig(f"{var_name}.png")

    # apr_df = pd.DataFrame(apr_diff, columns=['cause', 'population adjust difference April 2020 per 100,000'])
    # with sns.plotting_context("notebook", font_scale=0.5):
    #     g = sns.barplot(x='population adjust difference April 2020 per 100,000', y='cause', data=apr_df)
    #     plt.show()
    #     # g.get_figure().savefig("apr_adj_diff.png")


def get_df(months, years, population, total, no_hospice, hospice, name):
    all_cause_df = pd.DataFrame()
    all_cause_df['month'] = months
    all_cause_df['year'] = years
    all_cause_df['population'] = population
    all_cause_df['total'] = total
    all_cause_df['no_hospice'] = no_hospice
    all_cause_df['hospice'] = hospice
    per = 100000
    all_cause_df['pop_adjust'] = (all_cause_df['total'] / all_cause_df['population']) * per
    all_cause_df['pop_adjust_no_hospice'] = (all_cause_df['no_hospice'] / all_cause_df['population']) * per
    all_cause_df['pop_adjust_hospice'] = (all_cause_df['hospice'] / all_cause_df['population']) * per
    all_cause_df['name'] = name
    _all_cause_df = all_cause_df.loc[~all_cause_df["month"].str.contains("Total")]
    return _all_cause_df

if "__main__" == __name__:
    main()
