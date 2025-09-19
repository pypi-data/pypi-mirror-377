from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, TimestampType
from pyspark.sql.functions import current_timestamp
import random
import datetime



# 简化目录配置，不使用默认的 spark_catalog
# 创建数据库（如果不存在）
spark.sql("CREATE DATABASE IF NOT EXISTS wine_db")

# 创建 Iceberg 表（带主键和时间戳列）
create_table_sql = """
CREATE TABLE IF NOT EXISTS wine_db.wine_samples (
    wine_id INT COMMENT '红酒ID(主键)',
    name STRING COMMENT '红酒名称',
    year INT COMMENT '年份',
    country STRING COMMENT '国家',
    region STRING COMMENT '产区',
    price DOUBLE COMMENT '价格',
    rating DOUBLE COMMENT '评分',
    created_at TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP COMMENT '更新时间'
) USING iceberg
"""
spark.sql(create_table_sql)

# 生成20条红酒样例数据
wine_data = []
wine_names = [
    "Château Margaux", "Screaming Eagle", "Domaine de la Romanée-Conti", "Opus One", "Sassicaia",
    "Silver Oak", "Caymus", "Harlan Estate", "Sine Qua Non", "Penfolds Grange",
    "Vega Sicilia", "Almaviva", "Don Melchor", "Sena", "Clos Apalta",
    "Château Lafite Rothschild", "Château Latour", "Château Mouton Rothschild",
    "Château Haut-Brion", "Château Cheval Blanc"
]
countries = ["France", "USA", "Italy", "Spain", "Chile", "Australia"]
regions = ["Bordeaux", "Napa Valley", "Tuscany", "Rioja", "Maipo Valley", "Barossa Valley"]

for i in range(1, 21):
    name = wine_names[i - 1]  # 使用预定义的红酒名称
    year = random.randint(2015, 2022)
    country = random.choice(countries)
    region = random.choice(regions)
    price = round(random.uniform(50.0, 500.0), 2)
    rating = round(random.uniform(3.5, 5.0), 1)
    
    # 获取当前时间戳的实际值
    current_time = datetime.datetime.now()
    
    wine_data.append((
        i, name, year, country, region, price, rating,
        current_time, current_time  # 使用实际时间戳值
    ))

# 定义数据模式
schema = StructType([
    StructField("wine_id", IntegerType(), False),
    StructField("name", StringType(), False),
    StructField("year", IntegerType(), True),
    StructField("country", StringType(), True),
    StructField("region", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("rating", DoubleType(), True),
    StructField("created_at", TimestampType(), False),
    StructField("updated_at", TimestampType(), False)
])

# 创建 DataFrame
wine_df = spark.createDataFrame(wine_data, schema)

# 插入数据到 Iceberg 表
wine_df.write.format("iceberg").mode("append").saveAsTable("wine_db.wine_samples")

# 查询并显示表中的数据
print("Iceberg 表中的红酒数据:")
spark.sql("SELECT * FROM wine_db.wine_samples ORDER BY wine_id").show(truncate=False)

# 显示表详细信息
print("表详细信息:")
spark.sql("DESCRIBE EXTENDED wine_db.wine_samples").show(truncate=False)

# 示例查询：按国家分组统计
print("按国家分组的红酒统计:")
spark.sql("""
    SELECT country, 
           COUNT(*) as count, 
           ROUND(AVG(price), 2) as avg_price, 
           ROUND(AVG(rating), 2) as avg_rating
    FROM wine_db.wine_samples
    GROUP BY country
    ORDER BY avg_rating DESC
""").show()

# 示例查询：查找评分最高的红酒
print("评分最高的5款红酒:")
spark.sql("""
    SELECT wine_id, name, year, country, rating, price
    FROM wine_db.wine_samples
    ORDER BY rating DESC
    LIMIT 5
""").show(truncate=False)