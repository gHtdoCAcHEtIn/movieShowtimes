
### argument 1 [$moviequery] : search query for google.com/movies
### argument 2 [$location]   : search near (default = 94043)
### www.google.com/movies?q=$moviequery&near=$location


import requests
import re
import itertools
import simplejson, urllib

def main():
  #print 'TODAY\n-----'
  getMovieResults(movie='pixels', location='94043')
  #print 'TOMORROW\n--------'
  getMovieResults(movie='pixels', location='94043', date='1')
  getMovieResults(movie='antman', location='94002', date='0')
  #print('all movie results for today\n---------------------')
  #getMovieResults(movie='', location='94043', date='0')
  
  
def getMovieResults(movie='pixels', location='94043', date='0'):
  
  rootUrl = "http://www.google.com/movies"
  payload = {'q': movie, 'near': location, 'date': date}
  
  ### clean up payload
  for k, v in payload.items():
    if v == '':
      del payload[k]
  
  htmlSource = requests.get(rootUrl, params=payload)
  print('[' + htmlSource.url + ']')
  
  movieNamePattern = "<h2 itemprop=\"name\">.*?<a href=.*?>(.*?)</a>.*?</h2>"
  movieList = re.split(movieNamePattern, htmlSource.text)

  #print len(movieList), len(movieList)/2
  dataBase = list()
  for i in range(len(movieList)/2):
    #print movie
    movieName = movieList[2*i+1]
    #print movieName
    movieData = movieList[2*i+1+1]
    #print movieData
    #theatreNamePattern = "<div class=theater>.*?<div class=name.*?>.*?<a href=.*?>(.*?)</a>"
    theaterNamePattern = "<div class=theater>.*?<div class=name><a href=.*?>(.*?)</a></div><div class=address>(.*?)<a href=.*?></a></div>"
    results = re.split(theaterNamePattern, movieData)
    
    for j in range(len(results)/3):
      theatreName = results[3*j+1]
      theatreAddress = results[3*j+1+1]
      
      ### drive time to theatre
      driveTimeUrl = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(location,theatreAddress)
      driveTimeResult= simplejson.load(urllib.urlopen(driveTimeUrl))
      driveTime = driveTimeResult['rows'][0]['elements'][0]['duration']['text']
      
      showtimesData = results[3*j+3]
      #print(showtimesData)
      showtimesPattern = "<a href=.*?http://www.fandango.com/.*?date.*?(\d\d\d\d-\d\d-\d\d).*?(\d\d:\d\d).*?>.*?</a>"
      #showtimesPattern = "(\d\d:\d\d).*?>.*?</a>"
      movieShowtimes = re.findall(showtimesPattern, showtimesData)
      n = len(movieShowtimes)
      dataBase.extend([(date, time, movieName, theatreName, driveTime, theatreAddress) for (date, time) in movieShowtimes])

  #print dataBase
  ### sort dataBase by showtime
  dataBase.sort(key=lambda x: x[1])
  displayString = '{0:<10}  {1:<6}  {2:<30}  {3:<30}  {4:<10}  {5:<50}'
  if len(dataBase) > 0:
    print displayString.format('DATE', 'TIME', 'MOVIE', 'THEATRE', 'DRIVE TIME', 'ADDRESS')
    print displayString.format('----', '----', '-----', '-------', '----------', '-------')
    for idx, x in enumerate(dataBase):
      if (idx < 10): print displayString.format(x[0], x[1], x[2], x[3], x[4], x[5])


main()