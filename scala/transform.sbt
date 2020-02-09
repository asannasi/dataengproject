name := "myproj"

version := "1.0"

scalaVersion := "2.12.10"

libraryDependencies += "org.apache.kafka" %% "kafka-streams-scala" % "2.0.1"

libraryDependencies += "com.goyeau" %% "kafka-streams-circe" % "0.6"

val circeVersion = "0.12.3"

libraryDependencies ++= Seq(
  "io.circe" %% "circe-core",
  "io.circe" %% "circe-generic",
  "io.circe" %% "circe-parser"
).map(_ % circeVersion)
