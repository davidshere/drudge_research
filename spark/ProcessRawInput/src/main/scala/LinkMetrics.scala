package processrawinput

import org.apache.spark.sql.DataFrame

import org.apache.spark.ml.feature.VectorAssembler
import org.apache.spark.ml.linalg.Vectors

import org.apache.spark.ml.clustering.KMeans
//import org.apache.spark.ml.evaluation.ClusteringEvaluator

import org.apache.spark.sql.functions._

object LinkMetrics {

  def transformInput(df: DataFrame): DataFrame = {
   
    // create features
    val linkIdCountsDf = df.groupBy("linkId").count()
    
    val inputWithFeatureColumns = df
      .select("linkInstanceId", "linkId", "url")
      .join(linkIdCountsDf, "linkId")
      .withColumn("urlCharLength", length(col("url")))
      .withColumn("hedCharLength", length(col("hed")))

    val assembler = new VectorAssembler()
      .setInputCols(Array("count", "urlCharLength", "hedCharLength"))
      .setOutputCol("features")

    val dfToTrain = assembler.transform(inputWithFeatureColumns)

    dfToTrain
  }

  def cleanOutput(df: DataFrame): DataFrame = {
    df
      .drop("linkId")
      .drop("count")
      .drop("features")
      .withColumn(
        "linkType",
        when(col("prediction") === 0, "longTerm")
          .otherwise("shortTerm"))
      .drop("prediction")
     
  }
    
  def clusterLinkTypes(df: DataFrame): DataFrame = {
    val inDf = transformInput(df)

    // train the model, apply the clusters to the input data
    val kmeans = new KMeans().setK(2).setSeed(1l)
    val model = kmeans.fit(inDf)
    val dfWithPredictions = model.transform(inDf)

    // transform and return the output
    cleanOutput(dfWithPredictions)

  }  

}
