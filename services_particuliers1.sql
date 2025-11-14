-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3307
-- Généré le : ven. 14 nov. 2025 à 16:40
-- Version du serveur : 9.1.0
-- Version de PHP : 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `services_particuliers1`
--

-- --------------------------------------------------------

--
-- Structure de la table `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id_categorie` int NOT NULL AUTO_INCREMENT,
  `nom_categorie` varchar(100) NOT NULL,
  `description` text,
  PRIMARY KEY (`id_categorie`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `categories`
--

INSERT INTO `categories` (`id_categorie`, `nom_categorie`, `description`) VALUES
(10, 'Fitness', 'Entraînement physique et musculation'),
(11, 'Sports de raquette', 'Tennis, Badminton, Squash'),
(12, 'Bien-être & Récupération', 'Massages, Yoga, Nutrition'),
(20, 'Coaching', NULL),
(21, 'Coaching', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `reservations`
--

DROP TABLE IF EXISTS `reservations`;
CREATE TABLE IF NOT EXISTS `reservations` (
  `id_reservation` int NOT NULL AUTO_INCREMENT,
  `id_service` int NOT NULL,
  `id_utilisateur` int NOT NULL,
  `date_reservation` date NOT NULL,
  `date_souhaitee` time NOT NULL,
  PRIMARY KEY (`id_reservation`),
  KEY `idx_service` (`id_service`),
  KEY `idx_utilisateur` (`id_utilisateur`),
  KEY `idx_dates` (`date_reservation`,`date_souhaitee`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `reservations`
--

INSERT INTO `reservations` (`id_reservation`, `id_service`, `id_utilisateur`, `date_reservation`, `date_souhaitee`) VALUES
(9, 101, 1, '2025-11-20', '09:30:00'),
(10, 102, 2, '2025-11-21', '10:00:00'),
(11, 103, 3, '2025-11-22', '11:15:00'),
(12, 101, 4, '2025-11-23', '14:00:00'),
(13, 102, 1, '2025-11-24', '16:45:00'),
(14, 102, 10, '2025-11-15', '12:14:00'),
(15, 102, 10, '2025-11-21', '13:22:00'),
(16, 102, 10, '2025-11-15', '11:29:00'),
(17, 102, 10, '2025-11-21', '11:33:00');

-- --------------------------------------------------------

--
-- Structure de la table `services`
--

DROP TABLE IF EXISTS `services`;
CREATE TABLE IF NOT EXISTS `services` (
  `id_service` int NOT NULL AUTO_INCREMENT,
  `id_categorie` int NOT NULL,
  `titre` varchar(50) NOT NULL,
  `description` varchar(2000) NOT NULL,
  `localisation` varchar(50) NOT NULL,
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP,
  `actif` tinyint(1) DEFAULT '1',
  `cout` decimal(8,2) DEFAULT '0.00',
  `nom_image` varchar(255) DEFAULT NULL,
  `id_utilisateur` int NOT NULL,
  PRIMARY KEY (`id_service`),
  KEY `id_categorie` (`id_categorie`),
  KEY `nom` (`id_utilisateur`),
  KEY `idx_services_categorie` (`id_categorie`),
  KEY `idx_services_utilisateur` (`id_utilisateur`),
  KEY `idx_services_actif_date` (`actif`,`date_creation`)
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `services`
--

INSERT INTO `services` (`id_service`, `id_categorie`, `titre`, `description`, `localisation`, `date_creation`, `actif`, `cout`, `nom_image`, `id_utilisateur`) VALUES
(101, 11, 'Partenariat Tennis (Intermédiaire)', 'Recherche partenaire pour matchs amicaux intensifs.', 'Parc Central', '2025-11-10 01:35:35', 1, 5.00, '20251114_101652.png', 10),
(102, 12, 'Massage sportif - 60 min', 'Récupération musculaire après effort.', 'Local 101', '2025-11-10 01:35:35', 1, 30.00, 'massage.jpg', 1),
(103, 10, 'Programme de Musculation', 'Plan d\'entraînement personnalisé (INACTIF).', 'En ligne', '2025-11-10 01:35:35', 0, 40.00, 'muscu.jpg', 2);

-- --------------------------------------------------------

--
-- Structure de la table `utilisateurs`
--

DROP TABLE IF EXISTS `utilisateurs`;
CREATE TABLE IF NOT EXISTS `utilisateurs` (
  `id_utilisateur` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenom` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `courriel` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mot_de_passe` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credit` decimal(10,2) NOT NULL DEFAULT '0.00',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'utilisateur',
  PRIMARY KEY (`id_utilisateur`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id_utilisateur`, `nom`, `prenom`, `courriel`, `mot_de_passe`, `credit`, `role`) VALUES
(4, 'Admin', 'Garneau', 'admin@garneau.ca', 'sha256$n3dYlU31g7dD2a9v$2b5b48192b0f3408665f973e6593a213e4b31336181b676a6610338981e4b39b', 120.00, 'admin'),
(10, 'user2', 'noName', 'user2@gmail.com', '5c05d25b14799ac1cfbc8a5f45109855e9fd5dd50ff910144f480371978413cb9da91446e524be1aab3a7bcdcc5a76552945596f7a065fdfb9be4610a062a9e0', 70.00, 'utilisateur'),
(22, 'aicha', 'edwige', 'admin2@garneau.ca', '5c05d25b14799ac1cfbc8a5f45109855e9fd5dd50ff910144f480371978413cb9da91446e524be1aab3a7bcdcc5a76552945596f7a065fdfb9be4610a062a9e0', 100.00, 'admin');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
