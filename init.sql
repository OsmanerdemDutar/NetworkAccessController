-- 1. radcheck: Kullanıcı kimlik bilgileri (Kullanıcı adı ve şifreler veya MAC adresleri burada duracak)
CREATE TABLE IF NOT EXISTS radcheck (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL DEFAULT '',
    attribute VARCHAR(64) NOT NULL DEFAULT '',
    op VARCHAR(2) NOT NULL DEFAULT '==',
    value VARCHAR(253) NOT NULL DEFAULT ''
);

-- 2. radreply: Kullanıcıya özel dönülecek özel yanıtlar
CREATE TABLE IF NOT EXISTS radreply (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL DEFAULT '',
    attribute VARCHAR(64) NOT NULL DEFAULT '',
    op VARCHAR(2) NOT NULL DEFAULT '=',
    value VARCHAR(253) NOT NULL DEFAULT ''
);

-- 3. radusergroup: Hangi kullanıcının hangi gruba (admin, guest, employee) ait olduğu
CREATE TABLE IF NOT EXISTS radusergroup (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) NOT NULL DEFAULT '',
    groupname VARCHAR(64) NOT NULL DEFAULT '',
    priority INTEGER NOT NULL DEFAULT 1
);

-- 4. radgroupreply: Yetkilendirme (VLAN atamaları gibi politikalar bu tablodan gruplara basılacak)
CREATE TABLE IF NOT EXISTS radgroupreply (
    id SERIAL PRIMARY KEY,
    groupname VARCHAR(64) NOT NULL DEFAULT '',
    attribute VARCHAR(64) NOT NULL DEFAULT '',
    op VARCHAR(2) NOT NULL DEFAULT '=',
    value VARCHAR(253) NOT NULL DEFAULT ''
);

-- 5. radacct: Accounting (Hesap yönetimi) kayıtları. Kim, ne zaman bağlandı, kaç byte veri harcadı?
CREATE TABLE IF NOT EXISTS radacct (
    radacctid BIGSERIAL PRIMARY KEY,
    acctsessionid VARCHAR(64) NOT NULL DEFAULT '',
    acctuniqueid VARCHAR(32) NOT NULL DEFAULT '',
    username VARCHAR(64) NOT NULL DEFAULT '',
    realm VARCHAR(64) DEFAULT '',
    nasipaddress INET NOT NULL,
    nasportid VARCHAR(32) DEFAULT NULL,
    nasporttype VARCHAR(32) DEFAULT NULL,
    acctstarttime TIMESTAMP WITH TIME ZONE NULL,
    acctupdatetime TIMESTAMP WITH TIME ZONE NULL,
    acctstoptime TIMESTAMP WITH TIME ZONE NULL,
    acctinterval INTEGER,
    acctsessiontime INTEGER,
    acctauthentic VARCHAR(32) DEFAULT NULL,
    connectinfo_start VARCHAR(128) DEFAULT NULL,
    connectinfo_stop VARCHAR(128) DEFAULT NULL,
    acctinputoctets BIGINT,
    acctoutputoctets BIGINT,
    calledstationid VARCHAR(50) NOT NULL DEFAULT '',
    callingstationid VARCHAR(50) NOT NULL DEFAULT '',
    acctterminatecause VARCHAR(32) NOT NULL DEFAULT '',
    servicetype VARCHAR(32) DEFAULT NULL,
    framedprotocol VARCHAR(32) DEFAULT NULL,
    framedipaddress INET NULL
);