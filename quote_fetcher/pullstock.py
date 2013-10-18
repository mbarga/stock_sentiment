#! /usr/bin/python

# REFERENCES:
# (1) http://sentdex.com/sentiment-analysisbig-data-and-python-tutorials/how-to-chart-stocks-and-forex-doing-your-own-financial-charting/how-to-do-your-own-financial-charting-intro/
# (2) yahoo finance API: https://code.google.com/p/yahoo-finance-managed/wiki/csvQuotesDownload
# (3) yahoo finance chart API: https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload

#TODO candlestick wick is black (cant see)
#TODO fix moving avg. offsets? 
#TODO implement multiple stocks in a loop

import urllib2
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import candlestick
#matplotlib.rcParams.update({'font.size': 9})
import pylab

stockToPull = 'GOOG'

def pullData(stock):
	try:
		urlToVisit = 'http://ichart.yahoo.com/table.csv?s='+stock+'&a=0&b=1&c=2000&d=0&e=31&f=2010&g=w&ignore=.csv'
		saveFileLine = stock+'.txt'
		
		try:
			readExistingData = open(saveFileLine,'r').read()
			splitExisting = readExistingData.split('\n')
			mostRecentLine = splitExisting(-2)
			lastTime = str(mostRecentLine.split(',')[0])
		except:
			lastTime = 'zero'
		
		sourceCode = urllib2.urlopen(urlToVisit).read()
		splitSource = sourceCode.split('\n')
	
		saveFile = open(saveFileLine,'a')
		sourceCode = urllib2.urlopen(urlToVisit).read()
		splitSource = sourceCode.split('\n')
		 
		for eachLine in splitSource:
			splitLine = eachLine.split(',')
			if len(splitLine)==7:
				# if newest time greater than last time
				#if lastTime is not 'zero':
				lineToWrite = eachLine+'\n'
				saveFile.write(lineToWrite)

		saveFile.close()

		print 'Pulled',stock
		print 'sleeping...'
		# make this longer when waiting for url to update
		time.sleep(6)

	except Exception,e:
		print 'main loop',str(e)

def rsiFunc(prices, n=14): 
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)
    for i in range(n, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

    	up = (up*(n-1)+upval)/n
    	down = (down*(n-1)+downval)/n
    	rs = up/down
    	rsi[i] = 100. - 100./(1+rs)
    return rsi

def moving_average(values, window):
	weights = np.repeat(1.0, window)/window
	smas = np.convolve(values, weights, 'valid')
	return smas

def exp_moving_average(values, window):
	weights = np.exp(np.linspace(-1., 0., window))
	weights /= weights.sum()
	a = np.convolve(values, weights, mode='full')[:len(values)]
	a[:window] = a[window]
	return a

def compMACD(x, slow=26, fast=12):
	emaslow = exp_moving_average(x, slow)
	emafast = exp_moving_average(x, fast)
	return emaslow, emafast, emafast-emaslow

def graphData(stock, MA1, MA2):
	try:
		stockFile = stock+'.txt'
		
		date, openp, highp, lowp, closep, volume, adjclp = np.loadtxt(stockFile,delimiter=',',unpack=True,converters={ 0: mdates.strpdate2num('%Y-%m-%d')})

		x = 0
		y = len(date)
		candledata = []
		while x<y:
			appendLine = date[x], openp[x], closep[x], highp[x], lowp[x], volume[x]
			candledata.append(appendLine)
			x+=1

		av1 = moving_average(closep, MA1)
		av2 = moving_average(closep, MA2)

		SP = len(date[MA2-1:])

        	rsi = rsiFunc(closep)

#colors
		rsicolor = '#00ffe8'
		spinecolor = '#5998ff'
		axisbkgd = '#07000d'

#initialize the figure
		fig = plt.figure(facecolor=axisbkgd)

#AX1 is the stock data
		ax1 = plt.subplot2grid((6,4), (1,0), rowspan=3, colspan=4, axisbg=axisbkgd)
		candlestick(ax1, candledata[-SP:], width=1, colorup='#9eff15', colordown='#ff1717')

		label1=str(MA1)+' SMA'
		label2=str(MA2)+' SMA'
		ax1.plot(date[-SP:], av1[-SP:], spinecolor, label=label1, linewidth=1)
		ax1.plot(date[-SP:], av2[-SP:], '#e1edf9', label=label2, linewidth=1)
		ax1.grid(True, color='w')
		ax1.yaxis.label.set_color('w')
		ax1.yaxis.tick_right()
		ax1.spines['bottom'].set_color(spinecolor)
		ax1.spines['top'].set_color(spinecolor)
		ax1.spines['left'].set_color(spinecolor)
		ax1.spines['right'].set_color(spinecolor)
		ax1.tick_params(axis='y', colors='w')
		plt.ylabel('Stock Price')
		plt.legend(loc=9, ncol=2, prop={'size':7}, fancybox=True)

#Setup the plot legend
		maLeg = plt.legend(loc=9, ncol=2, prop={'size':7}, fancybox=True, borderaxespad=0.)
		maLeg.get_frame().set_alpha(0.4)
		textEd = pylab.gca().get_legend().get_texts()
		pylab.setp(textEd[0:5], color='w')

#AX0 is the RSI index
		ax0 = plt.subplot2grid((6,4), (0,0), sharex=ax1, rowspan=1, colspan=4, axisbg=axisbkgd)
		
        	ax0.plot(date[-SP:], rsi[-SP:],rsicolor,linewidth=0.8)
    		ax0.axhline(70, color=spinecolor, alpha=0.5)
		ax0.axhline(30, color=spinecolor, alpha=0.5)
		ax0.fill_between(date[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), facecolor=rsicolor, edgecolor=rsicolor, alpha=0.5)
		ax0.fill_between(date[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), facecolor=rsicolor, edgecolor=rsicolor, alpha=0.5)
    		ax0.spines['bottom'].set_color(spinecolor)
		ax0.spines['top'].set_color(spinecolor)
		ax0.spines['left'].set_color(spinecolor)
		ax0.spines['right'].set_color(spinecolor)
		ax0.tick_params(axis='x', colors='w')
		ax0.tick_params(axis='y', colors='w')
		ax0.yaxis.tick_right()
		ax0.set_yticks([30,70])
		#plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='lower'))
		plt.ylabel('RSI', color='w')

#AX2 is the stock volume
		ax2 = plt.subplot2grid((6,4), (4,0), sharex=ax1, rowspan=1, colspan=4, axisbg=axisbkgd)
		
		ax2.plot(date[-SP:], volume[-SP:], rsicolor, linewidth=.8)
		volumeMin = 0	
		ax2.fill_between(date[-SP:], volumeMin, volume[-SP:], facecolor=rsicolor, alpha=0.5)
		ax2.axes.yaxis.set_ticklabels([])
		ax2.spines['bottom'].set_color(spinecolor)
		ax2.spines['top'].set_color(spinecolor)
		ax2.spines['left'].set_color(spinecolor)
		ax2.spines['right'].set_color(spinecolor)
		ax2.tick_params(axis='x', colors='w')
		ax2.tick_params(axis='y', colors='w')
		plt.ylabel('Volume', color='w')
		ax2.axes.yaxis.set_ticklabels([])

#AX3 is the MACD plot
		ax3 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4, axisbg=axisbkgd)
			
		nslow = 26
		nfast = 12
		nema = 9

		emaslow, emafast, macd = compMACD(closep)
		ema9 = exp_moving_average(macd, nema)

		ax3.plot(date[-SP:], macd[-SP:])
		ax3.plot(date[-SP:], ema9[-SP:])
		ax3.fill_between(date[-SP:], macd[-SP:]-ema9[-SP:], 0, alpha=0.5, facecolor=rsicolor, edgecolor=rsicolor)
		plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))

		ax3.spines['bottom'].set_color(spinecolor)
		ax3.spines['top'].set_color(spinecolor)
		ax3.spines['left'].set_color(spinecolor)
		ax3.spines['right'].set_color(spinecolor)
		ax3.tick_params(axis='x', colors='w')
		ax3.tick_params(axis='y', colors='w')
		ax3.xaxis.set_major_locator(mticker.MaxNLocator(10))
		ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
		ax3.axes.yaxis.set_ticklabels([])
		plt.ylabel('MACD', color='w')
		for label in ax3.xaxis.get_ticklabels():
			label.set_rotation(45)
		
		plt.xlabel('Date')
		plt.setp(ax0.get_xticklabels(), visible=False)
		plt.setp(ax1.get_xticklabels(), visible=False)
		plt.setp(ax2.get_xticklabels(), visible=False)
		plt.suptitle(stock, color='w')
		plt.show()
		#fig.savefig('example.png', facecolor=fig.get_facecolor())

	except Exception,e:
		print 'main loop',str(e)

#pullData(stockToPull)
graphData(stockToPull, 12, 26)
