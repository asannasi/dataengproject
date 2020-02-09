/*
 * This program is a Kafka streams app that will process match data from the 
 * subscribed topic in JSON and transform it into multiple player interactions
 * messages in JSON format suited for neo4j. The transformed data is sent to 
 * Kafka as new topics. 
 */

package me.dataengproject.transform;

import java.util.Properties
import java.time.Duration

import org.apache.kafka.streams.scala.ImplicitConversions._
import org.apache.kafka.streams.scala.kstream._
import org.apache.kafka.streams.scala._
import org.apache.kafka.streams.scala.StreamsBuilder
import org.apache.kafka.streams.scala.Serdes._
import org.apache.kafka.streams.scala.ImplicitConversions._

import org.apache.kafka.common.serialization.Serializer;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serde;

import org.apache.kafka.streams.{KafkaStreams, StreamsConfig}
import org.apache.kafka.streams.kstream.Serialized;
import org.apache.kafka.streams.kstream.Materialized
import org.apache.kafka.streams.kstream.Printed

import com.goyeau.kafka.streams.circe.CirceSerdes._
import io.circe.generic.auto._

// Define JSON message structures
case class MatchData(
  match_id: String, 
  radiant_win: Boolean, 
  start_time: String, 
  duration: String,
  players: List[Player]
)
case class Player(
  account_id: String, 
  hero_id: Int, 
  xp_per_min: Int, 
  gold_per_min: Int,
  team: String,
  total_healing: Int,
  total_hero_damage: Int,
  total_tower_damage: Int,
  killed: List[Receiver],
  damaged: List[Receiver],
  healed: List[Receiver]
)
case class Receiver(
  account_id: String,
  hero_id: Int,
)
case class Interaction(
  account_id1: String,
  hero_id1: Int,
  account_id2: String,
  hero_id2: Int
)
case class TeamInteraction(
  account_id1: String,
  hero_id1: Int,
  team1: String,
  account_id2:String,
  hero_id2: Int,
  team2: String,
  radiant_win: Boolean, 
)

// This is the main method called when this Kafka streams app is run 
object Transformer extends App{
  // Configure the broker connections to the Kafka cluster and assign an App Id
  val props: Properties = {
    val p = new Properties()
    p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, 
      "10.0.0.13:9092,10.0.0.11:9092,10.0.0.9:9092")
    p.put(StreamsConfig.APPLICATION_ID_CONFIG, "transformer")
    p
  }

  // Connect to the Kafka stream topic
  val builder: StreamsBuilder = new StreamsBuilder
  val topicName: String = "raw_json"
  val source = builder.stream[String, MatchData](topicName)

  // Setup predicate for testing if an account_id is masked
  val anonAccountId: String = "4294967295"
  val isAnon = (account_id: String) => account_id == anonAccountId

  /*
   * Make 3 streams for player interactions of killed, damaged, and 
   * healed by using the data stored in each player. 
   */
  // Generate stream of each player's data
  val players: KStream[String, Player] = source
    .flatMapValues(value => value.players)
    .filter((_, value) => !isAnon(value.account_id))

  // Parse and format the interactions each player did to each other
  val killed: KStream[String, Interaction] = players
    .flatMapValues(value => value.killed
      .map(x => Interaction(
        value.account_id, value.hero_id, x.account_id, x.hero_id))
    )
    .filter((_, value) => !isAnon(value.account_id2))
  killed.to("killed")

  val healed: KStream[String, Interaction] = players
    .flatMapValues(value => value.healed
      .map(x => Interaction(
        value.account_id, value.hero_id, x.account_id, x.hero_id))
    )
    .filter((_, value) => !isAnon(value.account_id2))
  healed.to("healed")

  val damaged: KStream[String, Interaction] = players
    .flatMapValues(value => value.damaged
      .map(x => Interaction(
        value.account_id, value.hero_id, x.account_id, x.hero_id))
    )
    .filter((_, value) => !isAnon(value.account_id2))
  damaged.to("damaged")

  /*
   * Now branch player pairs stream into pairs that won with each other, lost
   * with each other, won against each other, and lost against each other.
   */
  // Generate distinct pairs of players from the 10 players in the match and
  // filter anonymous accounts
  val pairInteractions: KStream[String, TeamInteraction] = source
    .flatMapValues(value => value.players
                                  .combinations(2)
                                  .toList
                                  .map(x => TeamInteraction(
                                    x(0).account_id,
                                    x(0).hero_id,
                                    x(0).team,
                                    x(1).account_id,
                                    x(1).hero_id,
                                    x(1).team,
                                    value.radiant_win, 
                                  )))
    .filter((_,value) => !isAnon(value.account_id1) && 
                         !isAnon(value.account_id2))

  // Define predicates
  val player1Won = (pair: TeamInteraction) => pair.team1 == "radiant" && 
                                          pair.radiant_win == true
  val sameTeam = (pair: TeamInteraction) => pair.team1 == pair.team2

  val wonWith    = (_: String, pair: TeamInteraction) =>  
    player1Won(pair) &&  sameTeam(pair)
  val wonAgainst = (_: String, pair: TeamInteraction) => 
    player1Won(pair) && !sameTeam(pair)
  val lostWith   = (_: String, pair: TeamInteraction) => 
    !player1Won(pair) &&  sameTeam(pair)
  val lostAgainst= (_: String, pair: TeamInteraction) => 
    !player1Won(pair) && !sameTeam(pair)

  // Branch stream into 4 relationship streams.
  val relationships = pairInteractions 
    .branch(wonWith, wonAgainst, lostWith, lostAgainst)
  // Change each stream into interactions instead of team interactions
  val wonWithStream: KStream[String, Interaction] = relationships(0)
    .mapValues(value => Interaction(
      value.account_id1, value.hero_id1, value.account_id2, value.hero_id2))
  wonWithStream.to("won_with")
  val wonAgainstStream: KStream[String, Interaction] = relationships(1)
    .mapValues(value => Interaction(
      value.account_id1, value.hero_id1, value.account_id2, value.hero_id2))
  wonAgainstStream.to("won_against")
  val lostWithStream: KStream[String, Interaction] = relationships(2)
    .mapValues(value => Interaction(
      value.account_id1, value.hero_id1, value.account_id2, value.hero_id2))
  lostWithStream.to("lost_with")
  val lostAgainstStream: KStream[String, Interaction] = relationships(3)
    .mapValues(value => Interaction(
      value.account_id1, value.hero_id1, value.account_id2, value.hero_id2))
  lostAgainstStream.to("lost_against")

  // Send stream to Kafka cluster
  val streams: KafkaStreams = new KafkaStreams(builder.build(),props)
  streams.start()

  // Close stream if program is shut down
  sys.ShutdownHookThread{
    streams.close(Duration.ofSeconds(10))
  }
}
