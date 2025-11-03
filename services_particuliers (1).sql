-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Nov 03, 2025 at 06:34 PM
-- Server version: 11.7.2-MariaDB
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `services_particuliers`
--

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id_categorie` int(11) NOT NULL AUTO_INCREMENT,
  `nom_categorie` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  PRIMARY KEY (`id_categorie`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reservation`
--

DROP TABLE IF EXISTS `reservation`;
CREATE TABLE IF NOT EXISTS `reservation` (
  `id_reservation` int(11) NOT NULL AUTO_INCREMENT,
  `id_service` int(11) NOT NULL,
  `id_utilisateur` int(11) NOT NULL,
  `date_reservation` date NOT NULL,
  `heure_reservation` time NOT NULL,
  PRIMARY KEY (`id_reservation`),
  KEY `nom_service` (`id_service`),
  KEY `nom_utilisateur` (`id_utilisateur`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `services`
--

DROP TABLE IF EXISTS `services`;
CREATE TABLE IF NOT EXISTS `services` (
  `id_service` int(11) NOT NULL AUTO_INCREMENT,
  `id_categorie` int(11) NOT NULL,
  `titre` varchar(50) NOT NULL,
  `description` varchar(2000) NOT NULL,
  `localisation` varchar(50) NOT NULL,
  `date_creation` datetime DEFAULT current_timestamp(),
  `actif` tinyint(1) DEFAULT 1,
  `cout` decimal(8,2) DEFAULT 0.00,
  `photo` varchar(50) DEFAULT NULL,
  `id_utilisateurService` int(11) NOT NULL,
  PRIMARY KEY (`id_service`),
  KEY `id_categorie` (`id_categorie`),
  KEY `nom` (`id_utilisateurService`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `utilisateurs`
--

DROP TABLE IF EXISTS `utilisateurs`;
CREATE TABLE IF NOT EXISTS `utilisateurs` (
  `id_utilisateur` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(20) NOT NULL,
  `prenom` varchar(20) NOT NULL,
  `courriel` varchar(50) NOT NULL,
  `mot_de_passe` varchar(255) NOT NULL,
  `role` tinyint(1) NOT NULL,
  PRIMARY KEY (`id_utilisateur`),
  UNIQUE KEY `courriel` (`courriel`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id_utilisateur`, `nom`, `prenom`, `courriel`, `mot_de_passe`, `role`) VALUES
(2, 'Ouattara', 'Aicha', 'admin@gmail.com', '123456', 1);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `reservation`
--
ALTER TABLE `reservation`
  ADD CONSTRAINT `reservation_ibfk_1` FOREIGN KEY (`id_service`) REFERENCES `services` (`id_service`),
  ADD CONSTRAINT `reservation_ibfk_2` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`);

--
-- Constraints for table `services`
--
ALTER TABLE `services`
  ADD CONSTRAINT `services_ibfk_1` FOREIGN KEY (`id_categorie`) REFERENCES `categories` (`id_categorie`),
  ADD CONSTRAINT `services_ibfk_2` FOREIGN KEY (`id_utilisateurService`) REFERENCES `utilisateurs` (`id_utilisateur`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
