package processrawinput

import org.apache.spark.sql.DataFrame

import org.apache.spark.ml.feature.{ VectorAssembler, Normalizer }
import org.apache.spark.ml.linalg.Vectors

import org.apache.spark.ml.clustering.KMeans
//import org.apache.spark.ml.evaluation.ClusteringEvaluator

import org.apache.spark.sql.functions._

object LinkMetrics {

  def transformInput(df: DataFrame): DataFrame = {
   
    // create features
    val linkIdCountsDf = df.groupBy("linkId").count()
    
    val inputWithFeatureColumns = df
      .select("linkInstanceId", "linkId", "url", "hed")
      .join(linkIdCountsDf, "linkId")
      .withColumn("urlCharLength", length(col("url")))
      .withColumn("hedCharLength", length(col("hed")))

    val assembler = new VectorAssembler()
      .setInputCols(Array("count", "urlCharLength", "hedCharLength"))
      .setOutputCol("features")

    val dfWithFeatureVector = assembler.transform(inputWithFeatureColumns)

    normalizeFeatures(dfWithFeatureVector)
    
  }

  def normalizeFeatures(df: DataFrame): DataFrame = {
    val normalizer = new Normalizer()
	.setInputCol("feature")
	.setOutputCol("normFeatures")
	.setP(1.0)

    normalizer
      .transform(df)
      .withColumnRenamed("normFeature", "features")
  }

  def cleanOutput(df: DataFrame): DataFrame = {
    /*
    Do a little post processing, dropping unnecessary columns and
    using meaningful terms for the prediction model outputs. 


    */
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
