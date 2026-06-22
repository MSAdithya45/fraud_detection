import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Raw psycopg2 connection against Supabase PostgreSQL.
# (Kept for parity with the previous raw mysql.connector helper.)
conn = psycopg2.connect(os.getenv("DATABASE_URL"))

cursor = conn.cursor()
