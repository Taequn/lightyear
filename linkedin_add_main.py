import pandas as pd
import flaskMain as fm
from linkedinSupport.add_linkedin_column import LinkedinAdder

haros = pd.read_sql_table(table_name='haros', con=fm.db.engine)
with open("linkedinSupport/config/email.txt") as em, open("linkedinSupport/config/password.txt") as pw:
    email = em.read()
    password = pw.read()
adder = LinkedinAdder(email, password)
adder.add_column_haro(haros)
haros.to_sql(name='haros', con=fm.db.engine, index=False, if_exists='replace')