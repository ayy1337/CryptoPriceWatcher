#!/usr/bin/python3
'''     
        Version: 1.0.01
        Author: ayy1337
        Licence: GNU GPL v3.0
'''
import sys
import time
import os
import datetime
import urllib.request
import collections
from operator import attrgetter
from operator import itemgetter
import shelve
from trexapi import Bittrex
from poloapi import Poloniex
from playsound import playsound
from gi.repository import Notify

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
	def __init__(self, ticker, o, change, timestamp, volume, prevday):
		self.ticker = ticker
		self.change = float(change)
		self.average = self.open = self.high = self.low = self.close = float(o)
		self.volume = float(volume)
		self.timestamp = int(timestamp)
		self.numprices = 1
		self.prevday = prevday

class coin:

	def __init__(self, ticker):
		self.ticker = ticker
		self.minutes = collections.deque(maxlen = (int(minutesofdatatokeep) + 1))

	def addminute(self,ticker, timestamp):
		i = ticker
		t = i['MarketName']
		try:
			price = float(i['Last'])
			prevday = float(i['PrevDay'])
			volume = float(i['BaseVolume'])
		except:
			price = 0
			prevday = 0
			volume = 0
		try:
			change = (price/prevday) -1
		except:
			change = 0
		
		self.minutes.append(minute(t,price,change,timestamp,volume, prevday)) #ticker, price, change, volume, timestamp

	def updateminute(self,ticker,timestamp):
		currmin = self.minutes[-1]
		if (timestamp - currmin.timestamp) > 60:
			self.addminute(ticker,timestamp)
		else:
			if ticker['Last'] == None:
				print("New market added: {}".format(ticker["MarketName"]))
			try:
				last = float(ticker['Last'])
			except:
				last = 0
			currmin.close = last
			a = (currmin.average * currmin.numprices) + last
			currmin.numprices += 1
			currmin.average = a / currmin.numprices
			if last > currmin.high:
				currmin.high = last
			if last < currmin.low:
				currmin.low = last
			try:
				currmin.change = (currmin.close/currmin.prevday) -1
			except:
				currmin.change = 0

timestamp = int(time.time())
class updater:

	def __init__(self):
		self.coins = {}
		Notify.init("CPW")
		try:
			d = shelve.open(databasepath)
			self.coins = d["trexcoins"]
			d.close()
		except:
			pass
		self.bittrex = Bittrex("","")
		self.polo = Poloniex()
		self.soundlastplayed = self.lastcheckstatus = int(time.time())
		self.pcstatus = None



	def update(self):
		global timestamp
		timestamp = int(time.time())

		try:
			self.coins = self.updatecoins(self.coins)			
		except:
			return 1

		gainers, losers = self.checkcond(self.coins)
		try:
			d = shelve.open(databasepath)
			d['trexcoins'] = self.coins
			d.close()
		except:
			pass
		
		gainers = sorted(gainers, key=itemgetter(6,4))
		losers = sorted(losers, key=itemgetter(6,4))
		return gainers,losers

	def updatecoins(self, coins):
		data = self.bittrex.get_market_summaries()
		if data['success'] == 1:
			tickers = data['result']
		else:
			return
		timestamp = int(time.time())
		for item in tickers:

			t = item['MarketName']

			if item['MarketName'] not in coins:
				coins[item['MarketName']] = coin(item['MarketName'])
			if len(coins[t].minutes) > 0:
				coins[t].updateminute(item,timestamp)
			else:
				coins[t].addminute(item, timestamp)
		return coins

	def checkcond(self, coins):
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
			splt = key.split('-')
			suffix = splt[0]
			coinname = splt [1]

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
					try:
						changeup = (end.high - root.low) / root.low
					except:
						changeup = 0
					if changeup > largestgain:
						largestgain = changeup

					try:
						changedown = (end.low-root.high)/root.high
					except:
						changedown = 0
					if changedown < largestloss:
						largestloss = changedown
			if(len(tmp) > 0):
				try:
					periodchange = ((mins[-1].close-mins[-0].average) / mins[0].average) * 100
				except:
					periodchange = 0
			else:
				continue

			if (largestgain >= condperc) or (periodchange > 2):			
				gainers.append([coinname,largestgain*100,mins[-1].close,suffix, periodchange, int(mins[-1].change * 100), lowvol])
			if ((largestloss*-1) >= condperc) or (periodchange < -2):
				losers.append([coinname, largestloss * 100, mins[-1].close, suffix, periodchange, int(mins[-1].change * 100), lowvol])

		return gainers, losers

	def getfav(self, ticker):
		splt = ticker.split('-')
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
		return [splt[1]+'(b)', fiveminchange, price, thirtyminchange, tfhourchange, v]

	def getlast(self, ticker):
		return self.coins[ticker].minutes[-1].close

if __name__ == "__main__":

	a = updater()
	while 1:
		a.update()
		time.sleep(2)