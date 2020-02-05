
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
case class Player_Pair(player1: Player, player2: Player, radiant_win: Boolean, match_id: String)
case class Player(account_id: String, hero_id: Int, level: Int, team: String)
case class Match_Data(match_id: String, radiant_win: Boolean, players: List[Player])

object Transformer extends App{
  val props: Properties = {
    val p = new Properties()
    p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "10.0.0.13:9092")
    p.put(StreamsConfig.APPLICATION_ID_CONFIG, "transformer")
    p
  }
  val builder: StreamsBuilder = new StreamsBuilder
  val source = builder.stream[String, Match_Data]("raw_json")

  val playerPairs: KStream[String, Player_Pair] = source
    .flatMapValues(value => value.players.combinations(2).toList.map(x => Player_Pair(x(0), x(1), value.radiant_win, value.match_id)))
    .filter((_, value) => value.player1.account_id != "4294967295" && value.player2.account_id != "4294967295")

  val players: KStream[String, Player] = source
    .flatMapValues(value => value.players)
    .filter((_, value) => value.account_id != "4294967295")
  players.to("players")

  val player1Won = (pair: Player_Pair) => pair.player1.team == "radiant" && pair.radiant_win == true
  val sameTeam = (pair: Player_Pair) => pair.player1.team == pair.player2.team

  val wonWith = (_: String, pair: Player_Pair) => player1Won(pair) && sameTeam(pair)
  val wonAgainst = (_: String, pair: Player_Pair) => player1Won(pair) && !sameTeam(pair)
  val lostWith = (_: String, pair: Player_Pair) => !player1Won(pair) && sameTeam(pair)
  val lostAgainst = (_: String, pair: Player_Pair) => !player1Won(pair) && !sameTeam(pair)

  val relationships = playerPairs
    .branch(
      wonWith,
      wonAgainst,
      lostWith,
      lostAgainst
    )

  relationships(0).to("won_with")
  relationships(1).to("won_against")
  relationships(2).to("lost_with")
  relationships(3).to("lost_against")
  val streams: KafkaStreams = new KafkaStreams(builder.build(),props)
  //streams.cleanUp() // Not for production use. Will rebuild state.
  streams.start()
  sys.ShutdownHookThread{
    streams.close(Duration.ofSeconds(10))
  }
}
