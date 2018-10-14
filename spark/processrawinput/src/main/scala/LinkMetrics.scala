package processrawinput

import org.apache.spark.sql.DataFrame

import org.apache.spark.ml.feature.{ VectorAssembler, Normalizer }
import org.apache.spark.ml.linalg.Vectors

import org.apache.spark.ml.clustering.KMeans
//import org.apache.spark.ml.evaluation.ClusteringEvaluator

import org.apache.spark.sql.functions._

object LinkMetrics {

  def prepareInput(df: DataFrame): DataFrame = {
    val features = generateFeatures(df) 

    val assembler = new VectorAssembler()
      // current best feature set
      .setInputCols(Array("count", "urlCharLength", "hedCharLength"))
      .setOutputCol("features")

    val dfWithFeatureVector = assembler.transform(features)

    normalizeFeatures(dfWithFeatureVector)
    
  }

  def generateFeatures(df: DataFrame): DataFrame = {

    val linkIdCountsDf = df.groupBy("linkId").count()
    
    df
      .select("linkInstanceId", "linkId", "url", "hed")
      .join(linkIdCountsDf, "linkId")
      .withColumn("urlCharLength", length(col("url")))
      .withColumn("hedCharLength", length(col("hed")))
      .withColumn("urlhedInteration", length(col("hed")) * length(col("url")))
      .withColumn("hedUpperPct", levenshtein(col("hed"), lower(col("hed"))) / length(col("hed")))
  }


  def normalizeFeatures(df: DataFrame): DataFrame = {
    val normalizer = new Normalizer()
	.setInputCol("features")
	.setOutputCol("normFeatures")
	.setP(1.0)

    normalizer
      .transform(df)
      .drop("features")
      .withColumnRenamed("normFeatures", "features")
  }

  def cleanUpPredictions(df: DataFrame): DataFrame = {
    /*
     * Our model is pretty good at figuring out short term links
     * vs. long term links, but some are miscategorized, and obviously
     * so. In particular, a long term link should only have uppercase
     * letters in its headline, but some have lowercase letters. This
     * function finds links labeled long term and if they satisfy some
     * conditions, recategorizes them as short term links. It also
     * turns the 0 and 1 into `s` and `l`
     */
    df
      // recategorize st links as lt if they have lowercase headlines
      .withColumn(
        "predictionFixedHedCase",
	when(
	  col("prediction") === 0 && 
	  col("hed") =!= upper(col("hed")) && 
          ! lower(col("url")).like("%drudge%") &&
          ! col("url").like("%buycytotec"), 1)
          .otherwise(col("prediction"))
       )
      // change predictions from 0 to 1 to `s` and `l`
      .withColumn(
        "linkType",
        when(col("predictionFixedHedCase") === 0, "l").otherwise("s")
      )
      // drop intermediate columns
      .drop("prediction")
      .drop("predictionFixedHedCase")
  
  }

  def cleanOutput(df: DataFrame): DataFrame = {
    /*
     * Post processning steps:
     *   - fix some predictions and make the output meaningful
     *   - filter down to only the columns we need to return
     *   - filter down to only distict entries, one row per linkId
    */
    val dfWithCleanPredictions = cleanUpPredictions(df)

    dfWithCleanPredictions
      .select("linkId", "linkType")
      .distinct
  }
    
  def clusterLinkTypes(df: DataFrame): DataFrame = {
    val input = prepareInput(df)

    // train the model, apply the clusters to the input data
    val kmeans = new KMeans().setK(2).setSeed(1l)
    val model = kmeans.fit(input)
    val dfWithPredictions = model.transform(input)

    // transform and return the output
    cleanOutput(dfWithPredictions)

  }  

}
