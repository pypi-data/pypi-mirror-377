from pyspark.sql import functions as F

def get_token_history(df, new_token_column, old_token_column):
    edges = (
        df
        .select(
            F.col(f"{new_token_column}").alias("new_token"),
            F.col(f"{old_token_column}").alias("old_token")
        )
        .dropna(subset=["new_token", "old_token"])
        .dropDuplicates()
    )

    # 1) 루트(최초 토큰) 후보 찾기: old_token이지만 어떤 new_token으로도 등장하지 않은 토큰
    roots = edges.select("old_token").distinct().join(
        edges.select(F.col("new_token").alias("old_token")).distinct(),
        on="old_token",
        how="left_anti"
    )

    # roots: [old_token] (여러 체인이 있으면 여러 행)

    # 2) 첫 단계: 루트의 직후 자식들에 루트 토큰을 ori_token으로 부여
    history = (
        edges.join(roots, on="old_token", how="inner")
        .select(
            F.col("new_token"),
            F.col("old_token").alias("ori_token")
        )
        .distinct()
    )

    # 3) 전파: new_token을 old_token으로 이어가며 ori_token을 계속 상속
    MAX_HOPS = 20  # 재발급 최대 깊이가 더 길 수 있으면 늘리세요
    for _ in range(MAX_HOPS):
        step = (
            edges.join(
                history.select(F.col("new_token").alias("old_token"), "ori_token"),
                on="old_token",
                how="inner"
            )
            .select("new_token", "ori_token")
            .distinct()
        )
        # 이미 매핑된 new_token은 제외
        step = step.join(history, on="new_token", how="left_anti")
        if step.rdd.isEmpty():  # 더 이상 확장 불가하면 종료
            break
        history = history.unionByName(step)
    return history


def get_token_history_using_pdf(spark, df_token_reissue, new_token_column="user", old_token_column="prevUser"):
    import pandas as pd
    from pyspark.sql.types import StructType, StructField, StringType

    pdf = df_token_reissue.dropDuplicates().toPandas()

    if pdf.empty:
        schema = StructType([
            StructField(new_token_column, StringType(), True),
            StructField(old_token_column, StringType(), True),
            StructField("initial_token", StringType(), True)
        ])
        return spark.createDataFrame([], schema)

    parent_map = dict(
        (row[new_token_column], row[old_token_column])
        for _, row in pdf.iterrows()
        if pd.notnull(row[old_token_column]) and str(row[old_token_column]).strip() != ""
    )

    def find_root(token):
        visited = set()
        while token in parent_map and token not in visited:
            visited.add(token)
            next_token = parent_map[token]
            if pd.isnull(next_token) or str(next_token).strip() == "":
                return token
            token = next_token
        return token

    pdf["initial_token"] = pdf[new_token_column].map(find_root)

    df_token_history = spark.createDataFrame(pdf)
    df_token_history = df_token_history.dropDuplicates()
    return df_token_history


