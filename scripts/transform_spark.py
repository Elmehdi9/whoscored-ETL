from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

def load_json_data(file_path):
    try:
        spark = SparkSession.builder.appName("JSONProcessing").config("spark.driver.memory", "4g").getOrCreate()
        df = spark.read.json(file_path, multiLine=True)
        return df
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return None

def clean_process_data(df):
    try:
        df_exploded = df.select(col("league_name"), explode("matchs").alias("match_data"))

        events_df = df_exploded.select(
            col("league_name"),
            col("match_data.game_id").alias("game_id"),
            col("match_data.date").alias("date"),
            explode("match_data.events").alias("event_data")
        )

        cleaned_df = events_df.select(
            col("event_data.id").alias("event_id"),
            col("game_id").alias("match_id"),
            col("event_data.teamId").alias("team_id"),
            col("event_data.playerId").alias("player_id"),
            col("event_data.minute").alias("minute"),
            col("event_data.second").alias("second"),
            col("event_data.isTouch").alias("is_touch"),
            col("event_data.outcomeType.displayName").alias("outcome_type"),
            col("event_data.period.displayName").alias("period"),
            col("event_data.type.displayName").alias("type"),
            col("event_data.x").alias("x_coordinate"),
            col("event_data.y").alias("y_coordinate"),
            col("event_data.endX").alias("end_x_coordinate"),
            col("event_data.endY").alias("end_y_coordinate"),
            col("event_data.goalMouthY").alias("goal_y"),
            col("event_data.goalMouthZ").alias("goal_z")
        ).filter(col("player_id").isNotNull())

        cleaned_df.printSchema()
        cleaned_df.show(5)
        return cleaned_df
    except Exception as e:
        print(f"An error occurred during data cleaning: {e}")
        return None

def write_processed_data(df, output_name):
    try:
        
        df_single_partition = df.repartition(1)
        df_single_partition.write.mode('overwrite').parquet(output_name)
        print(f"Data successfully written to {output_name}.parquet")
    except Exception as e:
        print(f"An error occurred while writing the data: {e}")


if __name__ == "__main__":
    file_path = 'big_five_leagues.json'

    try:
        data_df = load_json_data(file_path)
        if data_df:
            processed_df = clean_process_data(data_df)
            if processed_df:
                write_processed_data(processed_df, "processed_data")
    except Exception as e:
        print(f"An error occurred: {e}")