# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "7315d09d-4de8-4f03-bad5-02e5bca9b8e0",
# META       "default_lakehouse_name": "Lakehouse1",
# META       "default_lakehouse_workspace_id": "b5b2f2c8-ac06-44be-8ef7-527fcab135a1",
# META       "known_lakehouses": [
# META         {
# META           "id": "7315d09d-4de8-4f03-bad5-02e5bca9b8e0"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# Welcome to your new notebook
# Type here in the cell editor to add code!
df = spark.sql("select * from DT_DIM_CUSTOMER")
display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
