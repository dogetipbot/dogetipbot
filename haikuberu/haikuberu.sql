/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `action`
--

DROP TABLE IF EXISTS `action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `action` (
  `action_id` int(20) unsigned NOT NULL AUTO_INCREMENT,
  `service_id` int(10) unsigned NOT NULL,
  `type` enum('givetip','withdraw','info','register','accept','decline','history','redeem','rates','deposit','link','connect','gold') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'givetip',
  `state` enum('completed','pending','failed','declined','expired') COLLATE utf8_unicode_ci NOT NULL,
  `error` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `from_user` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `to_user` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `to_addr` varchar(34) COLLATE utf8_unicode_ci DEFAULT NULL,
  `coin_val` decimal(20,8) DEFAULT NULL,
  `fiat_val` decimal(20,10) DEFAULT NULL,
  `txid` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `txfee` decimal(20,8) DEFAULT '0.00000000',
  `coin` varchar(3) COLLATE utf8_unicode_ci DEFAULT NULL,
  `fiat` varchar(3) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config1` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config2` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config3` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config4` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config5` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config6` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config7` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config8` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config9` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config10` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`action_id`),
  KEY `service_id` (`service_id`),
  KEY `txid` (`txid`),
  KEY `type` (`type`),
  KEY `config1` (`config1`),
  KEY `from_user` (`from_user`),
  KEY `to_user` (`to_user`),
  KEY `type_2` (`type`),
  CONSTRAINT `action_ibfk_1` FOREIGN KEY (`service_id`) REFERENCES `service` (`service_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `address`
--

DROP TABLE IF EXISTS `address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `address` (
  `address_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `user_id_alias` int(10) unsigned DEFAULT NULL,
  `coin` enum('dog') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'dog',
  `address` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `wallet_name` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `balance` decimal(20,8) NOT NULL DEFAULT '0.00000000',
  PRIMARY KEY (`address_id`),
  KEY `user_id` (`user_id`),
  KEY `user_id_alias` (`user_id_alias`),
  CONSTRAINT `address_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `config`
--

DROP TABLE IF EXISTS `config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `config` (
  `service_id` int(10) unsigned NOT NULL,
  `config1` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config2` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config3` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config4` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config5` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config6` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config7` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config8` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config9` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `config10` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`service_id`),
  CONSTRAINT `config_ibfk_2` FOREIGN KEY (`service_id`) REFERENCES `service` (`service_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fiat`
--

DROP TABLE IF EXISTS `fiat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fiat` (
  `fiat_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `fiat_data` text COLLATE utf8_unicode_ci,
  `fiat_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`fiat_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message` (
  `message_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `message` text COLLATE utf8_unicode_ci NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`message_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `service`
--

DROP TABLE IF EXISTS `service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service` (
  `service_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `service_name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`service_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Table values for table `service`
--
LOCK TABLES `service` WRITE;
/*!40000 ALTER TABLE `service` DISABLE KEYS */;

INSERT INTO `service` (`service_id`, `service_name`)
VALUES
	(1,'reddit'),
	(2,'twitch'),
	(3,'email'),
	(4,'twitter');

/*!40000 ALTER TABLE `service` ENABLE KEYS */;
UNLOCK TABLES;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unprocessed`
--

DROP TABLE IF EXISTS `unprocessed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unprocessed` (
  `unprocessed` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `txid` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`unprocessed`),
  KEY `txid` (`txid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unprocessed_bu`
--

DROP TABLE IF EXISTS `unprocessed_bu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unprocessed_bu` (
  `unprocessed` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `txid` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`unprocessed`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `user_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `joindate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `username`
--

DROP TABLE IF EXISTS `username`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `username` (
  `username_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `service_id` int(10) unsigned NOT NULL,
  `username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `joindate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`username_id`),
  UNIQUE KEY `unique_index` (`service_id`,`username`),
  KEY `user_id` (`user_id`),
  KEY `service_id` (`service_id`),
  KEY `username` (`username`),
  KEY `username_2` (`username`),
  CONSTRAINT `username_ibfk_4` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `username_ibfk_5` FOREIGN KEY (`service_id`) REFERENCES `service` (`service_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'haikuberu'
--
/*!50003 DROP PROCEDURE IF EXISTS `Achievement` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `Achievement`(IN user_id_in BIGINT(20))
BEGIN


SELECT
(SELECT SUM(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = user_id_in AND action.to_user IS NOT NULL AND action.from_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND `type` = 'givetip') AS `coins_sent`,
(SELECT SUM(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = user_id_in AND action.from_user IS NOT NULL AND action.to_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND `type` = 'givetip') AS `coins_received`,

(SELECT COUNT(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = user_id_in AND action.to_user IS NOT NULL AND action.from_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND `type` = 'givetip') AS `tips_sent`,
(SELECT COUNT(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = user_id_in AND action.from_user IS NOT NULL AND action.to_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND `type` = 'givetip') AS `tips_received`,

(SELECT COUNT(DISTINCT(action.to_user)) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = user_id_in AND action.to_user IS NOT NULL AND action.from_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND `type` = 'givetip') AS `tips_sent_unique`,
(SELECT COUNT(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = user_id_in AND action.to_user IS NULL AND action.from_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND `type` = 'deposit') AS `deposit_count`,
(SELECT COUNT(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = user_id_in AND action.to_user IS NULL AND action.from_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND `type` = 'givetip' AND to_addr IS NOT NULL) AS `withdraw_count`

;


END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetTwitchChannelHistory` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetTwitchChannelHistory`(IN channelName VARCHAR(255), IN maxResults INT(10), IN pageNumber INT(10))
BEGIN
      SET pageNumber = (pageNumber - 1) * maxResults;
        SELECT
        	*
        FROM
        	action
        WHERE
        	service_id = 2
        	AND type = 'givetip'
AND state IN('pending', 'completed')
        	AND config1 = CONCAT('#', channelName)
        ORDER BY
        	action.timestamp
        DESC LIMIT
        	pageNumber, maxResults;
    END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetTwitchChannelStats` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetTwitchChannelStats`(IN channelName VARCHAR(255))
BEGIN

    SELECT
    (SELECT SUM(coin_val) FROM action WHERE service_id = 2 AND type = 'givetip' AND state IN('pending', 'completed') AND config1 = CONCAT('#', channelName)) AS `total_tip_amount`,
    (SELECT COUNT(action_id) FROM action WHERE service_id = 2 AND type = 'givetip' AND state IN('pending', 'completed') AND config1 = CONCAT('#', channelName)) AS `total_tip_count`,
    (SELECT AVG(coin_val) FROM action WHERE service_id = 2 AND type = 'givetip' AND state IN('pending', 'completed') AND config1 = CONCAT('#', channelName)) AS `average_tip_amount`,
    (SELECT COUNT(DISTINCT(from_user)) FROM action WHERE service_id = 2 AND type = 'givetip' AND state IN('pending', 'completed') AND config1 = CONCAT('#', channelName)) AS `total_tip_users`;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `GetUserHistory` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetUserHistory`(IN userID BIGINT(20), IN maxResults INT(10), IN pageNumber INT(10))
BEGIN
      SET pageNumber = (pageNumber - 1) * maxResults;
        SELECT
        	service.service_name,
        	action.type,
        	action.state,
        	action.timestamp,
        	action.from_user,
        	action.to_user,
        	action.to_addr,
        	action.coin_val,
        	action.fiat_val,
        	action.coin,
        	action.fiat,
        	action.config1,
        	action.config2,
        	action.config3,
        	action.config4,
        	action.config5,
        	action.config6,
        	action.config7,
        	action.config8,
        	action.config9,
        	action.config10
        FROM
        	`username`
        	JOIN action ON action.service_id = username.service_id
        	JOIN service ON service.service_id = action.service_id
        WHERE
        	username.user_id = userID 
        	AND (action.from_user = username.username OR action.to_user = username.username) 
        	AND action.service_id = username.service_id 
        	AND type IN('givetip', 'redeem', 'withdraw', 'deposit', 'gold')
        ORDER BY
        	action.timestamp
        DESC LIMIT
        	pageNumber, maxResults;
    END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Info` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `Info`(
	IN user_id_in BIGINT(20)
)
BEGIN

SELECT
(SELECT balance from address WHERE user_id = user_id_in AND coin = 'dog') AS `balance`,
(SELECT SUM(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = user_id_in AND action.from_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND `type` = 'givetip') AS `total_sent`,

(SELECT SUM(action.coin_val) AS `total` FROM `username` JOIN action ON action.service_id = username.service_id WHERE username.user_id = user_id_in AND action.to_user= username.username AND action.service_id = username.service_id AND action.state = 'completed' AND `type` = 'givetip') AS `total_received`,

(SELECT address FROM `address` WHERE user_id = user_id_in) AS `address`;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Merge` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `Merge`(IN user_id_main BIGINT(20), IN user_id_merge BIGINT(20))
BEGIN
    DECLARE account_balance DECIMAL(20,8);

    SET account_balance = (SELECT balance FROM address WHERE user_id = user_id_merge);

    UPDATE username SET user_id = user_id_main WHERE user_id = user_id_merge;

    UPDATE address SET balance = balance + account_balance WHERE user_id = user_id_main;

    UPDATE address SET `balance` = 0, `user_id_alias` = user_id_main WHERE user_id = user_id_merge;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Register` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `Register`(
	IN service_id_in INT(10),
	IN username_in VARCHAR(100)
)
BEGIN
DECLARE user_id_insert INT DEFAULT NULL;
START TRANSACTION;
	INSERT INTO user(user_id) VALUES (null);
	SET user_id_insert = LAST_INSERT_ID();
	INSERT INTO username (user_id, service_id, username) VALUES (user_id_insert, service_id_in, username_in);
	INSERT INTO address (user_id) VALUES (user_id_insert);
COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `RegisterService` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = '' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `RegisterService`(
IN user_id_in BIGINT(20),	
IN service_id_in INT(10),
	IN username_in VARCHAR(100)
)
BEGIN
DECLARE user_id_insert INT DEFAULT NULL;
START TRANSACTION;
	INSERT INTO username (user_id, service_id, username) VALUES (user_id_in, service_id_in, username_in);
COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;