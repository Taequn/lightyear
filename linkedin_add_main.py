import flaskMain as fm
import numpy as np
import pandas as pd
from linkedinSupport.add_linkedin_column import LinkedinAdder

def add_linkedin_data():
    """
    adds linkedin urls for everyone on the haro database
    """
    
    haros = pd.read_sql_table(table_name='haros', con=fm.db.engine)
    with open("linkedinSupport/config/email.txt") as em, open("linkedinSupport/config/password.txt") as pw:
        email = em.read()
        password = pw.read()
    adder = LinkedinAdder(email, password)
    new_h = adder.add_column_haro(haros)
    new_h.to_sql(name='haros', con=fm.db.engine, index=False, if_exists='append')


def drop_old_table():
    """
    drops old table without values
    """

    haros = pd.read_sql_table(table_name='haros', con=fm.db.engine)
    haros.replace("MISSINGSENTINEL", np.nan, inplace=True)
    haros.dropna(inplace=True)
    haros.to_sql(name='haros', con=fm.db.engine, index=False, if_exists='replace')


add_linkedin_data()
drop_old_table()