**Alys Web Server**

Simple project made for fun, it requires Python, php, and php-cgi to run.

The base directory is html/ - Root requests will first look for index.php, then index.html.

404 Errors can be customised for each site, it will first look for html/currentSite/404.html (If hosting multiple sites), and if that doesn't exist it will then look for html/404.html. If neither of those exist, it will serve a simple 404 error message instead.

Only UTF-8 is currently supported. In php, POST and SESSION are currently not supported either.

**Multiple sites simultaneously**

Alys can serve from a different folder depending on what host the request comes from.
```ini
[SiteName]
host=localhost
dir=local
```
The above example will use html/local when accessed from http://localhost - 
You can add as many of these as you like.


**Supported file types**

HTML, CSS, JS, PHP, jpg, png, gif, mp3, ogg, wav
