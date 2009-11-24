-- phpMyAdmin SQL Dump
-- version 3.2.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Oct 21, 2009 at 10:53 AM
-- Server version: 5.1.37
-- PHP Version: 5.2.10

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- Database: `otalo`
--

-- --------------------------------------------------------

--
-- Table structure for table `Forum`
--

CREATE TABLE IF NOT EXISTS `Forum` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `BriefDescFile` varchar(24) NOT NULL,
  `LongDescFile` varchar(24) NOT NULL,
  `Owner` int(11) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `Forum`
--


-- --------------------------------------------------------

--
-- Table structure for table `Message`
--

CREATE TABLE IF NOT EXISTS `Message` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DatePosted` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Author` varchar(24) NOT NULL,
  `InReplyTo` int(11) NOT NULL,
  `Forum` int(11) NOT NULL,
  `SubjectFile` varchar(24) NOT NULL,
  `ContentFile` varchar(24) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `DatePosted` (`DatePosted`,`Author`,`InReplyTo`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=10 ;

--
-- Dumping data for table `Message`
--

INSERT INTO `Message` (`ID`, `DatePosted`, `Author`, `InReplyTo`, `Forum`, `SubjectFile`, `ContentFile`) VALUES
(4, '2009-09-21 12:13:08', '1001', 0, 0, '', '1253560375.wav'),
(5, '2009-09-21 12:22:36', '1001', 0, 0, '', '1253560951.wav'),
(6, '2009-09-21 16:35:15', '1001', 0, 0, '', '1253576107.wav'),
(7, '2009-09-21 16:38:30', '1001', 0, 0, '', '1253576304.wav'),
(8, '2009-09-25 10:28:31', '1001', 0, 0, '', '1253899660.wav'),
(9, '2009-09-25 10:29:51', '1001', 0, 0, '', '1253899786.wav');

-- --------------------------------------------------------

--
-- Table structure for table `User`
--

CREATE TABLE IF NOT EXISTS `User` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `PhoneNumber` varchar(24) NOT NULL,
  `Pin` varchar(8) NOT NULL,
  `NameFile` varchar(24) NOT NULL,
  `LocationFile` varchar(24) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `PhoneNumber` (`PhoneNumber`),
  KEY `PhoneNumber_2` (`PhoneNumber`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `User`
--
