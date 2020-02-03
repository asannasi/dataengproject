
package me.dataengproject.transform;

//https://medium.com/@danieljameskay/kafka-streams-dsl-for-scala-the-basics-11d603295f5c

import java.util.Properties
import java.time.Duration

import org.apache.kafka.streams.scala.ImplicitConversions._
import org.apache.kafka.streams.scala.Serdes._
import org.apache.kafka.streams.{KafkaStreams, StreamsConfig}
import org.apache.kafka.streams.scala.kstream._
import org.apache.kafka.streams.scala._
import org.apache.kafka.streams.scala.StreamsBuilder
import org.apache.kafka.streams.scala.Serdes._
import org.apache.kafka.streams.scala.ImplicitConversions._
import org.apache.kafka.common.serialization.Serializer;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.streams.kstream.Serialized;
import com.goyeau.kafka.streams.circe.CirceSerdes._
import io.circe.generic.auto._
import org.apache.kafka.streams.kstream.Materialized
import org.apache.kafka.streams.kstream.Printed

//case class Teammates(account_id: String)
//case class Player(account_id: String, teammates:Array[Teammate])
case class Player(account_id: Int, hero_id: Int, level: Int, win: String)
case class Match_Data(match_id: Int, radiant_win: String, players: List[Player])

object Transformer extends App{
  val props: Properties = {
    val p = new Properties()
    p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "10.0.0.10:9092")
    p.put(StreamsConfig.APPLICATION_ID_CONFIG, "transformer")
    p
  }
  val builder: StreamsBuilder = new StreamsBuilder
  val source = builder.stream[String, Match_Data]("test")
  source.print(Printed.toSysOut())

  val node: KStream[String, String] = source.flatMap(source => source.)
  source.to("StreamsOutput")
  val streams: KafkaStreams = new KafkaStreams(builder.build(),props)
  //streams.cleanUp() // Not for production use. Will rebuild state.
  streams.start()
  sys.ShutdownHookThread{
    streams.close(Duration.ofSeconds(10))
  }
}
