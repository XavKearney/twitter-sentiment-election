# Live Twitter Sentiment Analysis for #GE2017

This repo contains all the files I created as an experiment in Twitter sentiment analysis.

The live version used to be [here](http://xavkearney.com/sentiment), but is no longer active.

On the website, the width of each party's section corresponds to the relative strength of the sentiment on Twitter. The Positive/Negative labels denote the polarity of the sentiment itself.

The sentiment analysis is carried out using machine learning classifier tool [NLTK](http://www.nltk.org/) and [VADER](https://github.com/cjhutto/vaderSentiment).

The tweets are collated live using a Twitter API stream and a predefined set of search terms designed to encompass as many of the tweets relating to the election as possible. (API credentials have been removed from the code).

The results are only based on the tweets posted in the last few seconds, hence the sometimes dramatic variation that you may see. I calculate some moving averages to smooth this out a bit, but in general it would be too boring to only update the values at a slower rate, and the idea is to get an instantaneous idea of what's going on (for TV debates etc.)

I don't correct for any biases (e.g. the overall voting preference average for Twitter, or the difference in how vocal supporters of different parties are) because there are already so many biases built into the fact that it's based on tweets. I think it provides interesting insight regardless.

Parties are sorted alphabetically. I have no affiliation to any party or campaign.

# License
Distributed under the MIT License as in the LICENSE file.
