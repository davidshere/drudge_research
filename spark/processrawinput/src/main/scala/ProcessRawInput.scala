/* ProcessRawInput.scala */
package processrawinput

import java.net.URL
import java.util.UUID

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.{ Dataset, DataFrame }
import org.apache.spark.sql.functions._

import DrudgeLink._

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

  def cleanUpURL(ds: Dataset[DrudgeLink]): DataFrame = {
    // remove links with bad protocols
    val dfNoBadProtocol = ds
      .filter(r => ! r.url.startsWith("mailto:"))
      .filter(r => ! r.url.startsWith("javascript"))
      .filter(r => r.url != "<A HREF=")

    // clean up malformed URLs
    val uriBadProtocolRegex = "^(hhttp|tp|p)://"

    val cleanedProtocol = dfNoBadProtocol
      .withColumn("urlCleanProtocol",
        regexp_replace(
          ds("url"),
          uriBadProtocolRegex,
          "http://"))

    val cleanUpCharacters = cleanedProtocol
      .withColumn("trimmedUrl", trim(col("urlCleanProtocol")))

    cleanUpCharacters
      .drop("url")
      .drop("urlCleanProtocol")
      .withColumn("url", col("trimmedUrl"))
      .drop("trimmedUrl")
  }

  def enrichTableWithBasicColumns(df: DataFrame): DataFrame = {
    /*
      Run some simple transformations on the input data. Specifically, we're adding:

      host: UDF uses java.net.URL.getHost to parse the url into a hostname
      isDrudgeUrl: UDF to run a regex looking for 'drudge' in the hostname
      badURL: transform BAD URL from the input data (i know) to a boolean
      pageDateTime: casting the text input to a timestamp
      linkId: a hash of the unique key for a link
      linkInstanceId: a unique index for each instance of a drudge link
    */
    df
      // parsing the url
      .withColumn("host", toHost(col("url")))
      .withColumn("isDrudgeUrl", toDrudgeOrArchiveLinkBool(col("host")))
      // this is sort of a debugging column
      .withColumn("badURL", col("host").startsWith("BAD URL"))
      // transforming the page date time
      .withColumn("pageDateTime", col("page_dt").cast("timestamp"))
      .drop("page_dt")
      // add a unique identifier for the unique drudge link
      .withColumn("linkId", hash(concat(col("hed"), col("url"))))
      .withColumn("linkInstanceId", monotonically_increasing_id)
  }

  def transformDataFrame(df: Dataset[DrudgeLink]): DataFrame = {

    val dfCleanUrls = cleanUpURL(df)
    val dfWithCols = enrichTableWithBasicColumns(dfCleanUrls)

    // Need to classify link instances as long-term or short-term links
    import processrawinput.LinkMetrics
    val dfWithLinkTypes = LinkMetrics.clusterLinkTypes(dfWithCols)
    //dfWithCols
    dfWithLinkTypes.join(dfWithCols, "linkInstanceId")

  }

  def loadDrudgeLinks(filename: String, spark: SparkSession): Dataset[DrudgeLink] = {
    val inDf = spark.read.parquet(s"file:///vagrant/${filename}.parquet")

    // drop __index_level_0__ column
    val COL_TO_DROP = "__index_level_0__"
    val droppedColIndex = inDf.columns.indexOf(COL_TO_DROP)
    val df = inDf.drop(COL_TO_DROP)

    import spark.implicits._

    df.as[DrudgeLink]
  }

  def main(args: Array[String]) {
   
    val spark = SparkSession.builder.appName("ProcessRawInput").getOrCreate()

    val df = loadDrudgeLinks("H2Y2010", spark)

    val transformedDf = transformDataFrame(df)

    transformedDf.show(5)

  }
}
