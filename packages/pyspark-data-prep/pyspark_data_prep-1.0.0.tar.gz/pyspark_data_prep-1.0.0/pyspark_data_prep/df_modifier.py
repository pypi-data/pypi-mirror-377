import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

class DataFrameModifier:
    """
    A class to encapsulate common PySpark DataFrame modification operations.

    This class provides a clean and reusable way to perform transformations like
    adding new rows to an existing DataFrame by leveraging the unionByName() method.
    """

    def __init__(self, spark: SparkSession):
        """
        Initializes the DataFrameModifier with a SparkSession.

        Args:
            spark (SparkSession): The active SparkSession.
        """
        self.spark = spark

    def add_rows(self, df: pyspark.sql.DataFrame, new_data: list) -> pyspark.sql.DataFrame:
        """
        Adds one or more new rows to a PySpark DataFrame.

        This method is non-destructive and returns a new DataFrame.
        It infers the schema from the original DataFrame and creates a new
        DataFrame from the provided data before performing a union.

        Args:
            df (pyspark.sql.DataFrame): The original PySpark DataFrame.
            new_data (list): A list of tuples, where each tuple represents a new row.
                             The order and types of values in each tuple must match 
                             the original DataFrame's schema.

        Returns:
            pyspark.sql.DataFrame: A new DataFrame with the added rows.
        """
        if not isinstance(new_data, list):
            print("Error: new_data must be a list of tuples.")
            return df
            
        if not new_data:
            print("Warning: new_data list is empty. Returning the original DataFrame.")
            return df

        # Ensure all new rows have the correct number of columns
        for row in new_data:
            if len(row) != len(df.columns):
                print(f"Error: A row in new_data has {len(row)} items, but the DataFrame has {len(df.columns)} columns.")
                return df

        try:
            # Create a list of Row objects from the new data
            new_rows_list = [Row(*df.columns)(*row) for row in new_data]

            # Create a new DataFrame containing only the new rows.
            # We use the existing schema to maintain consistency.
            new_df = self.spark.createDataFrame(new_rows_list, df.schema)

            # Use unionByName to combine the original and new DataFrames.
            # This is robust as it matches columns by name, not position.
            combined_df = df.unionByName(new_df)

            return combined_df

        except Exception as e:
            print(f"An error occurred while adding the rows: {e}")
            return df