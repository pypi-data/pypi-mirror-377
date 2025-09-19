import datetime
import re
import time
from dataclasses import dataclass
from enum import Enum
from itertools import repeat
from logging import Logger
from typing import Any, Generator, List, Tuple, Type, cast
from urllib.parse import quote

import humanize
from currency_converter import CurrencyConverter  # type: ignore
from playwright.sync_api import Browser, ElementHandle, Page  # type: ignore
from rich.pretty import pretty_repr

from .listing import Listing
from .marketplace import ItemConfig, Marketplace, MarketplaceConfig, WebPage
from .utils import (
    BaseConfig,
    CounterItem,
    KeyboardMonitor,
    Translator,
    convert_to_seconds,
    counter,
    doze,
    extract_price,
    hilight,
    is_substring,
)


class Condition(Enum):
    NEW = "new"
    USED_LIKE_NEW = "used_like_new"
    USED_GOOD = "used_good"
    USED_FAIR = "used_fair"


class DateListed(Enum):
    ANYTIME = 0
    PAST_24_HOURS = 1
    PAST_WEEK = 7
    PAST_MONTH = 30


class DeliveryMethod(Enum):
    LOCAL_PICK_UP = "local_pick_up"
    SHIPPING = "shipping"
    ALL = "all"


class Availability(Enum):
    ALL = "all"
    INSTOCK = "in"
    OUTSTOCK = "out"


class Category(Enum):
    VEHICLES = "vehicles"
    PROPERTY_RENTALS = "propertyrentals"
    APPAREL = "apparel"
    ELECTRONICS = "electronics"
    ENTERTAINMENT = "entertainment"
    FAMILY = "family"
    FREE_STUFF = "freestuff"
    FREE = "free"
    GARDEN = "garden"
    HOBBIES = "hobbies"
    HOME_GOODS = "homegoods"
    HOME_IMPROVEMENT = "homeimprovement"
    HOME_SALES = "homesales"
    MUSICAL_INSTRUMENTS = "musicalinstruments"
    OFFICE_SUPPLIES = "officesupplies"
    PET_SUPPLIES = "petsupplies"
    SPORTING_GOODS = "sportinggoods"
    TICKETS = "tickets"
    TOYS = "toys"
    VIDEO_GAMES = "videogames"


@dataclass
class FacebookMarketItemCommonConfig(BaseConfig):
    """Item options that can be defined in marketplace

    This class defines and processes options that can be specified
    in both marketplace and item sections, specific to facebook marketplace
    """

    seller_locations: List[str] | None = None
    availability: List[str] | None = None
    condition: List[str] | None = None
    date_listed: List[int] | None = None
    delivery_method: List[str] | None = None
    category: str | None = None

    def handle_seller_locations(self: "FacebookMarketItemCommonConfig") -> None:
        if self.seller_locations is None:
            return

        if isinstance(self.seller_locations, str):
            self.seller_locations = [self.seller_locations]
        if not isinstance(self.seller_locations, list) or not all(
            isinstance(x, str) for x in self.seller_locations
        ):
            raise ValueError(f"Item {hilight(self.name)} seller_locations must be a list.")

    def handle_availability(self: "FacebookMarketItemCommonConfig") -> None:
        if self.availability is None:
            return

        if isinstance(self.availability, str):
            self.availability = [self.availability]
        if not all(val in [x.value for x in Availability] for val in self.availability):
            raise ValueError(
                f"Item {hilight(self.name)} availability must be one or two values of 'all', 'in', and 'out'."
            )
        if len(self.availability) > 2:
            raise ValueError(
                f"Item {hilight(self.name)} availability must be one or two values of 'all', 'in', and 'out'."
            )

    def handle_condition(self: "FacebookMarketItemCommonConfig") -> None:
        if self.condition is None:
            return
        if isinstance(self.condition, Condition):
            self.condition = [self.condition]
        if not isinstance(self.condition, list) or not all(
            isinstance(x, str) and x in [cond.value for cond in Condition] for x in self.condition
        ):
            raise ValueError(
                f"Item {hilight(self.name)} condition must be one or more of that can be one of 'new', 'used_like_new', 'used_good', 'used_fair'."
            )

    def handle_date_listed(self: "FacebookMarketItemCommonConfig") -> None:
        if self.date_listed is None:
            return
        if not isinstance(self.date_listed, list):
            self.date_listed = [self.date_listed]
        #
        new_values: List[int] = []
        for val in self.date_listed:
            if isinstance(val, str):
                if val.isdigit():
                    new_values.append(int(val))
                elif val.lower() == "all":
                    new_values.append(DateListed.ANYTIME.value)
                elif val.lower() == "last 24 hours":
                    new_values.append(DateListed.PAST_24_HOURS.value)
                elif val.lower() == "last 7 days":
                    new_values.append(DateListed.PAST_WEEK.value)
                elif val.lower() == "last 30 days":
                    new_values.append(DateListed.PAST_MONTH.value)
                else:
                    raise ValueError(
                        f"""Item {hilight(self.name)} date_listed must be one of 1, 7, and 30, or All, Last 24 hours, Last 7 days, Last 30 days.: {self.date_listed} provided."""
                    )
            elif isinstance(val, (int, float)):
                if int(val) not in [x.value for x in DateListed]:
                    raise ValueError(
                        f"""Item {hilight(self.name)} date_listed must be one of 1, 7, and 30, or All, Last 24 hours, Last 7 days, Last 30 days.: {self.date_listed} provided."""
                    )
                new_values.append(int(val))
            else:
                raise ValueError(
                    f"""Item {hilight(self.name)} date_listed must be one of 1, 7, and 30, or All, Last 24 hours, Last 7 days, Last 30 days.: {self.date_listed} provided."""
                )
        # new_values should have length 1 or 2
        if len(new_values) > 2:
            raise ValueError(
                f"""Item {hilight(self.name)} date_listed must have one or two values."""
            )
        self.date_listed = new_values

    def handle_delivery_method(self: "FacebookMarketItemCommonConfig") -> None:
        if self.delivery_method is None:
            return

        if isinstance(self.delivery_method, str):
            self.delivery_method = [self.delivery_method]

        if len(self.delivery_method) > 2:
            raise ValueError(
                f"Item {hilight(self.name)} delivery_method must be one or two values of 'local_pick_up' and 'shipping'."
            )

        if not isinstance(self.delivery_method, list) or not all(
            val in [x.value for x in DeliveryMethod] for val in self.delivery_method
        ):
            raise ValueError(
                f"Item {hilight(self.name)} delivery_method must be one of 'local_pick_up' and 'shipping'."
            )

    def handle_category(self: "FacebookMarketItemCommonConfig") -> None:
        if self.category is None:
            return

        if not isinstance(self.category, str) or self.category not in [x.value for x in Category]:
            raise ValueError(
                f"Item {hilight(self.name)} category must be one of {', '.join(x.value for x in Category)}."
            )


@dataclass
class FacebookMarketplaceConfig(MarketplaceConfig, FacebookMarketItemCommonConfig):
    """Options specific to facebook marketplace

    This class defines and processes options that can be specified
    in the marketplace.facebook section only. None of the options are required.
    """

    login_wait_time: int | None = None
    password: str | None = None
    username: str | None = None

    def handle_username(self: "FacebookMarketplaceConfig") -> None:
        if self.username is None:
            return

        if not isinstance(self.username, str):
            raise ValueError(f"Marketplace {self.name} username must be a string.")

    def handle_password(self: "FacebookMarketplaceConfig") -> None:
        if self.password is None:
            return

        if not isinstance(self.password, str):
            raise ValueError(f"Marketplace {self.name} password must be a string.")

    def handle_login_wait_time(self: "FacebookMarketplaceConfig") -> None:
        if self.login_wait_time is None:
            return
        if isinstance(self.login_wait_time, str):
            try:
                self.login_wait_time = convert_to_seconds(self.login_wait_time)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                raise ValueError(
                    f"Marketplace {self.name} login_wait_time {self.login_wait_time} is not recognized."
                ) from e
        if not isinstance(self.login_wait_time, int) or self.login_wait_time < 0:
            raise ValueError(
                f"Marketplace {self.name} login_wait_time should be a non-negative number."
            )


@dataclass
class FacebookItemConfig(ItemConfig, FacebookMarketItemCommonConfig):
    pass


class FacebookMarketplace(Marketplace):
    initial_url = "https://www.facebook.com/login/device-based/regular/login/"

    name = "facebook"

    def __init__(
        self: "FacebookMarketplace",
        name: str,
        browser: Browser | None,
        keyboard_monitor: KeyboardMonitor | None = None,
        logger: Logger | None = None,
    ) -> None:
        assert name == self.name
        super().__init__(name, browser, keyboard_monitor, logger)
        self.page: Page | None = None

    @classmethod
    def get_config(cls: Type["FacebookMarketplace"], **kwargs: Any) -> FacebookMarketplaceConfig:
        return FacebookMarketplaceConfig(**kwargs)

    @classmethod
    def get_item_config(cls: Type["FacebookMarketplace"], **kwargs: Any) -> FacebookItemConfig:
        return FacebookItemConfig(**kwargs)

    def login(self: "FacebookMarketplace") -> None:
        assert self.browser is not None

        self.page = self.create_page(swap_proxy=True)

        # Navigate to the URL, no timeout
        self.goto_url(self.initial_url)

        if self.logger:
            self.logger.debug("[Login] Checking for cookie consent pop-up...")
        try:
            allow_button_locator = self.page.get_by_role(
                "button",
                name=re.compile(r"Allow all cookies|Allow cookies|Accept All", re.IGNORECASE),
            )

            if allow_button_locator.is_visible():
                allow_button_locator.click()
                self.page.wait_for_timeout(2000)  # 2 seconds
                if self.logger:
                    self.logger.debug(
                        f"""{hilight("[Login]", "succ")} Allow all cookies' button clicked."""
                    )
            elif self.logger:
                self.logger.debug(
                    f"{hilight('[Login]', 'succ')} Cookie consent pop-up not found or not visible within timeout."
                )
        except Exception as e:
            if self.logger:
                self.logger.warning(
                    f"{hilight('[Login]', 'fail')} Could not handle cookie pop-up (or it was not present): {e!s}"
                )

        self.config: FacebookMarketplaceConfig
        try:
            if self.config.username:
                time.sleep(2)
                selector = self.page.wait_for_selector('input[name="email"]')
                if selector is not None:
                    selector.type(self.config.username, delay=250)
            if self.config.password:
                time.sleep(2)
                selector = self.page.wait_for_selector('input[name="pass"]')
                if selector is not None:
                    selector.type(self.config.password, delay=250)
            if self.config.username and self.config.password:
                time.sleep(2)
                selector = self.page.wait_for_selector('button[name="login"]')
                if selector is not None:
                    selector.click()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.error(f"""{hilight("[Login]", "fail")} {e}""")

        # in case there is a need to enter additional information
        login_wait_time = (
            60 if self.config.login_wait_time is None else self.config.login_wait_time
        )
        if login_wait_time > 0:
            if self.logger:
                self.logger.info(
                    f"""{hilight("[Login]", "info")} Waiting {humanize.naturaldelta(login_wait_time)}"""
                    + (
                        f""" or press {hilight("Esc")} when you are ready."""
                        if self.keyboard_monitor is not None
                        else ""
                    )
                )
            doze(login_wait_time, keyboard_monitor=self.keyboard_monitor)

    def search(
        self: "FacebookMarketplace", item_config: FacebookItemConfig
    ) -> Generator[Listing, None, None]:
        if not self.page:
            self.login()
            assert self.page is not None

        options = []

        condition = item_config.condition or self.config.condition
        if condition:
            options.append(f"itemCondition={'%2C'.join(condition)}")

        # availability can take values from item_config, or marketplace config and will
        # use the first or second value depending on how many times the item has been searched.
        if item_config.date_listed:
            date_listed = item_config.date_listed[0 if item_config.searched_count == 0 else -1]
        elif self.config.date_listed:
            date_listed = self.config.date_listed[0 if item_config.searched_count == 0 else -1]
        else:
            date_listed = DateListed.ANYTIME.value
        if date_listed is not None and date_listed != DateListed.ANYTIME.value:
            options.append(f"daysSinceListed={date_listed}")

        # delivery_method can take values from item_config, or marketplace config and will
        # use the first or second value depending on how many times the item has been searched.
        if item_config.delivery_method:
            delivery_method = item_config.delivery_method[
                0 if item_config.searched_count == 0 else -1
            ]
        elif self.config.delivery_method:
            delivery_method = self.config.delivery_method[
                0 if item_config.searched_count == 0 else -1
            ]
        else:
            delivery_method = DeliveryMethod.ALL.value
        if delivery_method is not None and delivery_method != DeliveryMethod.ALL.value:
            options.append(f"deliveryMethod={delivery_method}")

        # availability can take values from item_config, or marketplace config and will
        # use the first or second value depending on how many times the item has been searched.
        if item_config.availability:
            availability = item_config.availability[0 if item_config.searched_count == 0 else -1]
        elif self.config.availability:
            availability = self.config.availability[0 if item_config.searched_count == 0 else -1]
        else:
            availability = Availability.ALL.value
        if availability is not None and availability != Availability.ALL.value:
            options.append(f"availability={availability}")

        # search multiple keywords and cities
        # there is a small chance that search by different keywords and city will return the same items.
        found = {}
        search_city = item_config.search_city or self.config.search_city or []
        city_name = item_config.city_name or self.config.city_name or []
        radiuses = item_config.radius or self.config.radius
        currencies = item_config.currency or self.config.currency

        # this should not happen because `Config.validate_items` has checked this
        if not search_city:
            if self.logger:
                self.logger.error(
                    f"""{hilight("[Search]", "fail")} No search city provided for {item_config.name}"""
                )
        # increase the searched_count to differentiate first and subsequent searches
        item_config.searched_count += 1
        for city, cname, radius, currency in zip(
            search_city,
            repeat(None) if city_name is None else city_name,
            repeat(None) if radiuses is None else radiuses,
            repeat(None) if currencies is None else currencies,
        ):
            marketplace_url = f"https://www.facebook.com/marketplace/{city}/search?"

            if radius:
                # avoid specifying radius more than once
                if options and options[-1].startswith("radius"):
                    options.pop()
                options.append(f"radius={radius}")

            max_price = item_config.max_price or self.config.max_price
            if max_price:
                if max_price.isdigit():
                    options.append(f"maxPrice={max_price}")
                else:
                    price, cur = max_price.split(" ", 1)
                    if currency and cur != currency:
                        c = CurrencyConverter()
                        price = str(int(c.convert(int(price), cur, currency)))
                        if self.logger:
                            self.logger.debug(
                                f"""{hilight("[Search]", "info")} Converting price {max_price} {cur} to {price} {currency}"""
                            )
                    options.append(f"maxPrice={price}")

            min_price = item_config.min_price or self.config.min_price
            if min_price:
                if min_price.isdigit():
                    options.append(f"minPrice={min_price}")
                else:
                    price, cur = min_price.split(" ", 1)
                    if currency and cur != currency:
                        c = CurrencyConverter()
                        price = str(int(c.convert(int(price), cur, currency)))
                        if self.logger:
                            self.logger.debug(
                                f"""{hilight("[Search]", "info")} Converting price {max_price} {cur} to {price} {currency}"""
                            )
                    options.append(f"minPrice={price}")

            category = item_config.category or self.config.category
            if category:
                options.append(f"category={category}")
                if category == Category.FREE_STUFF.value or category == Category.FREE.value:
                    # find min_price= and max_price= in options and remove them
                    options = [
                        x
                        for x in options
                        if not x.startswith("minPrice=") and not x.startswith("maxPrice=")
                    ]

            for search_phrase in item_config.search_phrases:
                if self.logger:
                    self.logger.info(
                        f"""{hilight("[Search]", "info")} Searching {item_config.marketplace} for """
                        f"""{hilight(item_config.name)} from {hilight(cname or city)}"""
                        + (f" with radius={radius}" if radius else " with default radius")
                    )

                self.goto_url(
                    marketplace_url + "&".join([f"query={quote(search_phrase)}", *options])
                )

                found_listings = FacebookSearchResultPage(
                    self.page, self.translator, self.logger
                ).get_listings()
                time.sleep(5)
                if self.logger:
                    self.logger.error(
                        f"""{hilight("[Search]", "fail")} Failed to get search results for {search_phrase} from {city}"""
                    )

                counter.increment(CounterItem.SEARCH_PERFORMED, item_config.name)

                # go to each item and get the description
                # if we have not done that before
                for listing in found_listings:
                    if listing.post_url.split("?")[0] in found:
                        continue
                    if self.keyboard_monitor is not None and self.keyboard_monitor.is_paused():
                        return
                    counter.increment(CounterItem.LISTING_EXAMINED, item_config.name)
                    found[listing.post_url.split("?")[0]] = True
                    # filter by title and location; skip keyword filtering since we do not have description yet.
                    if not self.check_listing(listing, item_config, description_available=False):
                        counter.increment(CounterItem.EXCLUDED_LISTING, item_config.name)
                        continue
                    try:
                        details, from_cache = self.get_listing_details(
                            listing.post_url,
                            item_config,
                            price=listing.price,
                            title=listing.title,
                        )
                        if not from_cache:
                            time.sleep(5)
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        if self.logger:
                            self.logger.error(
                                f"""{hilight("[Retrieve]", "fail")} Failed to get item details: {e}"""
                            )
                        continue
                    # currently we trust the other items from summary page a bit better
                    # so we do not copy title, description etc from the detailed result
                    for attr in ("condition", "seller", "description"):
                        # other attributes should be consistent
                        setattr(listing, attr, getattr(details, attr))
                    listing.name = item_config.name
                    if self.logger:
                        self.logger.debug(
                            f"""{hilight("[Retrieve]", "succ")} New item "{listing.title}" from {listing.post_url} is sold by "{listing.seller}" and with description "{listing.description[:100]}..." """
                        )

                    # Warn if we never managed to extract a description for keyword-based filtering
                    if (
                        (not listing.description or len(listing.description.strip()) == 0)
                        and item_config.keywords
                        and len(item_config.keywords) > 0
                        and self.logger
                    ):
                        self.logger.debug(
                            f"""{hilight("[Error]", "fail")} Failed to extract description for {hilight(listing.title)} at {listing.post_url}. Keyword filtering will only apply to title."""
                        )

                    if self.check_listing(listing, item_config):
                        yield listing
                    else:
                        counter.increment(CounterItem.EXCLUDED_LISTING, item_config.name)

    def get_listing_details(
        self: "FacebookMarketplace",
        post_url: str,
        item_config: ItemConfig,
        price: str | None = None,
        title: str | None = None,
    ) -> Tuple[Listing, bool]:
        assert post_url.startswith("https://www.facebook.com")
        details = Listing.from_cache(post_url)
        if (
            details is not None
            and (price is None or details.price == price)
            and (title is None or details.title == title)
        ):
            # if the price and title are the same, we assume everything else is unchanged.
            return details, True

        if not self.page:
            self.login()

        assert self.page is not None
        self.goto_url(post_url)
        counter.increment(CounterItem.LISTING_QUERY, item_config.name)
        details = parse_listing(self.page, post_url, self.translator, self.logger)
        if details is None:
            raise ValueError(
                f"Failed to get item details of listing {post_url}. "
                "The listing might be missing key information (e.g. seller) or not in English."
                "Please add option language to your marketplace configuration is the latter is the case. See https://github.com/BoPeng/ai-marketplace-monitor?tab=readme-ov-file#support-for-non-english-languages for details."
            )
        details.to_cache(post_url)
        return details, False

    def check_listing(
        self: "FacebookMarketplace",
        item: Listing,
        item_config: FacebookItemConfig,
        description_available: bool = True,
    ) -> bool:
        # get antikeywords from both item_config or config
        antikeywords = item_config.antikeywords
        if antikeywords and (
            is_substring(antikeywords, item.title + " " + item.description, logger=self.logger)
        ):
            if self.logger:
                self.logger.info(
                    f"""{hilight("[Skip]", "fail")} Exclude {hilight(item.title)} due to {hilight("excluded keywords", "fail")}: {", ".join(antikeywords)}"""
                )
            return False

        # if the return description does not contain any of the search keywords
        keywords = item_config.keywords
        if (
            description_available
            and keywords
            and not (
                is_substring(keywords, item.title + "  " + item.description, logger=self.logger)
            )
        ):
            if self.logger:
                self.logger.info(
                    f"""{hilight("[Skip]", "fail")} Exclude {hilight(item.title)} {hilight("without required keywords", "fail")} in title and description."""
                )
            return False

        # get locations from either marketplace config or item config
        if item_config.seller_locations is not None:
            allowed_locations = item_config.seller_locations
        else:
            allowed_locations = self.config.seller_locations or []
        if allowed_locations and not is_substring(
            allowed_locations, item.location, logger=self.logger
        ):
            if self.logger:
                self.logger.info(
                    f"""{hilight("[Skip]", "fail")} Exclude {hilight("out of area", "fail")} item {hilight(item.title)} from location {hilight(item.location)}"""
                )
            return False

        # get exclude_sellers from both item_config or config
        if item_config.exclude_sellers is not None:
            exclude_sellers = item_config.exclude_sellers
        else:
            exclude_sellers = self.config.exclude_sellers or []
        if (
            item.seller
            and exclude_sellers
            and is_substring(exclude_sellers, item.seller, logger=self.logger)
        ):
            if self.logger:
                self.logger.info(
                    f"""{hilight("[Skip]", "fail")} Exclude {hilight(item.title)} sold by {hilight("banned seller", "failed")} {hilight(item.seller)}"""
                )
            return False

        return True


class FacebookSearchResultPage(WebPage):
    def _get_listings_elements_by_children_counts(self: "FacebookSearchResultPage"):
        parent: ElementHandle | None = self.page.locator("img").first.element_handle()
        # look for parent of parent until it has more than 10 children
        children = []
        while parent:
            children = parent.query_selector_all(":scope > *")
            if len(children) > 10:
                break
            parent = parent.query_selector("xpath=..")
        # find each listing
        valid_listings = []
        try:
            for listing in children:
                if not listing.text_content():
                    continue
                valid_listings.append(listing)
        except Exception as e:
            # this error should be tolerated
            if self.logger:
                self.logger.debug(
                    f"{hilight('[Retrieve]', 'fail')} Some grid item cannot be read: {e}"
                )
        return valid_listings

    def _get_listing_elements_by_traversing_header(self: "FacebookSearchResultPage"):
        heading = self.page.locator(
            f'[aria-label="{self.translator("Collection of Marketplace items")}"]'
        )
        if not heading:
            return []

        grid_items = heading.locator(
            ":scope > :first-child > :first-child > :nth-child(3) > :first-child > :nth-child(2) > div"
        )
        # find each listing
        valid_listings = []
        try:
            for listing in grid_items.all():
                if not listing.text_content():
                    continue
                valid_listings.append(listing.element_handle())
        except Exception as e:
            # this error should be tolerated
            if self.logger:
                self.logger.debug(
                    f"{hilight('[Retrieve]', 'fail')} Some grid item cannot be read: {e}"
                )
        return valid_listings

    def get_listings(self: "FacebookSearchResultPage") -> List[Listing]:
        # if no result is found
        btn = self.page.locator(f"""span:has-text('{self.translator("Browse Marketplace")}')""")
        if btn.count() > 0:
            if self.logger:
                msg = self._parent_with_cond(
                    btn.first,
                    lambda x: len(x) == 3
                    and self.translator("Browse Marketplace") in (x[-1].text_content() or ""),
                    1,
                )
                self.logger.info(f"{hilight('[Retrieve]', 'dim')} {msg}")
            return []

        # find the grid box
        try:
            valid_listings = (
                self._get_listing_elements_by_traversing_header()
                or self._get_listings_elements_by_children_counts()
            )
        except KeyboardInterrupt:
            raise
        except Exception as e:
            filename = datetime.datetime.now().strftime("debug_%Y%m%d_%H%M%S.html")
            if self.logger:
                self.logger.error(
                    f"{hilight('[Retrieve]', 'fail')} failed to parse searching result. Page saved to {filename}: {e}"
                )
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.page.content())
            return []

        listings: List[Listing] = []
        for idx, listing in enumerate(valid_listings):
            try:
                atag = listing.query_selector(
                    ":scope > :first-child > :first-child > :first-child > :first-child > :first-child > :first-child > :first-child > :first-child"
                )
                if not atag:
                    continue
                post_url = atag.get_attribute("href") or ""
                details_divs = atag.query_selector_all(":scope > :first-child > div")
                if not details_divs:
                    continue
                details = details_divs[1]
                divs = details.query_selector_all(":scope > div")
                raw_price = "" if len(divs) < 1 else divs[0].text_content() or ""
                title = "" if len(divs) < 2 else divs[1].text_content() or ""
                # location can be empty in some rare cases
                location = "" if len(divs) < 3 else (divs[2].text_content() or "")

                # get image
                img = listing.query_selector("img")
                image = img.get_attribute("src") if img else ""
                price = extract_price(raw_price)

                if post_url.startswith("/"):
                    post_url = f"https://www.facebook.com{post_url}"

                if image.startswith("/"):
                    image = f"https://www.facebook.com{image}"

                listings.append(
                    Listing(
                        marketplace="facebook",
                        name="",
                        id=post_url.split("?")[0].rstrip("/").split("/")[-1],
                        title=title,
                        image=image,
                        price=price,
                        # all the ?referral_code&referral_sotry_type etc
                        # could be helpful for live navigation, but will be stripped
                        # for caching item details.
                        post_url=post_url,
                        location=location,
                        condition="",
                        seller="",
                        description="",
                    )
                )
            except KeyboardInterrupt:
                raise
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"{hilight('[Retrieve]', 'fail')} Failed to parse search results {idx + 1} listing: {e}"
                    )
                continue
        return listings


class FacebookItemPage(WebPage):
    def verify_layout(self: "FacebookItemPage") -> bool:
        return True

    def get_title(self: "FacebookItemPage") -> str:
        raise NotImplementedError("get_title is not implemented for this page")

    def get_price(self: "FacebookItemPage") -> str:
        raise NotImplementedError("get_price is not implemented for this page")

    def get_image_url(self: "FacebookItemPage") -> str:
        raise NotImplementedError("get_image_url is not implemented for this page")

    def get_seller(self: "FacebookItemPage") -> str:
        raise NotImplementedError("get_seller is not implemented for this page")

    def get_description(self: "FacebookItemPage") -> str:
        raise NotImplementedError("get_description is not implemented for this page")

    def get_location(self: "FacebookItemPage") -> str:
        raise NotImplementedError("get_location is not implemented for this page")

    def get_condition(self: "FacebookItemPage") -> str:
        raise NotImplementedError("get_condition is not implemented for this page")

    def parse(self: "FacebookItemPage", post_url: str) -> Listing:
        if not self.verify_layout():
            raise ValueError("Layout mismatch")

        # title
        title = self.get_title()
        price = self.get_price()
        description = self.get_description()

        if not title or not price or not description:
            raise ValueError(f"Failed to parse {post_url}")

        if self.logger:
            self.logger.info(f"{hilight('[Retrieve]', 'succ')} Parsing {hilight(title)}")
        res = Listing(
            marketplace="facebook",
            name="",
            id=post_url.split("?")[0].rstrip("/").split("/")[-1],
            title=title,
            image=self.get_image_url(),
            price=extract_price(price),
            post_url=post_url,
            location=self.get_location(),
            condition=self.get_condition(),
            description=description,
            seller=self.get_seller(),
        )
        if self.logger:
            self.logger.debug(f"{hilight('[Retrieve]', 'succ')} {pretty_repr(res)}")
        return cast(Listing, res)


class FacebookRegularItemPage(FacebookItemPage):
    def verify_layout(self: "FacebookRegularItemPage") -> bool:
        return any(
            self.translator("Condition") in (x.text_content() or "")
            for x in self.page.query_selector_all("li")
        )

    def get_title(self: "FacebookRegularItemPage") -> str:
        try:
            h1_element = self.page.query_selector_all("h1")[-1]
            return h1_element.text_content() or self.translator("**unspecified**")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""

    def get_price(self: "FacebookRegularItemPage") -> str:
        try:
            price_element = self.page.locator("h1 + *")
            return price_element.text_content() or self.translator("**unspecified**")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""

    def get_image_url(self: "FacebookRegularItemPage") -> str:
        try:
            image_url = self.page.locator("img").first.get_attribute("src") or ""
            return image_url
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""

    def get_seller(self: "FacebookRegularItemPage") -> str:
        try:
            seller_link = self.page.locator("//a[contains(@href, '/marketplace/profile')]").last
            return seller_link.text_content() or self.translator("**unspecified**")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"{hilight('[Error]', 'fail')} get_seller failed: {type(e).__name__}: {e}"
                )
            return ""

    def get_description(self: "FacebookRegularItemPage") -> str:
        try:
            # Find the span with text "condition", then parent, then next...
            description_element = self.page.locator(
                f'span:text("{self.translator("Condition")}") >> xpath=ancestor::ul[1] >> xpath=following-sibling::*[1]'
            )
            return description_element.text_content() or self.translator("**unspecified**")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""

    def get_condition(self: "FacebookRegularItemPage") -> str:
        try:
            if self.logger:
                self.logger.debug(f"{hilight('[Debug]', 'info')} Getting condition info...")
            # Find the span with text "condition", then parent, then next...
            condition_text = self.translator("Condition")

            # Use .first property to avoid strict mode violation when multiple elements match
            # This handles cases where "Condition" appears in both the label and description text
            condition_locator = self.page.locator(f'span:text("{condition_text}")')
            condition_element = condition_locator.first

            result = self._parent_with_cond(
                condition_element,
                lambda x: len(x) >= 2
                and self.translator("Condition") in (x[0].text_content() or ""),
                1,
            )
            return result
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"{hilight('[Error]', 'fail')} get_condition failed: {type(e).__name__}: {e}"
                )
            return ""

    def get_location(self: "FacebookRegularItemPage") -> str:
        try:
            # look for "Location is approximate", then find its neighbor
            approximate_element = self.page.locator(
                f'span:text("{self.translator("Location is approximate")}")'
            )
            return self._parent_with_cond(
                approximate_element,
                lambda x: len(x) == 2
                and self.translator("Location is approximate") in (x[1].text_content() or ""),
                0,
            )
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""


class FacebookRentalItemPage(FacebookRegularItemPage):
    def verify_layout(self: "FacebookRentalItemPage") -> bool:
        # there is a header h2 with text Description
        return any(
            self.translator("Description") in (x.text_content() or "")
            for x in self.page.query_selector_all("h2")
        )

    def get_description(self: "FacebookRentalItemPage") -> str:
        # some pages do not have a condition box and appears to have a "Description" header
        # See https://github.com/BoPeng/ai-marketplace-monitor/issues/29 for details.
        try:
            description_header = self.page.query_selector(
                f'h2:has(span:text("{self.translator("Description")}"))'
            )
            return self._parent_with_cond(
                description_header,
                lambda x: len(x) > 1 and x[0].text_content() == self.translator("Description"),
                1,
            )
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""

    def get_condition(self: "FacebookRentalItemPage") -> str:
        # no condition information for rental items
        return self.translator("**unspecified**")


class FacebookAutoItemWithAboutAndDescriptionPage(FacebookRegularItemPage):
    def _has_about_this_vehicle(self: "FacebookAutoItemWithAboutAndDescriptionPage") -> bool:
        return any(
            self.translator("About this vehicle") in (x.text_content() or "")
            for x in self.page.query_selector_all("h2")
        )

    def _has_seller_description(self: "FacebookAutoItemWithAboutAndDescriptionPage") -> bool:
        return any(
            self.translator("Seller's description") in (x.text_content() or "")
            for x in self.page.query_selector_all("h2")
        )

    def _get_about_this_vehicle(self: "FacebookAutoItemWithAboutAndDescriptionPage") -> str:
        try:
            about_element = self.page.locator(
                f'h2:has(span:text("{self.translator("About this vehicle")}"))'
            )
            return self._parent_with_cond(
                # start from About this vehicle
                about_element,
                # find an array of elements with the first one being "About this vehicle"
                lambda x: len(x) > 1
                and self.translator("About this vehicle") in (x[0].text_content() or ""),
                # Extract all texts from the elements
                lambda x: "\n".join([child.text_content() or "" for child in x]),
            )
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""

    def _get_seller_description(self: "FacebookAutoItemWithAboutAndDescriptionPage") -> str:
        try:
            description_header = self.page.query_selector(
                f"""h2:has(span:text("{self.translator("Seller's description")}"))"""
            )

            return self._parent_with_cond(
                # start from the description header
                description_header,
                # find an array of elements with the first one being "Seller's description"
                lambda x: len(x) > 1
                and self.translator("Seller's description") in (x[0].text_content() or ""),
                # then, drill down from the second child
                lambda x: self._children_with_cond(
                    x[1],
                    # find the an array of elements
                    lambda y: len(y) > 1,
                    # and return the texts.
                    lambda y: f"""\n\n{self.translator("Seller's description")}\n\n{y[0].text_content() or self.translator("**unspecified**")}""",
                ),
            )
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""

    def verify_layout(self: "FacebookAutoItemWithAboutAndDescriptionPage") -> bool:
        # there is a header h2 with text "About this vehicle"
        return self._has_about_this_vehicle() and self._has_seller_description()

    def get_description(self: "FacebookAutoItemWithAboutAndDescriptionPage") -> str:
        return self._get_about_this_vehicle() + self._get_seller_description()

    def get_price(self: "FacebookAutoItemWithAboutAndDescriptionPage") -> str:
        description = self.get_description()
        # using regular expression to find text that looks like price in the description
        price_pattern = r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:,\d{2})?"
        match = re.search(price_pattern, description)
        return match.group(0) if match else self.translator("**unspecified**")

    def get_condition(self: "FacebookAutoItemWithAboutAndDescriptionPage") -> str:
        # no condition information for auto items
        return self.translator("**unspecified**")


class FacebookAutoItemWithDescriptionPage(FacebookAutoItemWithAboutAndDescriptionPage):
    def verify_layout(self: "FacebookAutoItemWithDescriptionPage") -> bool:
        return self._has_seller_description() and not self._has_about_this_vehicle()

    def get_description(self: "FacebookAutoItemWithDescriptionPage") -> str:
        try:
            description_header = self.page.query_selector(
                f"""h2:has(span:text("{self.translator("Seller's description")}"))"""
            )

            return self._parent_with_cond(
                # start from the description header
                description_header,
                # find an array of elements with the first one being "Seller's description"
                lambda x: len(x) > 1
                and self.translator("Seller's description") in (x[0].text_content() or ""),
                # then, drill down from the second child
                lambda x: self._children_with_cond(
                    x[1],
                    # find the an array of elements
                    lambda y: len(y) > 2,
                    # and return the texts.
                    lambda y: f"""\n\n{self.translator("Seller's description")}\n\n{y[1].text_content() or self.translator("**unspecified**")}""",
                ),
            )
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""

    def get_condition(self: "FacebookAutoItemWithDescriptionPage") -> str:
        try:
            description_header = self.page.query_selector(
                f"""h2:has(span:text("{self.translator("Seller's description")}"))"""
            )

            res = self._parent_with_cond(
                # start from the description header
                description_header,
                # find an array of elements with the first one being "Seller's description"
                lambda x: len(x) > 1
                and self.translator("Seller's description") in (x[0].text_content() or ""),
                # then, drill down from the second child
                lambda x: self._children_with_cond(
                    x[1],
                    # find the an array of elements
                    lambda y: len(y) > 2,
                    # and return the texts after seller's description.
                    lambda y: y[0].text_content() or self.translator("**unspecified**"),
                ),
            )
            if res.startswith(self.translator("Condition")):
                res = res[len(self.translator("Condition")) :]
            return res.strip()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""

    def get_price(self: "FacebookAutoItemWithDescriptionPage") -> str:
        # for this page, price is after header
        try:
            h1_element = self.page.query_selector_all("h1")[-1]
            header = h1_element.text_content()
            return self._parent_with_cond(
                # start from the header
                h1_element,
                # find an array of elements with the first one being "Seller's description"
                lambda x: len(x) > 1 and header in (x[0].text_content() or ""),
                # then, find the element after header
                1,
            )
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if self.logger:
                self.logger.debug(f"{hilight('[Retrieve]', 'fail')} {e}")
            return ""


def parse_listing(
    page: Page, post_url: str, translator: Translator | None = None, logger: Logger | None = None
) -> Listing | None:
    supported_facebook_item_layouts = [
        FacebookRentalItemPage,
        FacebookAutoItemWithAboutAndDescriptionPage,
        FacebookAutoItemWithDescriptionPage,
        FacebookRegularItemPage,
    ]

    for page_model in supported_facebook_item_layouts:
        try:
            return page_model(page, translator, logger).parse(post_url)
        except KeyboardInterrupt:
            raise
        except Exception:
            # try next page ayout
            continue
    return None
