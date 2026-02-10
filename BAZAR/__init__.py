import pymysql

# Le decimos a Django: "Usa PyMySQL como si fuera el cliente nativo"
pymysql.install_as_MySQLdb()