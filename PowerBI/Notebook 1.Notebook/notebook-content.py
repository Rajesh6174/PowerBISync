# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "027b6775-9b22-4a28-8877-4ce9e3c5ffe5",
# META       "default_lakehouse_name": "SalesLakehouse",
# META       "default_lakehouse_workspace_id": "b5b2f2c8-ac06-44be-8ef7-527fcab135a1"
# META     }
# META   }
# META }

# CELL ********************

# Welcome to your new notebook
# Type here in the cell editor to add code!
import sempy.fabric as fabric
import pyspark.sql.functions as F
df_datasets = fabric.list_datasets()
df_datasets

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

%pip install -U semantic-link

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import sempy.fabric as fabric
from sempy.relationships import plot_relationship_metadata

relationships = fabric.list_relationships("End-to-End Analytics with Snowflake and Power BI")
plot_relationship_metadata(relationships)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# install semantic-link-labs
%pip install semantic-link-labs

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# import package
import sempy_labs as labs
from sempy_labs import migration, directlake, admin
from sempy_labs import lakehouse as lake
from sempy_labs import report as rep
from sempy_labs.tom import connect_semantic_model
from sempy_labs.report import ReportWrapper
from sempy_labs import ConnectWarehouse
from sempy_labs import ConnectLakehouse

from pyspark.sql.functions import col, lit, udf
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType, ArrayType

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# find all semantic models
df_sem_model = spark.createDataFrame(admin.list_datasets())

df_sem_model_cleaned = df_sem_model.toDF(*(c.replace(' ', '_').lower() for c in df_sem_model.columns)) \
                .withColumn("upstream_datasets", col("upstream_datasets").cast(ArrayType(StringType()))) \
                .withColumn("users", col("users").cast(ArrayType(StringType())))

df_workspace = spark.createDataFrame(admin.list_workspaces()) \
    .withColumn("workspace_id", col("Id")) \
    .withColumn("workspace_name", col("Name")) \
    .select("workspace_id", "workspace_name")

df_sem_model_cleaned = df_sem_model_cleaned.join(df_workspace, 'workspace_id', "left") \
    .select("dataset_id", 
        "dataset_name", 
        "workspace_id", 
        "workspace_name", 
        "add_rows_api_enabled", 
        "is_refreshable", 
        "is_effective_identity_required", 
        "is_effective_identity_roles_required", 
        "target_storage_mode", 
        "created_date", 
        "content_provider_type", 
        "upstream_datasets", 
        "users", 
        "is_in_place_sharing_enabled", 
        "auto_sync_read_only_replicas", 
        "max_read_only_replicas"
    )                                       # excluded cols: create_report_embed_url, qna_embed_url, configured_by, web_url

display(df_sem_model_cleaned)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

dataframes = []

for row in df_sem_model_cleaned.collect():

    workspace_name=row['workspace_name']
    dataset_name = row['dataset_name']

    objects_pd = labs.list_semantic_model_objects(dataset=dataset_name, workspace=workspace_name)

    if len(objects_pd) == 0:
        number_of_tables = 0
        number_of_columns = 0
        number_of_hierarchies = 0

    else:
        objects = spark.createDataFrame(objects_pd)
        number_of_tables      = objects.filter("`Object Type` = 'Table' OR `Object Type` = 'Calculated Table'").count()
        number_of_columns     = objects.filter("`Object Type` = 'Column' OR `Object Type` = 'Calculated Column'").count()
        number_of_hierarchies = objects.filter("`Object Type` = 'Hierarchy'").count()
    number_of_reports     = len(labs.list_reports_using_semantic_model(dataset=dataset_name, workspace=workspace_name))

    with connect_semantic_model(dataset=dataset_name, workspace=workspace_name, readonly=True) as tom_wrapper:
        number_of_calculated_columns = len(list(tom_wrapper.all_calculated_columns()))
        number_of_calculated_tables  = len(list(tom_wrapper.all_calculated_tables()))
        number_of_measures           = len(list(tom_wrapper.all_measures()))
        has_date_table               = tom_wrapper.has_date_table()
        has_hybrid_table             = tom_wrapper.has_hybrid_table()
        has_rls                      = False if not len(list(tom_wrapper.all_rls())) else True
        is_direct_lake               = tom_wrapper.is_direct_lake()
        is_default_semantic_model    = labs.is_default_semantic_model(dataset=dataset_name, workspace=workspace_name)

    row = Row(
        workspace_name               = workspace_name, 
        dataset_name                 = dataset_name, 
        number_of_reports            = number_of_reports, 
        number_of_tables             = number_of_tables, 
        number_of_columns            = number_of_columns,
        number_of_hierarchies        = number_of_hierarchies, 
        number_of_calculated_columns = number_of_calculated_columns, 
        number_of_calculated_tables  = number_of_calculated_tables, 
        number_of_measures           = number_of_measures, 
        has_date_table               = has_date_table,
        has_hybrid_table             = has_hybrid_table,
        has_rls                      = has_rls,
        is_direct_lake               = is_direct_lake,
        is_default_semantic_model    = is_default_semantic_model
    )

    schema = StructType([
        StructField("workspace_name", StringType(), True),
        StructField("dataset_name", StringType(), True),
        StructField("number_of_reports", IntegerType(), True),
        StructField("number_of_tables", IntegerType(), True),
        StructField("number_of_columns", IntegerType(), True),
        StructField("number_of_hierarchies", IntegerType(), True),
        StructField("number_of_calculated_columns", IntegerType(), True),
        StructField("number_of_calculated_tables", IntegerType(), True),
        StructField("number_of_measures", IntegerType(), True),
        StructField("has_date_table", BooleanType(), True),
        StructField("has_hybrid_table", BooleanType(), True),
        StructField("has_rls", BooleanType(), True),
        StructField("is_direct_lake", BooleanType(), True),
        StructField("is_default_semantic_model", BooleanType(), True)
    ])

    # Create a DataFrame with one row
    df_enriching_info = spark.createDataFrame([row], schema = schema)

    dataframes.append(df_enriching_info)


# Union all DataFrames in the list
df_enriching_all_sem_models = dataframes[0]
for temp_df in dataframes[1:]:
    df_enriching_all_sem_models = df_enriching_all_sem_models.union(temp_df)

# Show the final DataFrame
display(df_enriching_all_sem_models)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df_sem_model_final = df_sem_model_cleaned.join(df_enriching_all_sem_models, ['dataset_name', 'workspace_name'], "left")
display(df_sem_model_final)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
