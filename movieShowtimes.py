
### argument 1 [$moviequery] : search query for google.com/movies
### argument 2 [$location]   : search near (default = 94043)
### www.google.com/movies?q=$movieName&near=$location&date=0

import sys
import requests, re
import itertools
import simplejson, urllib

def main(args):
  if len(args) == 4:
    getMovieResults(movie=args[1], location=args[2], date=args[3])
  elif len(args) == 3:
    getAllMovieResults(location=args[1], date=args[2])
  
  #getMovieResults(movie='pixels', location='94043')
  #getMovieResults(movie='pixels', location='94043', date='1')
  #getMovieResults(movie='antman', location='94002', date='0')
  #getAllMovieResults('94043', '0')
  
def getAllMovieResults(location, date):

  if type(location) is str and location.isdigit() and len(location) == 5:
    if type(date) is str and date.isdigit() and (date == '0' or date == '1' or date == '2'):
      print(location, date)
    else:
      print("Bad date input")
  else:
    print("Bad zipcode input")

  rootUrl = "http://www.google.com/movies"
  payload = {'near': location, 'date': date}
  
  ### clean up payload
  for k, v in payload.items():
    if v == '':
      del payload[k]
  
  htmlSource = requests.get(rootUrl, params=payload)
  print('[' + htmlSource.url + ']')
  
  #movieNamePattern = "<h2 itemprop=\"name\">.*?<a href=.*?>(.*?)</a>.*?</h2>"
  theaterNamePattern = "<div class=theater>.*?<h2 class=name><a href=.*?>(.*?)</a></h2><div class=info>(.*?)<a href=.*?></a></div></div>"
  results_theaterNames = re.split(theaterNamePattern, htmlSource.text)

  dataBase = list()
  for i in range(len(results_theaterNames)/3):
    theaterName = results_theaterNames[3*i+1]
    #print(theaterName)
    
    theaterAddress = results_theaterNames[3*i+1+1]
    #print(theaterAddress)
    
    theaterData = results_theaterNames[3*i+1+1+1]
    #print(theatreData)
    
    
    ### drive time to theatre
    driveTimeUrl = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(location,theaterAddress)
    driveTimeResult= simplejson.load(urllib.urlopen(driveTimeUrl))
    driveTime = driveTimeResult['rows'][0]['elements'][0]['duration']['text']
    #print(driveTime)
    
    theaterDataPattern = "<div class=movie><div class=name><a href=.*?>(.*?)</a></div>"
    results_theaterData = re.split(theaterDataPattern, theaterData)
    
    for j in range(len(results_theaterData)/2):
      movieName = results_theaterData[2*j+1]
      #print(movieName)
      
      showtimesData = results_theaterData[2*j+1+1]
      #print(showtimesData)
      
      showtimesPattern = "<a href=.*?http://www.fandango.com/.*?date.*?(\d\d\d\d-\d\d-\d\d).*?(\d\d:\d\d).*?>.*?</a>"
      results_showtimes = re.findall(showtimesPattern, showtimesData)
      #print(results_showtimes)
      
      n = len(results_showtimes)
      #print n
      
      dataBase.extend([dict([('date', date), ('time', time), ('movieName', movieName), ('theater', theaterName), ('driveTime', driveTime), ('theaterAddress', theaterAddress)]) for (date, time) in results_showtimes])

  #print dataBase
  
  ### sort dataBase by showtime
  dataBase.sort(key=lambda x: x['time'])
  date0           = str(max([len(x['date']) for x in dataBase]))
  time0           = str(max([len(x['time']) for x in dataBase]))
  movie0          = str(max([len(x['movieName']) for x in dataBase]))
  theaterName0    = str(max([len(x['theater']) for x in dataBase]))
  driveTime0      = str(max([len(x['driveTime']) for x in dataBase]))
  theaterAddress0 = str(max([len(x['theaterAddress']) for x in dataBase]))
  
  displayString = '{{0:<{0}}}  {{1:<{1}}}  {{2:<{2}}}  {{3:<{3}}}  {{4:<{4}}}  {{5:<{5}}}'.format(date0, time0, movie0, theaterName0, driveTime0, theaterAddress0)
  #print(displayString)
  
  if len(dataBase) > 0:
    
    print(displayString.format('DATE', 'TIME', 'MOVIE', 'THEATER', 'DRIVE TIME', 'ADDRESS'))
    print(displayString.format('----', '----', '-----', '-------', '----------', '-------'))
    
    for idx, x in enumerate(dataBase):
      if (idx < 25): 
        print(displayString.format(x['date'], x['time'], x['movieName'], x['theater'], x['driveTime'], x['theaterAddress']))



def getMovieResults(movie, location, date):
  
  if type(movie) is str and len(movie) > 0:
    if type(location) is str and location.isdigit() and len(location) == 5:
      if type(date) is str and date.isdigit() and (date == '0' or date == '1' or date == '2'):
        print(movie, location, date)
      else:
        print("Bad date input")
    else:
      print("Bad zipcode input")
  else:
    print("Bad movie input") 
  
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
      dataBase.extend([dict([('date', date), ('time', time), ('movieName', movieName), ('theatre', theatreName), ('driveTime', driveTime), ('theatreAddress', theatreAddress)]) for (date, time) in movieShowtimes])

  #print dataBase
  ### sort dataBase by showtime
  dataBase.sort(key=lambda x: x['time'])
  displayString = '{0:<10}  {1:<6}  {2:<30}  {3:<30}  {4:<10}  {5:<50}'
  if len(dataBase) > 0:
    print(displayString.format('DATE', 'TIME', 'MOVIE', 'THEATRE', 'DRIVE TIME', 'ADDRESS'))
    print(displayString.format('----', '----', '-----', '-------', '----------', '-------'))
    for idx, x in enumerate(dataBase):
      if (idx < 10): 
        print(displayString.format(x['date'], x['time'], x['movieName'], x['theatre'], x['driveTime'], x['theatreAddress']))


if __name__ == "__main__":
  main(sys.argv)
