#!/usr/bin/python3

import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import ChromeOptions, ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located as presence
from typing import List
from datetime import datetime
import logging
import json
import argparse
import getpass
import sys
from os import path
import re

class Tweet:
    def __init__(self, username, profile, tweetlink, tweet, replies, likes, post_time):
        self.username = username
        self.profile = profile
        self.tweetlink = tweetlink
        self.tweet = tweet
        self.replies = replies
        self.likes = likes
        self.time = post_time

    def toJson(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o:o.__dict__)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Tweet):
            return False
        return self.tweetlink == value.tweetlink

    def __repr__(self) -> str:
        return f"Username:{self.username}\nProfile:{self.profile}\n{self.tweet}\nReplies:{self.replies}\tLikes:{self.likes}\nLink:{self.tweetlink}\nTime:{self.time}"


class Profile:
    def __init__(self, vname, username, desc, location, joinDate, following, followers):
        self.visible_name = vname
        self.username = username
        self.description = desc
        self.location = location
        self.joinDate = joinDate
        self.following = following
        self.followers = followers

    def toJson(self):
        return json.dumps(self, ensure_ascii=False ,default=lambda o:o.__dict__)

class News:
    def __init__(self, headline, time, category):
        self.headline = headline
        self.time = time
        self.category = category

    def __eq__(self, other:object) -> bool:
        if not isinstance(other, News):
            return False
        return self.headline == other.headline

    def toJson(self):
        return json.dumps(self, ensure_ascii=False ,default=lambda o:o.__dict__)

def has_news(news_list: List[News], news : News):
    for n in news_list:
        if news == n:
            return True
    return False

def has_tweet(tweet_list : List[Tweet], tweet : Tweet):
    for twt in tweet_list:
        if twt == tweet:
            return True
    return False

def get_user_element(div_user : WebElement):
    try:
        user_link = div_user.find_element(By.TAG_NAME, value="a")
        return user_link
    except Exception as e:
        logging.error("User Link could not be Extracted.")

def get_tweet_time(div_user : WebElement):
    try:
        timeElement = div_user.find_element(By.TAG_NAME, "time")
        post_time = timeElement.get_attribute("datetime")
        return post_time
    except Exception as e:
        logging.error("Get Time Element could not be Extracted (Ads don't have time...).")
        return ""

def get_profile_link(user_link : WebElement):
    try:
        return user_link.get_attribute("href")
    except Exception as e:
        logging.error("Profile Link could not be Extracted.")
        return ""
    
def get_profile_name(user_element: WebElement):
    try:
        user_spans = user_element.find_elements(By.TAG_NAME, "span")
        username = ""
        for us in user_spans:
            if username != us.text:
                username += us.text
        return username
    except Exception as e:
        logging.error("Cannot Extract Username.")
        return ""

def get_tweet_text(div_twt : WebElement):
    try:
        twt_span = div_twt.find_elements(By.TAG_NAME, value="span")
        return " ".join([sp.text for sp in twt_span])
    except Exception as e:
        logging.error("Tweet text extraction fail miserably which makes this script useless.")
        return ""
    
def get_replies(div_grp : WebElement):
    try:
        reply_btn = div_grp.find_element(By.CSS_SELECTOR, "button[data-testid='reply']")
        reply_btn_spns = reply_btn.find_elements(By.TAG_NAME, "span")
        replies = ""
        for spn in reply_btn_spns:
            if replies != spn.text:
                replies += spn.text
        return replies if replies != "" else 0
    except Exception as e:
        logging.error("Extracting replies from tweet failed.")
        return ""

def get_likes(div_grp : WebElement):
    try:
        like_btn = div_grp.find_element(By.CSS_SELECTOR, "button[data-testid='like']")
        like_btn_spns = like_btn.find_elements(By.TAG_NAME, "span")
        likes = ""
        for spn in like_btn_spns:
            if likes != spn.text:
                likes += spn.text
        return likes if likes != "" else 0
    except Exception as e:
        logging.error("Extracting likes from tweet failed.")
        return ""
    
def get_tweet_link(div_grp : WebElement):
    try:
        anlytcs = div_grp.find_elements(By.TAG_NAME, "a")
        tweet_link = ""
        for al in anlytcs:
            temp = al.get_attribute("href")
            if temp.endswith("analytics"):
                tweet_link = temp[:-10]
                break
        return tweet_link
    except Exception as e:
        logging.error("Tweet Link Extraction Failed.")
        return ""

def parse_articles(articles : WebElement) -> List[Tweet]:
    tweets = []
    to_be_parsed = len(articles)
    logging.info(f"article size is {to_be_parsed}")
    for article in articles:
        try:
            div_user = article.find_element(By.CSS_SELECTOR, value="div[data-testid='User-Name']")
            user_element = get_user_element(div_user)
            if user_element == None:
                continue
            post_time = get_tweet_time(div_user)
            user = get_profile_link(user_element)
            username = get_profile_name(user_element)
            div_twt = article.find_element(By.CSS_SELECTOR, value="div[data-testid='tweetText']")
            twt = get_tweet_text(div_twt)
            div_grp = article.find_element(By.CSS_SELECTOR, "div[role='group']")
            replies = get_replies(div_grp)
            likes = get_likes(div_grp)
            tweet_link = get_tweet_link(div_grp)
            tweets.append(Tweet(username,user, tweet_link, twt, replies, likes, post_time))
        except Exception as e:
            logging.error("Tweet Parse Failed. Ads or Twitter weirdness may cause this don't bother.")
            continue
    logging.info(f"{len(tweets)} of {to_be_parsed} articles parsed.")
    return tweets

def get_name_tuple(user_element : WebElement):
    try:
        user_data = user_element.find_elements(By.TAG_NAME, value='span')
        user_values = "".join([x.text for x in user_data]).split('@')
        return user_values
    except Exception as e:
        logging.error("Profile Name Parse Failed.")
        return ["",""]

def get_user_description(description_element : WebElement):
    try:
        description_data = description_element.find_elements(By.TAG_NAME, value="span")
        description_values = " ".join([x.text for x in description_data if x.text != ' '])
        return description_values
    except Exception as e:
        logging.error("User Description Parse Failed.")
        return ""

def get_profile_location(location_element : WebElement):
    try:
        location_data = location_element.find_elements(By.TAG_NAME, value='span')
        location_values = location_data[0].text
        return location_values
    except:
        logging.error("Location Parse Failed.")
        return ""
    
def get_profile_creation(join_element : WebElement):
    try:
        join_data = join_element.find_elements(By.TAG_NAME, value='span')
        join_values = join_data[0].text
        return join_values
    except Exception as e:
        logging.error("Join Date Parse Failed.")
        return ""
    
def get_follower_data(user_element : WebElement):
    try:
        top_div = user_element.find_element(By.XPATH, "..")
        alinks = top_div.find_elements(By.TAG_NAME, value='a')
        fwing = ""
        fwrs = ""
        for elem in alinks:
            if "following" in elem.get_property("href"):
                fgspan = elem.find_elements(By.TAG_NAME, value='span')
                fwing = fgspan[0].text
            if "verified_followers" in elem.get_property("href"):
                vfspan = elem.find_elements(By.TAG_NAME, value='span')
                fwrs = vfspan[0].text
        return fwing, fwrs    
    except Exception as ex:
        logging.error("Follower data parse failed.")
        return "",""

def output_profile_data(profile : Profile):
    try:
        filename = f"{profile.username}.json"
        with open(filename, 'w') as f:
            f.write(profile.toJson())
        logging.info(f"{profile.username} data saved successfully.")
    except Exception as e:
        logging.error("Cannot save profile data file.")

def get_profile_data(browser : webdriver.Chrome):
    try:
        user_element = browser.find_element(By.CSS_SELECTOR, value="div[data-testid='UserName']")
        user_values = get_name_tuple(user_element)
        description_element = browser.find_element(By.CSS_SELECTOR, value="div[data-testid='UserDescription']")
        description_values = get_user_description(description_element)
        location_element = browser.find_element(By.CSS_SELECTOR, value="span[data-testid='UserLocation']")
        location_values = get_profile_location(location_element)
        join_element = browser.find_element(By.CSS_SELECTOR, value="span[data-testid='UserJoinDate']")
        join_value = get_profile_creation(join_element)
        following, followers = get_follower_data(user_element)
        p = Profile(user_values[0], f"@{user_values[1]}", description_values, location_values, join_value, following, followers)
        output_profile_data(p)
    except Exception as ex:
        logging.error("Profile Data Extraction Failed.")
    finally:
        browser.quit()

def output_news_data(news : List[News]) -> bool:
    try:
        filename = "news_" + str(datetime.now().timestamp()) + ".json"
        logging.info(f"News will be saved to {filename}...")
        json_data = "[" + "\n,".join([json.dumps(item.toJson(), ensure_ascii=False, check_circular=False) for item in news]) + "]"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_data)
        logging.info(f"News saved to : {filename}")
        return True
    except Exception as e:
        logging.error("Following error occured :", e)
        return False

def extract_news(browser : webdriver.Chrome, number):
    try:
        news = []
        previous = -1
        failed_to_get = 0
        while len(news) < number:
            news_divs = browser.find_elements(By.CSS_SELECTOR, value="div[data-testid='trend']")
            for divs in news_divs:
                try:
                    spans = divs.find_elements(By.TAG_NAME, value="span")
                    hl = spans[0].text
                    tm, ctgry = spans[1].text.split("·",2)
                    nw = News(hl, tm, ctgry)
                    if not has_news(news, nw):
                        news.append(nw)
                except:
                    logging.error("Parsing a News Failed.")
                    continue
            js = f"window.scrollBy(0,750);"
            browser.execute_script(js)
            time.sleep(3)
            if previous != len(news):
                previous = len(news)
                failed_to_get = 0
            else:
                if failed_to_get < 3:
                    failed_to_get += 1
                    logging.warning(f"{failed_to_get} attemps to get news.")
                else:
                    break
            logging.info(f"{len(news)} distinct news item extracted so far.")
        if output_news_data(news):
            logging.info(f"Successfully Extracted {len(news)} news.")
        else:
            logging.error("Saving News Failed.")
    except KeyboardInterrupt:
        logging.critical("Shutting Down...")
        if len(news) > 0:
            if output_news_data(news):
                logging.info(f"Successfully Extracted {len(news)} news.")
            else:
                logging.error(f"Saving News Failed...")
    except Exception as e:
        logging.error("News Extraction Failed.")
    finally:
        browser.quit()

def extract_routine(browser : webdriver.Chrome,number, scroll, is_search = True):
    extracted_list = []
    log_string = "Tweets" if is_search else "Replies"
    bytag = By.TAG_NAME if is_search else By.CSS_SELECTOR
    bytag_value = "article" if is_search else "article[tabindex='0']"
    link = (browser.current_url).replace('/', '_')
    filename = f"replies_{link}_{str(datetime.now().timestamp())}.json" if not is_search else None
    previous = 0
    failed_to_get = 0
    start_time = time.perf_counter()
    try:
        while len(extracted_list) < number:
            articles = browser.find_elements(bytag, bytag_value)
            js = f"window.scrollBy(0,{scroll});"
            browser.execute_script(js)
            time.sleep(3)
            scroll = 2500
            twt = parse_articles(articles)
            for t in twt:
                if not has_tweet(extracted_list, t):
                    extracted_list.append(t)
            logging.info(f"Number of distinct {log_string} extracted so far : {len(extracted_list)}")
            if previous != len(extracted_list):
                previous = len(extracted_list)
                failed_to_get = 0
            else:
                if failed_to_get < 3:
                    failed_to_get += 1
                    logging.warning(f"{failed_to_get} attemps to get replies failed.")
                else:
                    break
        if output_json(extracted_list, filename):
            elapsed = round(time.perf_counter() - start_time, 3)
            logging.info(f"Successfully Extracted {len(extracted_list)} {log_string} in {elapsed} secs.")
        else:
            logging.error(f"Saving {log_string} Failed...")
    except KeyboardInterrupt:
        logging.critical("Shutting Down...")
        if len(extracted_list) > 0:
            if output_json(extracted_list, filename):
                elapsed = round(time.perf_counter() - start_time, 3)
                logging.info(f"Successfully Extracted {len(extracted_list)} {log_string} in {elapsed} secs.")
            else:
                logging.error(f"Saving {log_string} Failed...")
    except Exception as e:
        logging.error("Error Ocurred Extracting Tweets.")
        if len(extracted_list) > 0:
            output_json(extracted_list, filename)
    finally:
        browser.quit()

def get_tweet_replies(browser : webdriver.Chrome, number):
    try:  
        section = WebDriverWait(browser, 10).until(
                presence((By.TAG_NAME, "section"))
            )
        article = section.find_element(By.CSS_SELECTOR, value="article[tabindex='-1']")
        initial = article.find_element(By.CSS_SELECTOR, value="button[data-testid='reply']")
        rep_text = initial.get_attribute("aria-label").split(" ")[0]
        logging.info(f"Number of total replies to Tweet: {rep_text}")
        number = int(rep_text) if int(rep_text) < number else number
        extract_routine(browser, number, 500, False)
    except Exception as ex:
        logging.error("Parsing Replies Failed.")

def output_json(tweets : List[Tweet], filename = None) -> bool:
    try:
        if filename == None:
            filename = "output_" + str(datetime.now().timestamp()) + ".json"
        logging.info(f"Tweets will be saved to {filename}...")
        json_data = "[" + "\n,".join([json.dumps(item.toJson(), ensure_ascii=False, check_circular=False) for item in tweets]) + "]"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_data)
        logging.info(f"Tweets saved to : {filename}")
        return True
    except Exception as e:
        logging.error("Following error occured :", e)
        return False

def get_web_driver(headless):
    try:
        if not path.exists("/usr/local/bin/chromedriver"):
            logging.critical("ChromeDriver is not in the required path : '/usr/local/bin/chromedriver'")
            sys.exit("Please fix the issue and re-run.")
        service = ChromeService(executable_path="/usr/local/bin/chromedriver")
        options = ChromeOptions()
        if headless:
            logging.info("Running in Headless Mode.")
            options.add_argument("--headless=new")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("disable-infobars")
        browser = webdriver.Chrome(options=options, service=service)
        browser.implicitly_wait(5)
        browser.maximize_window()
        return browser
    except Exception as e:
        logging.error("Following Error Occured :", e)

def login(browser : webdriver.Chrome, email, phone, password):
    try:
        browser.get("https://www.x.com/login")
        time.sleep(2)
        username_text = browser.find_element(by=By.NAME, value="text")
        username_text.send_keys(email + Keys.RETURN)
        time.sleep(2)
        pwd = browser.find_element(by=By.NAME, value="password")
        pwd.send_keys(password + Keys.RETURN)
        logging.info("Login Successfull.")
    except NoSuchElementException as ex:
        logging.warning("Element Not Found")
        phone_text = browser.find_element(by=By.NAME, value="text")
        phone_text.send_keys(phone + Keys.RETURN)
        time.sleep(2)
        pwd = browser.find_element(by=By.NAME, value="password")
        pwd.send_keys(password + Keys.RETURN)

def save_cookie(cookies : List[dict]):
    content = []
    for c in cookies:
        content.append(json.dumps(c))
    with open("xitter", 'w') as f:
        for c in content:
            f.writelines(c + "\n")
    logging.info(f"Cookies saved for : x.com")

def read_cookies() -> List[dict]:
    cookies = []
    content = []
    with open("xitter", "r") as f:
        content = f.readlines()
    for line in content:
        cookies.append(json.loads(line))
    return cookies

def search_tweets(browser : webdriver.Chrome, search_term : str, latest, number):
    if search_term.startswith("#"):
        search_term = "%23" + search_term[1:]
    try:
        if latest:
            browser.get(f"https://x.com/search?q={search_term}&src=typed_query")
            section = WebDriverWait(browser, 30).until(
                presence((By.TAG_NAME, "section"))
            )
            extract_routine(browser, number, 0)
        else:
            browser.get(f"https://x.com/search?q={search_term}&src=trend_click&f=live&vertical=trends")
            section = WebDriverWait(browser, 30).until(
                presence((By.TAG_NAME, "section"))
            )
            extract_routine(browser, number, 500)
    except Exception as e:
        logging.error("Error Ocurred Extracting Tweets.")

def parse_news(browser: webdriver.Chrome, number):
    try:
        browser.get("https://x.com/explore/tabs/news")
        section = WebDriverWait(browser, 30).until(
                presence((By.TAG_NAME, "section"))
        )
        extract_news(browser, number)
    except Exception as e:
        logging.error("Error occured Extracting news.")

def main(args, username, email, password, login_with_cookie = False):
    hless = args.headless
    browser = get_web_driver(hless);
    if login_with_cookie:
        browser.get("https://www.x.com")
        cookies = read_cookies()
        for c in cookies:
            browser.add_cookie(c)
        browser.refresh()
        form = WebDriverWait(browser, 30).until(
             presence((By.TAG_NAME, "input"))
        )
    else:
        login(browser, username, email, password)
        form = WebDriverWait(browser, 30).until(
             presence((By.TAG_NAME, "input"))
        )
    cookies = browser.get_cookies()
    save_cookie(cookies)
    if args.search != None:
        top = args.top
        number = args.number
        term = args.search
        time.sleep(5)
        search_tweets(browser, term, top, number)
    elif args.news == True:
        num = args.number
        parse_news(browser, num)
    elif args.profile != None:
        pattern = r"((http|https)://)(www.x.com/|x.com/)[a-zA-Z0-9_]+"
        check = re.compile(pattern)
        link = args.profile
        if check.match(link).group() != link:
            logging.error("I can only extract profile data from x.com.")
        else:
            browser.get(link)
            wait = WebDriverWait(browser, 10).until(
                presence((By.CSS_SELECTOR, "div[data-testid='UserName']"))     
            )
            get_profile_data(browser)
    else:
        pattern = r"((http|https)://)(www.x.com/|x.com/)[a-zA-Z0-9_]+(/status/)[0-9]+"
        check = re.compile(pattern)
        link = args.replies
        if check.match(link).group() != link:
            logging.error("I can only extract replies from x.com tweets.")
        else:
            number = args.number
            browser.get(link)
            wait = WebDriverWait(browser, 10).until(
                presence((By.CSS_SELECTOR, "div[aria-label='Timeline: Conversation']"))
            )
            get_tweet_replies(browser, number)
    
    
if __name__ == "__main__":
    print("""
                '||' '|'   .                             .                   
          ....    || |   .||.  ... ..   ....     ....  .||.    ...   ... ..  
        .|...||    ||     ||    ||' '' '' .||  .|   ''  ||   .|  '|.  ||' '' 
        ||        | ||    ||    ||     .|' ||  ||       ||   ||   ||  ||     
         '|...' .|   ||.  '|.' .||.    '|..'|'  '|...'  '|.'  '|..|' .||.    
                                                                     
                            Version : 0b0001
      ------------------------------------------------------------------------
      Written for certain individual so he doesn't get bored and post polls :))
            Also his eye-balls can relax a bit during UKRiots. 
      
                                !!! Attention !!!
          Using This Script doesn't comply with the X Terms of Service and doing so 
          may result in the PERMANENT SUSPENSION of your account.
          Using your personal account with this script is NOT RECOMMENDED!!!
          Create a Disposable Account. YOU HAVE BEEN WARNED!!!
      
                    Find me on Twitter - @Oceancholic.
      ------------------------------------------------------------------------
    """)
    parser = argparse.ArgumentParser(prog="eXtractor", description="This is not meant to be a production grade script but a weekend fun to make a free alternative to X API.")
    parser.add_argument("-s", "--search", type=str, help="Tag to search '#twitterWasBetterB4Elon', TwitterRocksElonSucks, '#IOwnMyAccountNotElon' etc.", metavar=(""))
    parser.add_argument("-t", "--top", action='store_true', help="Flag to search for Top Tweets only")
    parser.add_argument("-p", "--profile", help="link to a profile to get Profile Data", metavar=(""))
    parser.add_argument("-r", "--replies", help="Link to a tweet to get replies from", metavar=(""))
    parser.add_argument("-n", "--number", type=int, default=200, help="Number Of Tweets to get (default ~200)", metavar=(""))
    parser.add_argument("-c", "--credential", help="Credentials file is useful for managing multiple accounts (see format in github repo)", metavar=(""))
    parser.add_argument("--news", action='store_true', help="Get News from Explore tab (Beta)")
    parser.add_argument("--headless", action='store_true',help="Do not open Browser Windows.")
    parser.add_argument("--version", action='version', version="%(prog)s version 0b0001")
    args = parser.parse_args()
    log_format = ' %(asctime)s : %(levelname)-10s -- %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)
    if args.profile == None and args.search == None and args.replies == None and args.news != True:
        logging.error("At least one of the options are required (search / profile / replies / news)")
        parser.print_help()
    else:
        if args.credential != None:
            if path.exists(args.credential):
                info = []
                with open(args.credential, 'r') as f:
                    info = f.readlines()
                email = info[0]
                username = info[1]
                password = info[2]
                main(args, info[0], info[1], info[2])
            else:
                logging.critical("File Not Found!")
        else:
            if path.exists("xitter"):
                logging.info("Trying To Login with Cookies...")
                main(args,"","","",True)
            else:
                username = input("Enter your Username : ")
                email = input("Enter Your Email :")
                password = getpass.getpass("Enter Your Twitter Password: ")
                main(args, username, email, password)
