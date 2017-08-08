#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#github:https://github.com/MRchenone/python_demo
from os import path
from wordcloud import WordCloud
d=path.dirname(__file__)
# Read the whole text.
text=open(path.join(d,'my.txt')).read()
# Generate a word cloud image
wordcloud=WordCloud().generate(text)
# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud)
plt.axis('off')
wordcloud=WordCloud(max_font_size=40).generate(text)
plt.figure()
plt.imshow(wordcloud)
plt.axis('off')
plt.show()