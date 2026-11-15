import ibm_db

CONN_STR = (
    "DATABASE=UVMOVE;"
    "HOSTNAME=localhost;"
    "PORT=50000;"
    "PROTOCOL=TCPIP;"
    "UID=db2inst1;"
    "PWD=uvmove123;"
)

def get_connection():
    try:
        return ibm_db.connect(CONN_STR, "", "")
    except Exception as e:
        raise RuntimeError(f"Error conectando a IBM Db2: {ibm_db.conn_errormsg()} - {e}")
