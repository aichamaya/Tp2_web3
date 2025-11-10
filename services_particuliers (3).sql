-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Nov 10, 2025 at 04:28 PM
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
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id_categorie`, `nom_categorie`, `description`) VALUES
(10, 'Fitness', 'Entraînement physique et musculation'),
(11, 'Sports de raquette', 'Tennis, Badminton, Squash'),
(12, 'Bien-être & Récupération', 'Massages, Yoga, Nutrition'),
(20, 'Coaching', NULL),
(21, 'Coaching', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `reservations`
--

DROP TABLE IF EXISTS `reservations`;
CREATE TABLE IF NOT EXISTS `reservations` (
  `id_reservation` int(11) NOT NULL AUTO_INCREMENT,
  `id_service` int(11) NOT NULL,
  `id_utilisateur` int(11) NOT NULL,
  `date_reservation` datetime NOT NULL DEFAULT current_timestamp(),
  `date_souhaitee` date NOT NULL,
  `cout_paye` decimal(10,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id_reservation`),
  KEY `nom_service` (`id_service`),
  KEY `nom_utilisateur` (`id_utilisateur`),
  KEY `idx_reservations_service` (`id_service`),
  KEY `idx_reservations_utilisateur` (`id_utilisateur`),
  KEY `idx_reservations_dates` (`date_reservation`,`date_souhaitee`)
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
  `nom_image` varchar(255) DEFAULT NULL,
  `id_utilisateur` int(11) NOT NULL,
  PRIMARY KEY (`id_service`),
  KEY `id_categorie` (`id_categorie`),
  KEY `nom` (`id_utilisateur`),
  KEY `idx_services_categorie` (`id_categorie`),
  KEY `idx_services_utilisateur` (`id_utilisateur`),
  KEY `idx_services_actif_date` (`actif`,`date_creation`)
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `services`
--

INSERT INTO `services` (`id_service`, `id_categorie`, `titre`, `description`, `localisation`, `date_creation`, `actif`, `cout`, `nom_image`, `id_utilisateur`) VALUES
(100, 10, 'Cours de Yoga débutant', 'Séance de yoga doux pour améliorer la flexibilité.', 'Gymnase A', '2025-11-10 01:35:35', 1, 10.00, 'yoga.jpg', 2),
(101, 11, 'Partenariat Tennis (Intermédiaire)', 'Recherche partenaire pour matchs amicaux intensifs.', 'Parc Central', '2025-11-10 01:35:35', 1, 5.00, 'tennis.jpg', 3),
(102, 12, 'Massage sportif - 60 min', 'Récupération musculaire après effort.', 'Local 101', '2025-11-10 01:35:35', 1, 30.00, 'massage.jpg', 1),
(103, 10, 'Programme de Musculation', 'Plan d\'entraînement personnalisé (INACTIF).', 'En ligne', '2025-11-10 01:35:35', 0, 40.00, 'muscu.jpg', 2);

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
  `credit` decimal(10,2) NOT NULL DEFAULT 0.00,
  `role` varchar(20) NOT NULL DEFAULT 'utilisateur',
  PRIMARY KEY (`id_utilisateur`),
  UNIQUE KEY `courriel` (`courriel`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id_utilisateur`, `nom`, `prenom`, `courriel`, `mot_de_passe`, `credit`, `role`) VALUES
(2, 'Dubois', 'Alice', 'alice@test.ca', 'sha256$r3o9p5d2$1c3d1f0a1e3d9f3b7c2d8e4f1a9c3e2f5b8a6d4e2c0e1a3d9b8c7f6e5d4a3b2c', 15.00, 'utilisateur'),
(3, 'Tremblay', 'Bob', 'bob@test.ca', 'sha256$a7b1c3d9$5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f', 5.00, 'utilisateur'),
(4, 'Admin', 'Garneau', 'admin@garneau.ca', 'sha256$n3dYlU31g7dD2a9v$2b5b48192b0f3408665f973e6593a213e4b31336181b676a6610338981e4b39b', 0.00, 'admin');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `reservations`
--
ALTER TABLE `reservations`
  ADD CONSTRAINT `fk_reservations_service` FOREIGN KEY (`id_service`) REFERENCES `services` (`id_service`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_reservations_utilisateur` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `reservations_ibfk_1` FOREIGN KEY (`id_service`) REFERENCES `services` (`id_service`),
  ADD CONSTRAINT `reservations_ibfk_2` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`);

--
-- Constraints for table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  ADD CONSTRAINT `utilisateurs_ibfk_1` FOREIGN KEY (`id_utilisateur`) REFERENCES `utilisateurs` (`id_utilisateur`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
