"""Configurations."""

import json
import logging
import logging.config
import os
import sys
from pathlib import Path

from rich.logging import RichHandler

# Configuration
NOCACHE = os.environ.get("SOCCERDATA_NOCACHE", 'False').lower() in ('true', '1', 't')
NOSTORE = os.environ.get("SOCCERDATA_NOSTORE", 'False').lower() in ('true', '1', 't')
LOGLEVEL = os.environ.get('SOCCERDATA_LOGLEVEL', 'INFO').upper()

# Directories
BASE_DIR = Path(os.environ.get("SOCCERDATA_DIR", Path.home() / "soccerdata"))
LOGS_DIR = Path(BASE_DIR, "logs")
DATA_DIR = Path(BASE_DIR, "data")
CONFIG_DIR = Path(BASE_DIR, "config")

# Create dirs
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Logger
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "minimal": {"format": "%(message)s"},
        "detailed": {
            "format": "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d]\n%(message)s\n"  # noqa: E501
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "minimal",
            "level": logging.DEBUG,
        },
        "info": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "info.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.INFO,
        },
        "error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "error.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.ERROR,
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console", "info", "error"],
            "level": LOGLEVEL,
            "propagate": True,
        },
    },
}
logging.config.dictConfig(logging_config)
logger = logging.getLogger("root")
logger.handlers[0] = RichHandler(markup=True)

# Team name replacements
TEAMNAME_REPLACEMENTS = {}
_f_custom_teamnname_replacements = CONFIG_DIR / "teamname_replacements.json"
if _f_custom_teamnname_replacements.is_file():
    with open(_f_custom_teamnname_replacements, encoding='utf8') as json_file:
        for team, to_replace_list in json.load(json_file).items():
            for to_replace in to_replace_list:
                TEAMNAME_REPLACEMENTS[to_replace] = team
    logger.info("Custom team name replacements loaded from %s.", _f_custom_teamnname_replacements)
else:
    logger.info(
        "No custom team name replacements found. You can configure these in %s.",
        _f_custom_teamnname_replacements,
    )


# League dict
LEAGUE_DICT = {
    "ENG-Premier League": {
        "WhoScored": "England - Premier League",
    },
    "ESP-La Liga": {
        "SoFIFA": "[Spain] La Liga",
        "WhoScored": "Spain - LaLiga",
    },
    "ITA-Serie A": {
        "WhoScored": "Italy - Serie A",
    },
    "GER-Bundesliga": {
        "WhoScored": "Germany - Bundesliga",
    },
    "FRA-Ligue 1": {
        "WhoScored": "France - Ligue 1",
    },
    "POR-Liga": {
        "WhoScored": "Portugal - Liga - Portugal",
    },
    "TUR-Super League": {
        "WhoScored": "Turkey - Super - Lig",
    },
    "NET-Eredevisie": {
        "WhoScored": "Netherlands - Eredivisie",
    },
    "ENG-Championship":{
        "WhoScored": "England - Championship",
    },
    "BEL-Jupiler Pro":{
        "WhoScored": "Belgium - Jupiler - Pro - League",
    },
    "GER-Bundesliga 2":{
        "WhoScored": "Germany - 2 - Bundesliga",
    }
}

_f_custom_league_dict = CONFIG_DIR / "league_dict.json"
if _f_custom_league_dict.is_file():
    with open(_f_custom_league_dict, encoding='utf8') as json_file:
        LEAGUE_DICT = {**LEAGUE_DICT, **json.load(json_file)}
    logger.info("Custom league dict loaded from %s.", _f_custom_league_dict)
else:
    logger.info(
        "No custom league dict found. You can configure additional leagues in %s.",
        _f_custom_league_dict,
    )