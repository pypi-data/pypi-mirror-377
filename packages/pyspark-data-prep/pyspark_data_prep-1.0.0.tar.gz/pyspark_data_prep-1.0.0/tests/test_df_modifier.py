import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark_data_prep.df_modifier import DataFrameModifier

@pytest.fixture(scope="session")
def spark_session():
    """
    Creates and returns a SparkSession for testing.
    """
    spark = SparkSession.builder \
        .master("local[2]") \
        .appName("PySpark Test") \
        .getOrCreate()
    yield spark
    spark.stop()

@pytest.fixture
def sample_dataframe(spark_session):
    """
    Creates a sample DataFrame for testing.
    """
    schema = StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True)
    ])
    data = [(1, "Alice"), (2, "Bob")]
    return spark_session.createDataFrame(data, schema)

def test_add_rows_success(spark_session, sample_dataframe):
    """
    Tests if rows are added successfully and the row count is correct.
    """
    modifier = DataFrameModifier(spark_session)
    new_data = [(3, "Charlie"), (4, "David")]
    combined_df = modifier.add_rows(sample_dataframe, new_data)
    
    # Assert that the new DataFrame has the correct number of rows.
    assert combined_df.count() == 4
    
    # Assert that the new rows exist in the combined DataFrame.
    expected_rows = {("Charlie",), ("David",)}
    added_rows = set(combined_df.filter("id > 2").rdd.map(lambda r: (r.name,)).collect())
    assert added_rows == expected_rows

def test_add_rows_with_empty_list(spark_session, sample_dataframe):
    """
    Tests that an empty list of new rows returns the original DataFrame.
    """
    modifier = DataFrameModifier(spark_session)
    combined_df = modifier.add_rows(sample_dataframe, [])
    
    # Assert that the DataFrame remains unchanged.
    assert combined_df.count() == sample_dataframe.count()