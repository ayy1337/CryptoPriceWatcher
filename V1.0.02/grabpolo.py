#!/usr/bin/python3
'''     
        Version: 1.0
        Author: ayy1337
        Licence: GNU GPL v3.0
'''
import sys, time, os, datetime, collections, shelve
import urllib.request
import collections
from operator import attrgetter
from operator import itemgetter
from poloapi import Poloniex

condperc = .01
mins = 5
period = mins * 60
timebetweenticks = 2 #in seconds
minutesofdatatokeep = 30

cwd = os.getcwd()
if os.name in ['posix','linux']:
	databasepath = cwd + "/db"
else:
	databasepath = cwd + "\\db"

class minute:
	def __init__(self, ticker, o, change, timestamp, volume):
		self.ticker = ticker
		self.change = float(change)
		self.average = self.open = self.high = self.low = self.close = float(o)
		self.volume = float(volume)
		self.timestamp = int(timestamp)
		self.numprices = 1

class coin:

	def __init__(self, ticker):
		self.ticker = ticker
		self.ticks = collections.deque(maxlen = int(minutesofdatatokeep/timebetweenticks))
		self.minutes = collections.deque(maxlen = (int(minutesofdatatokeep) + 1))

	def addtick(self,ticker, timestamp):
		i = ticker
		self.ticks.append(tick(self.ticker,i['last'],i['percentChange'],i['baseVolume'],timestamp))

	def addminute(self, ticker, timestamp):
		i = ticker
		self.minutes.append(minute(self.ticker,i['last'],i['percentChange'],timestamp,i['baseVolume']))

	def updateminute(self, ticker, timestamp):
		currmin = self.minutes[-1]
		if (timestamp - currmin.timestamp) > 60:
			self.addminute(ticker,timestamp)
		else:
			last = float(ticker['last'])
			currmin.close = last
			a = (currmin.average * currmin.numprices) + last
			currmin.numprices += 1
			currmin.average = a / currmin.numprices
			if last > currmin.high:
				currmin.high = last
			if last < currmin.low:
				currmin.low = last
			currmin.change = float(ticker['percentChange'])


def checkcond(coins):
	out = []
	gainers = []
	losers = []
	for key in coins:
		coin = coins[key]
		mins = coin.minutes
		tmp = []
		endtime = mins[-1].timestamp

		largestgain = 0
		largestloss = 0
		periodchange = 0
		lowvol = ""
		splt = key.split('_')
		suffix = splt[0]
		coinname = splt[1]
		if suffix != "BTC":
			continue
		if 100 < mins[-1].volume < 500:
			lowvol = 'l'
		elif mins[-1].volume <= 100:
			lowvol = 'v'
		for i in range(1,len(mins)): 
			tick = mins[-i]
			if (endtime - tick.timestamp) <= period:
				tmp.append(tick) #tmp[0] is most recent minute, tmp[-1] is oldest/least-recent minute
			else:
				break
		for i in range(1,len(tmp)+1): 
			for n in range(i+1, len(tmp)+1):
				root = tmp[-i]
				end = tmp[-n]
				changeup = (end.high - root.low) / root.low
				if changeup > largestgain:
					largestgain = changeup
				changedown = (end.low-root.high)/root.high
				if changedown < largestloss:
					largestloss = changedown
		if(len(tmp) > 0):
			periodchange = ((mins[-1].close-mins[-0].average) / mins[0].average) * 100
		else:
			continue
		if (largestgain >= condperc) or (periodchange > 2):			
			gainers.append([coinname,largestgain*100,mins[-1].close,suffix, periodchange, int(mins[-1].change * 100), lowvol])
		if ((largestloss*-1) >= condperc) or (periodchange < -2):
			losers.append([coinname, largestloss * 100, mins[-1].close, suffix, periodchange, int(mins[-1].change * 100), lowvol])

	return gainers, losers



timestamp = int(time.time())
class updater:

	def __init__(self):
		self.coins = {}
		try:
			d = shelve.open(databasepath)
			self.coins = d["polocoins"]
			d.close()
		except:
			pass
		self.polo = Poloniex()		

	def update(self):
		try:
			self.grabtickers()
		except:
			return 1
		gainers, losers = checkcond(self.coins)
		d = shelve.open(databasepath)
		d['polocoins'] = self.coins
		d.close()
		gainers = sorted(gainers, key=itemgetter(6,4))
		losers = sorted(losers, key=itemgetter(6,4))
		return gainers,losers

	def grabtickers(self):
		tickers = self.polo.returnTicker()
		timestamp = int(time.time())
		for item in tickers:
			if item not in self.coins:
				self.coins[item] = coin(item)
			if len(self.coins[item].minutes) > 0:
				self.coins[item].updateminute(tickers[item],timestamp)
			else:
				self.coins[item].addminute(tickers[item], timestamp)

	def getfav(self, ticker):
		splt = ticker.split('_')
		c = self.coins[ticker]
		mins = c.minutes
		oldprice = mins[-(min(len(mins),5))].open
		currprice = mins[-1].close
		fiveminchange = ((currprice/oldprice)-1) * 100 
		oldprice = mins[-(min(len(mins),30))].open
		thirtyminchange = ((currprice/oldprice)-1)*100
		price = currprice
		volume = mins[-1].volume
		if volume > 500:
			v = ' '
		elif volume >100:
			v = 'l'
		else:
			v = 'v'
		tfhourchange = mins[-1].change * 100
		return [splt[1]+'(p)', fiveminchange, price, thirtyminchange, tfhourchange, v]

	def getlast(self, ticker):
		return self.coins[ticker].minutes[-1].close

if __name__ == "__main__":
	updater = updater()
	while 1:
		print(updater.update())
		time.sleep(timebetweenticks)