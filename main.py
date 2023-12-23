import streamlit as st
import hydralit_components as hc
import sqlite3
import pandas as pd
from datetime import datetime
import pytz

# Database
connection = sqlite3.connect("warung_simpang_raya.db")
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("CREATE TABLE IF NOT EXISTS Pemasukan (id INTEGER PRIMARY KEY, pemasukan TEXT, uang FLOAT, tanggal_pemasukan DATE, FOREIGN KEY (tanggal_pemasukan) REFERENCES Tanggal(tanggal))")
connection.commit()

cursor.execute("CREATE TABLE IF NOT EXISTS Pengeluaran (id INTEGER PRIMARY KEY, pengeluaran TEXT, uang FLOAT, tanggal_pengeluaran DATE, FOREIGN KEY (tanggal_pengeluaran) REFERENCES Tanggal(tanggal))")
connection.commit()

cursor.execute("CREATE TABLE IF NOT EXISTS Tanggal (tanggal DATE PRIMARY KEY)")
connection.commit()

# # Tentukan zona waktu Indonesia
indonesia_timezone = pytz.timezone('Asia/Jakarta')

waktu_indonesia = datetime.now(indonesia_timezone)

format_tanggal = '%Y-%m-%d'
tanggal_str = waktu_indonesia.strftime(format_tanggal)

df_pemasukan = pd.DataFrame(columns=['Pemasukan', 'uang', 'tanggal'])
df_pengeluaran = pd.DataFrame(columns=['Pemasukan', 'uang', 'tanggal'])

option_data = [
            {'label':"Pemasukan"},
            {'label':"Pengeluaran"}
        ]
over_theme = {'txc_inactive': 'black','menu_background':'#ECF5FE','txc_active':'black','option_active':'#fafafa'}
font_fmt = {'font-class':'h2','font-size':'150%'}

op = hc.option_bar(option_definition=option_data,key='PrimaryOption',override_theme=over_theme,font_styling=font_fmt,horizontal_orientation=True)
st.markdown(f"<h2 align='center'> {op} Simpang Raya Kampir </h2>", unsafe_allow_html=True)

form_pemasukan = st.empty()

with form_pemasukan.form("Pemasukan", clear_on_submit=True):
    tanggal_inp = st.date_input(label="Tanggal Pemasukan", disabled=True)
    text_inp = st.text_area("Pemasukan")
    pemasukan_uang = st.number_input("Rp.", min_value=1000, max_value=1000000, step=200)
    submit = st.form_submit_button("Submit")

    if submit:
        try:
            get_tanggal = cursor.execute("SELECT tanggal from Tanggal WHERE tanggal= ?", (tanggal_inp,))
            get_tanggal = cursor.fetchone()

            if str(op) == "Pemasukan":
                if not get_tanggal:
                    cursor.execute("INSERT INTO Tanggal(tanggal) VALUES(?)", (tanggal_inp, ))
                    connection.commit()
                    df_pemasukan.loc[len(df_pemasukan)] = [text_inp, pemasukan_uang, tanggal_inp]
                
                cursor.execute("INSERT INTO pemasukan(pemasukan, uang, tanggal_pemasukan) VALUES(?, ?, ?)", (text_inp, pemasukan_uang, tanggal_inp))
                connection.commit()

            elif str(op) == "Pengeluaran":
                if not get_tanggal:
                    cursor.execute("INSERT INTO Tanggal(tanggal) VALUES(?)", (tanggal_inp, ))
                    connection.commit()
                    df_pengeluaran.loc[len(df_pengeluaran)] = [text_inp, pemasukan_uang, tanggal_inp]
                
                cursor.execute("INSERT INTO pengeluaran(pengeluaran, uang, tanggal_pengeluaran) VALUES(?, ?, ?)", (text_inp, pemasukan_uang, tanggal_inp))
                connection.commit()

            st.success("Data Berhasil disimpan !")
        
        except Exception as e:
            st.warning(e)

if str(op) == "Pemasukan":

    st.write("")
    st.markdown("<h3 align='center'> Data Pemasukan </h3>", unsafe_allow_html=True)

    query = f"SELECT * FROM Pemasukan WHERE tanggal_pemasukan = '{tanggal_str}'"
    df = pd.read_sql_query(query, connection)
    df_copy = df.copy()
    df['uang'] = df['uang'].map(lambda x: '{:,.0f}'.format(x).replace(',', '.'))
    st.table(df)
    st.markdown("<h5 align='right'> Total Pemasukan : Rp. {:,.2f} </h5>".format(df_copy['uang'].sum()), unsafe_allow_html=True )
    st.download_button(
        label="Unduh CSV",
        data=df.to_csv(index=False),
        file_name='dataframe.csv',
        mime='text/csv',
    )
elif str(op) == "Pengeluaran":
    query = f"SELECT * FROM Pengeluaran WHERE tanggal_pengeluaran = '{tanggal_str}'"
    st.markdown("<h4 align='center'> Data Pengeluaran </h4>", unsafe_allow_html=True)
    df = pd.read_sql_query(query, connection)
    df_copy = df.copy()
    df['uang'] = df['uang'].map(lambda x: '{:,.0f}'.format(x).replace(',', '.'))
    st.table(df)
    st.markdown("<h5 align='right'> Total Pemasukan : Rp. {:,.2f} </h5>".format(sum(df_copy['uang'])), unsafe_allow_html=True )