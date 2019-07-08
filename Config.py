# -*- coding: utf-8 -*-
from configparser import ConfigParser

# 初始化类
cp = ConfigParser()
cp.read("setting.cfg", encoding='utf-8')

# 得到所有的section，以列表的形式返回
section = cp.sections()[0]

DBHOST = cp.get(section, "DBHOST") if cp.has_option(section, "DBHOST") else "39.108.101.181"

DBPORT = cp.getint(section, "DBPORT") if cp.has_option(section, "DBPORT") else 3306

DBUSER = cp.get(section, "DBUSER") if cp.has_option(section, "DBUSER") else "root"

DBPWD = cp.get(section, "DBPWD") if cp.has_option(section, "DBPWD") else "Aa000000!"

DBNAME = cp.get(section, "DBNAME") if cp.has_option(section, "DBNAME") else "company_info"

DBCHAR = cp.get(section, "DBCHAR") if cp.has_option(section, "DBCHAR") else "utf-8"

