
-- Head 1

-- bank table
CREATE TABLE `bank_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bank_name` varchar(50) DEFAULT NULL,
  `account_no` varchar(50) DEFAULT NULL,
  `status` int(11) DEFAULT 0,
  `entry_by` varchar(30) DEFAULT NULL,
  `entry_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB

CREATE TABLE `journal_voucher` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `head_id` int(11) DEFAULT NULL,
  `trans_type` varchar(20) NOT NULL,
  `trans_mode` varchar(20) DEFAULT NULL,
  `trans_date` varchar(100) DEFAULT NULL,
  `trans_amount` decimal(10,2) DEFAULT NULL,
  `remarks` varchar(200) NOT NULL,
  `entry_by` varchar(15) NOT NULL,
  `entry_time` datetime NOT NULL,
  `bank_acc_id` varchar(80) NOT NULL,
  `cheque_no` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB

CREATE TABLE `ustility_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `utility_name` varchar(150) DEFAULT NULL,
  `utility_rate` decimal(10,2) DEFAULT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
)


CREATE TABLE `product_suplier` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `SupplierName` varchar(150) NOT NULL DEFAULT '',
  `Address` varchar(100) NOT NULL,
  `ContactNo` varchar(100) NOT NULL,
  `deed` varchar(250) DEFAULT NULL COMMENT 'deed', 
  `isActive` int(11) NOT NULL DEFAULT 1,
  `isManufacturer` int(1) DEFAULT 0 COMMENT '0= just a supplier, 1=supplier+manufacturer',
  `EntryUser` varchar(50) NOT NULL,
  `EntryTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
)

