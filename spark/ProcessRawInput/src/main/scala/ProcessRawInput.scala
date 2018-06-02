/* ProcessRawInput.scala */
package processrawinput

import java.net.URL

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.Dataset
import org.apache.spark.sql.functions._

import processrawinput.DrudgeLink._

object ProcessRawInput {

  def getHost(s: String): String = {
    try {
      new URL(s).getHost.toLowerCase
    } catch {
      case e: Throwable => "BAD URL"
   }
  }
  def toHost = udf[String, String](getHost(_))

  val DRUDGE_REGEX = ".*drudge.*".r  
  def isDrudgeOrArchiveLink(s: String): Boolean = {
    DRUDGE_REGEX.findFirstIn(s).isDefined
  }
  def toDrudgeOrArchiveLinkBool = 
    udf[Boolean, String](isDrudgeOrArchiveLink(_))


  def main(args: Array[String]) {
   
    val spark = SparkSession.builder.appName("ProcessRawInput").getOrCreate()

    val inDf = spark.read.parquet("file:///home/david/transformed_data/H2Y2012.parquet")

    // drop __index_level_0__ column
    val COL_TO_DROP = "__index_level_0__"
    val droppedColIndex = inDf.columns.indexOf(COL_TO_DROP)
    val df = inDf.drop(COL_TO_DROP)

    import spark.implicits._
    val ds: Dataset[DrudgeLink] = df.as[DrudgeLink]
    
    ds.show(5)


    // clean up malformed URLs
    val uriBadProtocolRegex = "^(hhttp|tp)://"
    val dsCleanURL = ds.withColumn("urlCleanProtocol",
                           regexp_replace(
                             ds("url"),
                             uriBadProtocolRegex,
                             "http://"))

    def dsClean = 
      dsCleanURL
        // parsing the url
        .withColumn("host", toHost(col("urlCleanProtocol")))
        .withColumn("isDrudgeUrl", toDrudgeOrArchiveLinkBool(col("host")))
        .withColumn("badURL", col("host").startsWith("BAD URL"))     
        // transforming the page date time 
        .withColumn("pageDateTime", col("page_dt").cast("timestamp"))
        .drop("page_dt")

    dsClean.show(5)
    
    dsClean
      .filter("host = 'BAD URL'")
      .select("url")
      .show()
    spark.stop()
  }
}
