import pandas as pd
import numpy as np
from config.pseudonymisation import pseudonymize
from extraction import extract

df = extract('data/row.csv')

def duplicate_data():
    global df
    df = df.drop_duplicates()

def text_cleaning():
    global df
    cols = ['Customer Name', 'City', 'State', 'Region', 'Category', 'Segment', 'Sub-Category', 'Product Name',
            'Product ID']
    df.loc[:, cols] = df[cols].apply(lambda x: x.str.strip().str.lower())

    # ====== Segment ======
    corr = {
        'consumerr': 'consumer',
        'home ofice': 'home office',
    }
    df.loc[:, "Segment"] = df['Segment'].replace(corr)

def data_types_parsing():
    global df
    # ====== Date ======
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format="mixed")

    # ====== Category, Segment, Sub-Category ======
    cols = ['Category', 'Segment', 'Sub-Category']
    df = df.astype({col: 'category' for col in cols})

def impossible_and_suspicious_values():
    global df
    # ====== Quantity ======
    df = df.drop(df[df['Quantity'] < 0].index)  # msaht tout les line li quntity dyalhom < 0
    # ====== Discount ======
    df = df.drop(df[df['Discount'] > 1].index)
    # ====== Profit ======
    df = df.drop(columns=['Profit']) # msaht column dyal profit ga3

def imputation():
    global df
    # ====== Date ======
    mask_correct_date = df['Ship Date'] >= df['Order Date']
    ship_duration_mean = (df[mask_correct_date]['Ship Date'] - df[mask_correct_date][
        'Order Date']).dt.days.mean()  # calculer la moyean de period enntre date de commander et le date de délivrer

    # 1 remplire le NaT valeurs de Ship Date
    df['Ship Date'] = df['Ship Date'].fillna(df['Order Date'] + pd.DateOffset(days=ship_duration_mean))

    #  2 corriger le dates problem de Ship Date < Order Date
    mask_incorrect_date = df['Ship Date'] < df['Order Date']
    df.loc[mask_incorrect_date, 'Ship Date'] = df[mask_incorrect_date]['Order Date'] + pd.DateOffset(
        days=ship_duration_mean)  # hitach lifihom shiped date < man date order colhom fihom value de "2010-01-01" donc ghir problem de data ghadi n3taber date Order correct et nzid 3lih mean de duration

    df['ship_duration'] = (df['Ship Date'] - df[
        'Order Date']).dt.days  # calculer la period enntre date de commander et le date de délivrer

    # ====== Ship Mode ======
    # sns.scatterplot(data=df, x="Ship Mode", y="ship_duration")
    # plt.show()
    # print(df['Ship Mode'].value_counts())

    conditions = [
        (df['ship_duration'] >= 0) & (df['ship_duration'] <= 1),
        (df['ship_duration'] >= 1) & (df['ship_duration'] <= 4),
        (df['ship_duration'] >= 4) & (df['ship_duration'] <= 5),
    ]

    choices = [
        "Same Day",
        "First Class",
        "Second Class"
    ]

    df['Ship Mode'] = df['Ship Mode'].fillna(
        pd.Series(np.select(conditions, choices, default='Standard Class'), index=df.index)
    )

    # ====== Customer Name (Dictionary Mapping) ======
    customers_names = df.dropna(subset='Customer Name').drop_duplicates('Customer ID').loc[
        :, ['Customer Name', 'Customer ID']].set_index('Customer ID')
    df['Customer Name'] = df['Customer Name'].fillna(df['Customer ID'].map(
        customers_names['Customer Name']))  # hna 3amrt ga3 les customer name avec les customer id li 3andhom names

    df = df.drop(df[df[
        'Customer Name'].isna()].index)  # hna kayn wahd customer ID unique mam3awdch walakin ma3andch Name ya3ni ma3andich mnin n3raf name donc hadi supprimih

    # ====== Quantity ======
    df['Quantity'] = df['Quantity'].fillna(df.groupby('Product Name')['Quantity'].transform('mean'))
    df = df.dropna(subset='Quantity')

    # ====== Sales ======
    df = df.drop(df[df['Sales'] == 1131924.0].index)  # had value outlier kbira bzaaf o kat3awd fa 15 lines
    df['Sales'] = df['Sales'].fillna(df.groupby('Product Name')['Sales'].transform('mean'))
    df['price'] = df['Sales'] / (df['Quantity'] * (1 - df['Discount']))  # zad column dyal
    df = df.dropna(subset='Sales')  # b9aw des valeur fihom NaN (4)

    # ====== Product ID ======
    df['Product ID'] = df.groupby('Product Name')['Product ID'].transform('first')

    # ====== Row ID ======
    df['Row ID'] = np.arange(1, df.shape[0] + 1)

    # ====== Order ID ======
    prefix = df['Order ID'].str[:2]
    year = df['Order Date'].dt.year.astype(str)
    df['Order ID'] = prefix + '-' + year + '-' + df['Row ID'].astype(str)

def structural_standardisation():
    global df
    df.columns = df.columns.str.lower().str.replace(' ', '_')

def pseudonymisation():
    global df
    df['customer_name'] = df['customer_name'].apply(pseudonymize)

def get_data_frame():
    global df
    return df