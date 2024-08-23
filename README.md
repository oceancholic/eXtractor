<pre>
                '||' '|'   .                             .                   
          ....    || |   .||.  ... ..   ....     ....  .||.    ...   ... ..  
        .|...||    ||     ||    ||' '' '' .||  .|   ''  ||   .|  '|.  ||' '' 
        ||        | ||    ||    ||     .|' ||  ||       ||   ||   ||  ||     
         '|...' .|   ||.  '|.' .||.    '|..'|'  '|...'  '|.'  '|..|' .||.    

</pre>

<div>
<h1>!!! Attention !!!</h1>
  <p>
          <h2>Using This Script doesn't comply with the X Terms of Service and doing so 
          may result in the PERMANENT SUSPENSION of your account.
          Using your personal account with this script is NOT RECOMMENDED!!!
          Create a Disposable Account. <br> YOU HAVE BEEN WARNED!!!</h2>
</p>
</div>

<p>This is not a production grade script but a weekend fun to make a free alternative to X API.<br>
  X web handles/loads tweets and their replies in a weird way (renders certain amount of tweets based on their tweet height img/gif etc.) to avoid AI scrapping their data from site and advertisements also adds some complexity.
</p><br> 
  <p>
    I tried to find an optimum scroll size and wait time to minimize errors and extract most tweets in shortest possible time yet it is lot slower (abt 220sec per ~200 posts) 
    than pulling data from legit X API. There could be still errors and way more room for improvement so contributions/collaborations and ideas are very very welcome!<br>
  </p>
  <p>License file is for the awesome <a href="https://github.com/SeleniumHQ/selenium">Selenium Library</a>
  </p>
<hr>

<h3>Usage</h3>
<hr>
<p>
    eXtractor script expects linux OS, Chromium browser and suitable <a href="https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json">ChromeDriver</a>
    to be installed at <br> "/usr/local/bin/chromedriver". <br> Please Dig Selenium Documentation for instructions.
  </p>
  <p>Python Selenium wrapper can be installed</p>
  <pre>
    pip3 install selenium
  </pre>
<hr>
<div>
  <h3>eXtractor has 3 modes of operation:</h3>
  <p>
    <ul>
      <li>Search For Hashtags and Keywords</li>
      <li>Get Profile data from supplied profile link</li>
      <li>Get Replies to a Tweet from supplied tweet link</li>
    </ul>
  </p>
</div>
<div>
  <h3>Also There is 3 Methods of Login</h3>
  <ul>
    <li>using credential file (format below)</li>
    <li>manually enter</li>
    <li>cookies</li>
  </ul>
  <hr>
  <h3>Using Credential File</h3>
  <p>Credential File consist of 3 lines</p>
  <ol>
    <li>First line is username without '@'</li>
    <li>second line is email address</li>
    <li>third line is password in plain text</li>
  </ol>
  <p>Example Credential File</p>
  <pre>
    shitposter_2024
    email@address.com
    v3ry53Cre7P@s5W0rD!
  </pre>
  <p>supply your credential file path name with -c or --credential argument</p>
  <pre>
    python3 eXtractor.py -c myFile.txt
  </pre>
  <p>
    Using Credential File is usefull when you manage multiple accounts for scapping data. Please be aware that keeping credentials in plain text file is not a good choice. Another good reason to use a "disposable account" with this script.
  </p>
  <hr>
  <h3>Manually Enter</h3>
  <p>
    if you do not have a saved cookie and didn't provide a credential file, script will kindly ask for your credentials interactively. (P.S. typed password won't show in cmd line.)
  </p>
  <hr>
  <h3>Cookies</h3>
  <p>
    Once you successfully Login by one of the above methods it will save your cookies into "xitter" file in the same directory(There is no special reason to call cookie file "xitter" so feel free to change for your personal enjoyment.). The next time you use the script you don't need to supply credential file it will read the cookies and authorize.<br>
    However you usually don't want your auth cookies lying around unencrypted! it's a good idea to delete them when you finished. There is a catch thou. X will constantly notify you "There was a Login from a new device...." if you don't use cookies and this is the main reason why I had the urge to add the cookie feature.
  </p>
</div>
<h3>Searching</h3>
<hr>
<p>
  Searching is made with the -s or --search flag followed by a search term. if you are going to search a hashtag write your term in quotes like "#TwitterRocksElonSucks", keywords does not require quotes.</p>
  <p>
  Additionally you can cap the number of results to be extracted by adding -n flag followed by a number. Default is ~200.
  </p>
  <p>
    Another option is -t --top flag. if you provide this flag it will search for "Top Tweets" otherwise you'll get latest ones.
  </p>
  <p>
  Results will be saved in json format in the same directory.<br> You can get bored while eXtractor is busy doing it's thing just hit CTRL+C to exit and it will save the tweets already downloaded before exit.
</p>
<pre>
  python3 eXtracted.py -s "#viraltweets" -n 1000 -t
</pre>
<h3>
  Profile Data
</h3>
<p>
  if you need information from a certain profile like description/location/joinDate use -p --profile flag followed by a profile link. number and top flags are irrelevant in this mode. 
</p>
<pre>
  python3 eXtractor.py -p https://x.com/debian
</pre>
<h3>
  Replies
</h3>
<p>
  When you need to get responses to a certain tweet or unroll a thread you can use -r --replies flag followed by a tweet link. Replies is not a recursive function so it will only get first level of replies. You can provide -n flag to increase the amount of replies to get(Default ~200).</p> 
<p>
  Whatever number you provide it will only return actual first level replies.  
</p>
<p>
  Replies will be saved in the same directory in json format same as the search function with "replies" prefix in the file name.
</p>
<pre>
  python3 eXtractor.py -r https://x.com/AnonymousUK2022/status/1825436338683781120
</pre>
