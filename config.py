from configparser import ConfigParser
from typing import Generator, List, Union
from core.client import Client
from pathlib import Path

from core.types import SearchCriteria, Age

from functools import partial


def safe_get(config: ConfigParser, section: str, key: str) -> str | None:
    return config.get(section, key, fallback=None)


def get_config(path: Union[str, Path] = "config.ini") -> ConfigParser:
    config = ConfigParser()
    config.read(path)
    return config


def parse_age_string(s: str, btw_chr: str = "-", in_btw_chr: str = ",") -> List[Age]:
    result = list()
    for age in s.split(btw_chr):
        _from, to = age.split(in_btw_chr)
        result.append({"from": int(_from), "to": int(to)})
    return result


def parse_search_criteria(config: ConfigParser, name: str) -> SearchCriteria:
    criteria: SearchCriteria
    criteria = {
        "group": 0,
        "userSex": "ANY",
        "peerSex": "ANY",
    }
    user_sex = config.get(name, "sex", fallback=None)
    search_sex = config.get(name, "search-sex", fallback=None)
    user_age = config.get(name, "age", fallback=None)
    search_age = config.get(name, "search-age", fallback=None)
    if user_sex and user_age and search_sex and search_age:
        criteria["userSex"] = user_sex
        criteria["peerSex"] = search_sex
        criteria["userAge"] = parse_age_string(user_age)[0]
        criteria["peerAges"] = parse_age_string(search_age)
        return criteria
    else:
        return criteria


def parse_clients_config(
    path: Union[str, Path] = "config.ini",
) -> Generator[Client, None, None]:
    config = get_config(path=path)
    names_of_clients = config.get("settings", "clients")
    for name in names_of_clients.replace(" ", "").split(","):
        option = f"client/{name}"
        user_id = config.get(option, "user_id")
        ua = config.get(option, "ua")
        proxy = config.get(option, "proxy", fallback=None)
        wait_for = config.get(option, "wait-for", fallback=None)
        yield Client(
            name=name,
            user_id=user_id,
            ua=ua,
            search_criteria=parse_search_criteria(config, option),
            proxy=proxy,
            wait_for=wait_for,
        )


_discord_config = get_config()
load_discord = partial(_discord_config.get, "discord")
bool_load_discord = partial(_discord_config.getboolean, "discord", fallback=False)
load_safe_discord = partial(_discord_config.get, "discord", fallback=None)
